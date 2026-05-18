"""
Обработчик для просмотра и удаления собственных объявлений пользователя.
"""
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CommandHandler, CallbackQueryHandler, MessageHandler, filters

from data.data import get_user_items, get_item_by_id, delete_item

logger = logging.getLogger(__name__)


def format_my_items_list(items: list) -> str:
    text = "<b>Ваши объявления</b>\n\n"
    for item in items:
        price_formatted = f"{item['price']:,}".replace(",", " ")
        text += (
            f"<b>{item['title']}</b>\n"
            f"💰 {price_formatted} ₽  |  📍 {item.get('city', 'Не указан')}  |  🛠 {item.get('condition', 'Не указано')}\n"
            f"ID: {item['id']}\n\n"
        )
    return text


async def show_my_items(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Показать список объявлений пользователя."""
    if update.callback_query:
        query = update.callback_query
        await query.answer()
        user_id = query.from_user.id
    else:
        user_id = update.effective_user.id

    items = get_user_items(user_id)
    if not items:
        text = (
            "У вас пока нет собственных объявлений.\n\n"
            "Вы можете создать новое объявление через кнопку Продать или команду /sell."
        )
        if update.callback_query:
            await update.callback_query.edit_message_text(text=text)
        else:
            await update.message.reply_text(text)
        return

    text = format_my_items_list(items)
    keyboard = []
    for item in items:
        keyboard.append([
            InlineKeyboardButton(
                f"Посмотреть \u00AB{item['title'][:20]}\u00BB",
                callback_data=f"view_myitem_{item['id']}"
            )
        ])
    keyboard.append([
        InlineKeyboardButton("Главное меню", callback_data="main_menu")
    ])
    reply_markup = InlineKeyboardMarkup(keyboard)

    if update.callback_query:
        await update.callback_query.edit_message_text(
            text=text,
            reply_markup=reply_markup,
            parse_mode="HTML"
        )
    else:
        await update.message.reply_text(
            text=text,
            reply_markup=reply_markup,
            parse_mode="HTML"
        )


async def show_my_item_detail(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Показать одну собственную карточку товара."""
    query = update.callback_query
    await query.answer()
    item_id = int(query.data.split("_")[-1])
    item = get_item_by_id(item_id)

    if not item:
        await query.edit_message_text("Товар не найден.")
        return

    text = (
        f"<b>{item['title']}</b>\n\n"
        f"💰 Цена: {item['price']} ₽\n"
        f"📍 Город: {item.get('city', 'Не указан')}\n"
        f"🛠 Состояние: {item.get('condition', 'Не указано')}\n\n"
        f"{item['description']}\n\n"
        f"ID: {item['id']}"
    )
    keyboard = [
        [InlineKeyboardButton("Удалить объявление", callback_data=f"delete_myitem_{item_id}")],
        [InlineKeyboardButton("Назад", callback_data="back_to_my_items")],
        [InlineKeyboardButton("Главное меню", callback_data="main_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(
        text=text,
        reply_markup=reply_markup,
        parse_mode="HTML"
    )


async def delete_my_item(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Удалить объявление пользователя."""
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    item_id = int(query.data.split("_")[-1])
    item = get_item_by_id(item_id)

    if not item or item['seller_id'] != user_id:
        await query.answer("Это объявление нельзя удалить", show_alert=True)
        return

    delete_item(item_id)
    await query.answer("Объявление удалено")
    await show_my_items(update, context)


async def back_to_my_items(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Вернуться к списку собственных объявлений."""
    query = update.callback_query
    await query.answer()
    await show_my_items(update, context)


def get_handlers():
    return [
        CommandHandler("myitems", show_my_items),
        CallbackQueryHandler(show_my_item_detail, pattern=r"^view_myitem_\d+$"),
        CallbackQueryHandler(delete_my_item, pattern=r"^delete_myitem_\d+$"),
        CallbackQueryHandler(back_to_my_items, pattern=r"^back_to_my_items$"),
    ]
