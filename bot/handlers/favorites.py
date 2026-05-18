"""
Обработчик для просмотра избранных товаров.
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
    get_user_favorites,
    remove_from_favorites,
    get_item_by_id
)

logger = logging.getLogger(__name__)


async def show_favorites(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Показать избранные товары."""
    user_id = update.effective_user.id
    favorites = get_user_favorites(user_id)
    
    if not favorites:
        text = "В избранном пока нет товаров.\n\nПосмотрите каталог и добавьте интересующие вас товары."
        if update.callback_query:
            await update.callback_query.edit_message_text(text=text)
        else:
            await update.message.reply_text(text)
        return
    
    # Инициализируем индекс
    if "fav_index" not in context.user_data:
        context.user_data["fav_index"] = 0
    
    await show_favorite_card(update, context, user_id, favorites)


async def show_favorite_card(update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int, favorites: list) -> None:
    """Показать одну карточку из избранного."""
    if not favorites:
        text = "В избранном пока нет товаров."
        if update.callback_query:
            await update.callback_query.edit_message_text(text=text)
        else:
            await update.message.reply_text(text)
        return
    
    current_index = context.user_data.get("fav_index", 0)
    if current_index >= len(favorites):
        current_index = 0
        context.user_data["fav_index"] = 0
    
    item = favorites[current_index]
    
    # Формируем текст карточки
    card_text = format_favorite_card(item, current_index + 1, len(favorites))
    
    # Создаем клавиатуру
    keyboard = [
        [
            InlineKeyboardButton("Удалить", callback_data=f"remove_fav_{item['id']}"),
            InlineKeyboardButton("Связаться", callback_data=f"contact_fav_{item['id']}")
        ],
        [
            InlineKeyboardButton("Назад", callback_data="prev_fav"),
            InlineKeyboardButton(f"{current_index + 1}/{len(favorites)}", callback_data="noop_fav"),
            InlineKeyboardButton("Вперёд", callback_data="next_fav")
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
                logger.warning(f"Не удалось загрузить фото: {e}")
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
        
        context.user_data["current_fav_id"] = item["id"]
        
    except Exception as e:
        logger.error(f"Ошибка при показе избранного: {e}")


def format_favorite_card(item: dict, current: int, total: int) -> str:
    """Форматирует информацию о товаре из избранного."""
    card = (
        f"<b>{item.get('title', 'Без названия')}</b>\n\n"
        f"💰 Цена: {item.get('price', 'не указана')} ₽\n"
        f"📍 Город: {item.get('city', 'Не указан')}\n"
        f"🛠 Состояние: {item.get('condition', 'Не указано')}\n\n"
        f"Описание:\n{item.get('description', 'Нет описания')}\n\n"
        f"<i>Товар {current} из {total} в избранном</i>"
    )
    return card


async def remove_from_fav(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Удалить товар из избранного."""
    query = update.callback_query
    user_id = query.from_user.id
    parts = query.data.split("_")
    if len(parts) < 3 or not parts[-1].isdigit():
        await query.answer("Неверные данные действия", show_alert=True)
        return
    item_id = int(parts[-1])
    
    remove_from_favorites(user_id, item_id)
    await query.answer("Удалено из избранного")
    
    # Показываем следующий товар
    favorites = get_user_favorites(user_id)
    if favorites:
        await show_favorite_card(update, context, user_id, favorites)
    else:
        await query.edit_message_text(
            text="В избранном пока нет товаров."
        )


async def contact_from_fav(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Отправить контакт продавца из избранного."""
    query = update.callback_query
    user_id = query.from_user.id
    parts = query.data.split("_")
    if len(parts) < 3 or not parts[-1].isdigit():
        await query.answer("Неверные данные действия", show_alert=True)
        return
    item_id = int(parts[-1])
    
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


async def next_favorite(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Перейти к следующему избранному товару."""
    query = update.callback_query
    await query.answer()
    
    context.user_data["fav_index"] = context.user_data.get("fav_index", 0) + 1
    favorites = get_user_favorites(query.from_user.id)
    await show_favorite_card(update, context, query.from_user.id, favorites)


async def prev_favorite(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Вернуться к предыдущему избранному товару."""
    query = update.callback_query
    await query.answer()
    
    fav_index = context.user_data.get("fav_index", 0)
    if fav_index > 0:
        context.user_data["fav_index"] = fav_index - 1
    
    favorites = get_user_favorites(query.from_user.id)
    await show_favorite_card(update, context, query.from_user.id, favorites)


async def noop_fav_button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Пустая кнопка (ничего не делает)."""
    await update.callback_query.answer()


def get_handlers():
    """Возвращает список обработчиков для избранного."""
    return [
        CommandHandler("favorites", show_favorites),
        CallbackQueryHandler(remove_from_fav, pattern=r"^remove_fav_\d+$"),
        CallbackQueryHandler(contact_from_fav, pattern=r"^contact_fav_\d+$"),
        CallbackQueryHandler(next_favorite, pattern=r"^next_fav$"),
        CallbackQueryHandler(prev_favorite, pattern=r"^prev_fav$"),
        CallbackQueryHandler(noop_fav_button, pattern=r"^noop_fav$")
    ]
