"""
Обработчик для показа карточек товаров.
Реализует интерфейс "как в приложении для знакомств".
"""
import logging
from pathlib import Path
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    ContextTypes,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters
)

from data.data import (
    get_available_items,
    get_item_by_id,
    add_to_favorites,
    remove_from_favorites,
    is_favorite
)

logger = logging.getLogger(__name__)


async def start_browsing(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Начало просмотра карточек товаров."""
    user_id = update.effective_user.id
    
    # Инициализируем состояние пользователя
    if "current_item_index" not in context.user_data:
        context.user_data["current_item_index"] = 0
    
    await show_item_card(update, context, user_id)


async def show_item_card(update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int) -> None:
    """Показать карточку товара."""
    items = get_available_items()
    
    if not items:
        text = "К сожалению, сейчас нет доступных объявлений.\n\nПопробуйте позже или создайте свое объявление."
        if update.callback_query:
            await update.callback_query.edit_message_text(text=text)
        else:
            await update.message.reply_text(text)
        return
    
    # Получаем текущий индекс
    current_index = context.user_data.get("current_item_index", 0)
    if current_index >= len(items):
        current_index = 0
    
    context.user_data["current_item_index"] = current_index
    item = items[current_index]
    
    # Проверяем, в избранном ли товар
    in_favorites = is_favorite(user_id, item["id"])
    
    # Формируем текст карточки
    card_text = format_item_card(item)
    
    # Создаем клавиатуру
    keyboard = [
        [
            InlineKeyboardButton("Пропустить", callback_data=f"skip_{item['id']}"),
            InlineKeyboardButton(
                "Убрать" if in_favorites else "В избранное",
                callback_data=f"fav_{item['id']}"
            ),
            InlineKeyboardButton("Связаться", callback_data=f"contact_{item['id']}")
        ],
        [
            InlineKeyboardButton("Назад", callback_data="prev_item"),
            InlineKeyboardButton("", callback_data="noop"),
            InlineKeyboardButton("Вперёд", callback_data="next_item")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    try:
        if update.callback_query:
            await update.callback_query.message.delete()
        
        # Отправляем карточку с фото или без
        photo_source = item.get("photo_url") or item.get("photo")
        if photo_source:
            photo_path = Path(photo_source)
            if not photo_path.is_absolute() and not photo_path.exists():
                photo_path = Path(__file__).resolve().parent.parent / photo_source
            if photo_path.exists():
                photo_source = str(photo_path)

            try:
                await context.bot.send_photo(
                    chat_id=user_id,
                    photo=photo_source,
                    caption=card_text,
                    parse_mode="HTML",
                    reply_markup=reply_markup
                )
            except Exception as e:
                logger.warning(f"Не удалось загрузить фото {photo_source}: {e}")
                await context.bot.send_message(
                    chat_id=user_id,
                    text=card_text,
                    parse_mode="HTML",
                    reply_markup=reply_markup
                )
        else:
            await context.bot.send_message(
                chat_id=user_id,
                text=card_text,
                parse_mode="HTML",
                reply_markup=reply_markup
            )
        
        context.user_data["current_item_id"] = item["id"]
        
    except Exception as e:
        logger.error(f"Ошибка при показе карточки: {e}")


def format_item_card(item: dict) -> str:
    """Форматирует информацию о товаре для карточки."""
    card = (
        f"<b>{item.get('title', 'Без названия')}</b>\n\n"
        f"💰 Цена: {item.get('price', 'не указана')} ₽\n"
        f"📍 Город: {item.get('city', 'Не указан')}\n"
        f"🛠 Состояние: {item.get('condition', 'Не указано')}\n\n"
        f"Описание:\n{item.get('description', 'Нет описания')}\n\n"
        f"ID: #{item.get('id', 'N/A')}"
    )
    return card


async def skip_item(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Пропустить товар (крестик)."""
    query = update.callback_query
    await query.answer("Товар пропущен")
    
    # Переходим к следующему товару
    context.user_data["current_item_index"] = context.user_data.get("current_item_index", 0) + 1
    await show_item_card(update, context, query.from_user.id)


async def toggle_favorite(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Добавить/удалить товар из избранного."""
    query = update.callback_query
    user_id = query.from_user.id
    item_id = int(query.data.split("_")[1])
    
    if is_favorite(user_id, item_id):
        remove_from_favorites(user_id, item_id)
        status = "Удалено из избранного"
    else:
        add_to_favorites(user_id, item_id)
        status = "Добавлено в избранное"
    
    await query.answer(status)


async def contact_seller(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Отправить контакт продавца."""
    query = update.callback_query
    user_id = query.from_user.id
    item_id = int(query.data.split("_")[1])
    
    item = get_item_by_id(item_id)
    if not item:
        await query.answer("Товар больше не доступен")
        return
    
    seller_username = item.get('seller_username') or '@username'
    message = (
        f"Контакты продавца:\n"
        f"{seller_username}\n\n"
        f"Напишите продавцу в Telegram, чтобы уточнить детали покупки."
    )
    await query.answer("Контакт отправлен")
    await context.bot.send_message(
        chat_id=user_id,
        text=message,
        parse_mode="HTML"
    )


async def next_item(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Перейти к следующему товару."""
    query = update.callback_query
    await query.answer()
    
    context.user_data["current_item_index"] = context.user_data.get("current_item_index", 0) + 1
    await show_item_card(update, context, query.from_user.id)


async def prev_item(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Вернуться к предыдущему товару."""
    query = update.callback_query
    await query.answer()
    
    current_index = context.user_data.get("current_item_index", 0)
    if current_index > 0:
        context.user_data["current_item_index"] = current_index - 1
    
    await show_item_card(update, context, query.from_user.id)


async def noop_button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Пустая кнопка (ничего не делает)."""
    await update.callback_query.answer()


def get_handlers():
    """Возвращает список обработчиков для просмотра карточек."""
    return [
        CommandHandler("browse", start_browsing),
        CallbackQueryHandler(skip_item, pattern=r"^skip_\d+$"),
        CallbackQueryHandler(toggle_favorite, pattern=r"^fav_\d+$"),
        CallbackQueryHandler(contact_seller, pattern=r"^contact_\d+$"),
        CallbackQueryHandler(next_item, pattern=r"^next_item$"),
        CallbackQueryHandler(prev_item, pattern=r"^prev_item$"),
        CallbackQueryHandler(noop_button, pattern=r"^noop$")
    ]
