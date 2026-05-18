"""
Хендлеры для работы с каталогом товаров.
Пагинация, просмотр карточки товара.
"""
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CallbackQueryHandler

from config import ITEMS_PER_PAGE, SELLER_CONTACT
from data.data import get_items, get_item_by_id

logger = logging.getLogger(__name__)


async def show_catalog(update: Update, context: ContextTypes.DEFAULT_TYPE, page: int = 0):
    """Показать страницу каталога товаров."""
    items = get_items()
    total_pages = (len(items) + ITEMS_PER_PAGE - 1) // ITEMS_PER_PAGE
    
    if not items:
        await update.message.reply_text(
            "Каталог пока пуст. Попробуйте позже."
        )
    
    # Получаем товары для текущей страницы
    start_idx = page * ITEMS_PER_PAGE
    end_idx = min(start_idx + ITEMS_PER_PAGE, len(items))
    page_items = items[start_idx:end_idx]
    
    # Формируем список товаров
    items_text = "<b>Каталог товаров</b>\n\n"
    for item in page_items:
        price_formatted = f"{item['price']:,}".replace(",", " ")
        status_text = "Доступен" if item["status"] == "available" else "Недоступен"
        items_text += f"<b>{item['title']}</b> — {status_text}\n"
        items_text += f"   Цена: {price_formatted} ₽\n\n"
    
    items_text += f"Страница {page + 1} из {total_pages}"
    
    # Создаём инлайн-клавиатуру с товарами и навигацией
    keyboard = []
    
    # Кнопки с товарами
    for item in page_items:
        keyboard.append([InlineKeyboardButton(item['title'], callback_data=f"view_item_{item['id']}")])
    
    # Кнопки навигации
    nav_buttons = []
    if page > 0:
        nav_buttons.append(InlineKeyboardButton("Назад", callback_data=f"catalog_page_{page - 1}"))
    if page < total_pages - 1:
        nav_buttons.append(InlineKeyboardButton("Вперёд", callback_data=f"catalog_page_{page + 1}"))
    
    if nav_buttons:
        keyboard.append(nav_buttons)
    
    # Кнопка возврата в главное меню
    keyboard.append([InlineKeyboardButton("Главное меню", callback_data="main_menu")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        items_text,
        reply_markup=reply_markup,
        parse_mode="HTML"
    )


async def catalog_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик нажатий на кнопки каталога."""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    
    if data.startswith("catalog_page_"):
        page = int(data.split("_")[-1])
        await show_catalog_from_callback(query, context, page)
    elif data.startswith("view_item_"):
        item_id = int(data.split("_")[-1])
        await show_item_card(query, context, item_id)
    elif data == "main_menu":
        from handlers.main_menu import show_main_menu
        await show_main_menu(query, context)


async def show_catalog_from_callback(query, context: ContextTypes.DEFAULT_TYPE, page: int = 0):
    """Показать страницу каталога из callback запроса."""
    items = get_items()
    total_pages = (len(items) + ITEMS_PER_PAGE - 1) // ITEMS_PER_PAGE
    
    if not items:
        await query.edit_message_text("Каталог пока пуст. Попробуйте позже.")
        return
    
    start_idx = page * ITEMS_PER_PAGE
    end_idx = min(start_idx + ITEMS_PER_PAGE, len(items))
    page_items = items[start_idx:end_idx]
    
    items_text = "<b>Каталог товаров</b>\n\n"
    for item in page_items:
        price_formatted = f"{item['price']:,}".replace(",", " ")
        status_text = "Доступен" if item["status"] == "available" else "Недоступен"
        items_text += f"<b>{item['title']}</b> — {status_text}\n"
        items_text += f"   Цена: {price_formatted} ₽\n\n"
    
    items_text += f"Страница {page + 1} из {total_pages}"
    
    keyboard = []
    for item in page_items:
        keyboard.append([InlineKeyboardButton(item['title'], callback_data=f"view_item_{item['id']}")])
    
    nav_buttons = []
    if page > 0:
        nav_buttons.append(InlineKeyboardButton("Назад", callback_data=f"catalog_page_{page - 1}"))
    if page < total_pages - 1:
        nav_buttons.append(InlineKeyboardButton("Вперёд", callback_data=f"catalog_page_{page + 1}"))
    
    if nav_buttons:
        keyboard.append(nav_buttons)
    
    keyboard.append([InlineKeyboardButton("Главное меню", callback_data="main_menu")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        items_text,
        reply_markup=reply_markup,
        parse_mode="HTML"
    )


async def show_item_card(update: Update | CallbackQueryHandler, context: ContextTypes.DEFAULT_TYPE, item_id: int):
    """Показать карточку товара."""
    # Определяем тип обновления
    if hasattr(update, 'edit_message_text'):
        # Это callback query
        query = update
        await query.answer()
        user_id = query.from_user.id
        edit_mode = True
    else:
        # Это обычное сообщение
        user_id = update.effective_user.id
        edit_mode = False
    
    item = get_item_by_id(item_id)
    if not item:
        if edit_mode:
            await query.edit_message_text("Товар не найден.")
        else:
            await update.message.reply_text("Товар не найден.")
        return
    
    # Формируем текст карточки
    status_text = "Доступен" if item["status"] == "available" else "Недоступен"
    price_formatted = f"{item['price']:,}".replace(",", " ")
    
    card_text = f"<b>{item['title']}</b>\n\n"
    card_text += f"Цена: {price_formatted} ₽\n"
    card_text += f"Статус: {status_text}\n\n"
    card_text += f"Описание:\n{item['description']}"
    
    keyboard = [
        [InlineKeyboardButton("Назад к каталогу", callback_data="back_to_catalog")],
        [InlineKeyboardButton("Главное меню", callback_data="main_menu")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Отправляем с фото если есть
    if item.get("photo"):
        photo_file = item["photo"]
        try:
            if edit_mode:
                await query.edit_message_media(
                    media={"type": "photo", "media": photo_file, "caption": card_text, "parse_mode": "HTML"},
                    reply_markup=reply_markup
                )
            else:
                await update.message.reply_photo(
                    photo=photo_file,
                    caption=card_text,
                    reply_markup=reply_markup,
                    parse_mode="HTML"
                )
        except Exception as e:
            logger.warning(f"Не удалось отправить фото: {e}")
            if edit_mode:
                await query.edit_message_text(card_text, reply_markup=reply_markup, parse_mode="HTML")
            else:
                await update.message.reply_text(card_text, reply_markup=reply_markup, parse_mode="HTML")
    else:
        if edit_mode:
            await query.edit_message_text(card_text, reply_markup=reply_markup, parse_mode="HTML")
        else:
            await update.message.reply_text(card_text, reply_markup=reply_markup, parse_mode="HTML")


async def back_to_catalog_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Вернуться к каталогу."""
    query = update.callback_query
    await query.answer()
    await show_catalog_from_callback(query, context, page=0)


def get_handlers():
    """Получить список хендлеров для каталога."""
    return [
        CallbackQueryHandler(catalog_callback, pattern=r"^catalog_page_\d+"),
        CallbackQueryHandler(catalog_callback, pattern=r"^view_item_\d+"),
        CallbackQueryHandler(back_to_catalog_callback, pattern=r"^back_to_catalog$"),
    ]
