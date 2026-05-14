"""
Хендлеры для бронирования и отмены бронирования товаров.
"""
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CallbackQueryHandler

from config import ADMIN_ID, SELLER_CONTACT
from data.data import (
    get_item_by_id, create_booking, cancel_booking,
    get_user_bookings, get_booking_item_id
)

logger = logging.getLogger(__name__)


async def reserve_item(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик бронирования товара."""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    item_id = int(query.data.split("_")[-1])
    
    item = get_item_by_id(item_id)
    if not item:
        await query.edit_message_text("❌ Товар не найден.")
        return
    
    # Пробуем создать бронь
    booking_number = create_booking(user_id, item_id)
    
    if booking_number is None:
        await query.edit_message_text(
            f"❌ Увы, товар \"{item['title']}\" уже забронирован или недоступен."
        )
        return
    
    # Формируем сообщение об успешном бронировании
    price_formatted = f"{item['price']:,}".replace(",", " ")
    success_text = (
        f"✅ <b>Товар \"{item['title']}\" забронирован!</b>\n\n"
        f"🔢 <b>Ваш номер брони:</b> #{booking_number}\n"
        f"💰 <b>Цена:</b> {price_formatted} ₽\n\n"
        f"Пожалуйста, свяжитесь с продавцом для уточнения деталей:\n"
        f"📱 {SELLER_CONTACT}\n\n"
        f"⏰ Бронь действует в течение 24 часов."
    )
    
    # Обновляем карточку товара
    keyboard = [
        [InlineKeyboardButton("❌ Отменить бронь", callback_data=f"cancel_reserve_{item_id}")],
        [InlineKeyboardButton("← Назад к каталогу", callback_data="back_to_catalog")],
        [InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        success_text,
        reply_markup=reply_markup,
        parse_mode="HTML"
    )
    
    # Уведомляем админа
    await notify_admin_new(context, user_id, item, booking_number)


async def cancel_reservation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик отмены бронирования."""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    item_id = int(query.data.split("_")[-1])
    
    item = get_item_by_id(item_id)
    if not item:
        await query.edit_message_text("❌ Товар не найден.")
        return
    
    # Проверяем, что товар забронирован этим пользователем
    if item.get("reserved_by") != user_id:
        await query.edit_message_text(
            "❌ Вы не можете отменить эту бронь, так как она оформлена другим пользователем."
        )
        return
    
    # Получаем номер брони
    bookings = get_user_bookings(user_id)
    booking_number = None
    for b in bookings:
        if b["item"] and b["item"]["id"] == item_id:
            booking_number = b["booking_number"]
            break
    
    if booking_number is None:
        # Пытаемся найти по другому методу
        await query.edit_message_text("❌ Не удалось найти активную бронь на этот товар.")
        return
    
    # Отменяем бронь
    if cancel_booking(booking_number, user_id):
        success_text = (
            f"❌ <b>Бронь отменена!</b>\n\n"
            f"Товар \"{item['title']}\" снова доступен для покупки.\n"
            f"Номер отменённой брони: #{booking_number}"
        )
        
        # Обновляем карточку товара
        keyboard = [
            [InlineKeyboardButton("🔒 Забронировать", callback_data=f"reserve_{item_id}")],
            [InlineKeyboardButton("← Назад к каталогу", callback_data="back_to_catalog")],
            [InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            success_text,
            reply_markup=reply_markup,
            parse_mode="HTML"
        )
        
        # Уведомляем админа об отмене
        await notify_admin_cancel(context, user_id, item, booking_number)
    else:
        await query.edit_message_text("❌ Не удалось отменить бронь. Попробуйте позже.")


async def notify_admin_new(context: ContextTypes.DEFAULT_TYPE, user_id: int, item: dict, booking_number: int):
    """Отправить уведомление админу о новой брони."""
    if not ADMIN_ID:
        logger.warning("ADMIN_ID не настроен, уведомление не отправлено.")
        return
    
    try:
        price_formatted = f"{item['price']:,}".replace(",", " ")
        notification_text = (
            f"🔔 <b>Новая бронь!</b>\n\n"
            f"🔢 Номер брони: #{booking_number}\n"
            f"🛍 Товар: {item['title']}\n"
            f"💰 Цена: {price_formatted} ₽\n"
            f"👤 Пользователь: {user_id}\n\n"
            f"Свяжитесь с покупателем для подтверждения сделки."
        )
        
        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=notification_text,
            parse_mode="HTML"
        )
    except Exception as e:
        logger.error(f"Ошибка при отправке уведомления админу: {e}")


async def notify_admin_cancel(context: ContextTypes.DEFAULT_TYPE, user_id: int, item: dict, booking_number: int):
    """Отправить уведомление админу об отмене брони."""
    if not ADMIN_ID:
        logger.warning("ADMIN_ID не настроен, уведомление не отправлено.")
        return
    
    try:
        notification_text = (
            f"❌ <b>Бронь отменена!</b>\n\n"
            f"🔢 Номер брони: #{booking_number}\n"
            f"🛍 Товар: {item['title']}\n"
            f"👤 Пользователь: {user_id}\n\n"
            f"Товар снова доступен для продажи."
        )
        
        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=notification_text,
            parse_mode="HTML"
        )
    except Exception as e:
        logger.error(f"Ошибка при отправке уведомления админу: {e}")


async def my_bookings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показать мои бронирования."""
    user_id = update.effective_user.id
    bookings = get_user_bookings(user_id)
    
    if not bookings:
        await update.message.reply_text(
            "📋 <b>Мои бронирования</b>\n\n"
            "У вас пока нет активных бронирований.",
            parse_mode="HTML"
        )
        return
    
    text = "📋 <b>Мои бронирования</b>\n\n"
    keyboard = []
    
    for b in bookings:
        item = b["item"]
        booking_num = b["booking_number"]
        if item:
            price_formatted = f"{item['price']:,}".replace(",", " ")
            text += f"🔢 Бронь #{booking_num}\n"
            text += f"🛍 {item['title']}\n"
            text += f"💰 {price_formatted} ₽\n\n"
            keyboard.append([InlineKeyboardButton(
                f"❌ Отменить бронь #{booking_num}",
                callback_data=f"cancel_reserve_{item['id']}"
            )])
    
    keyboard.append([InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        text,
        reply_markup=reply_markup,
        parse_mode="HTML"
    )


async def my_bookings_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показать мои бронирования из callback."""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    bookings = get_user_bookings(user_id)
    
    if not bookings:
        await query.edit_message_text(
            "📋 <b>Мои бронирования</b>\n\n"
            "У вас пока нет активных бронирований.",
            parse_mode="HTML"
        )
        return
    
    text = "📋 <b>Мои бронирования</b>\n\n"
    keyboard = []
    
    for b in bookings:
        item = b["item"]
        booking_num = b["booking_number"]
        if item:
            price_formatted = f"{item['price']:,}".replace(",", " ")
            text += f"🔢 Бронь #{booking_num}\n"
            text += f"🛍 {item['title']}\n"
            text += f"💰 {price_formatted} ₽\n\n"
            keyboard.append([InlineKeyboardButton(
                f"❌ Отменить бронь #{booking_num}",
                callback_data=f"cancel_reserve_{item['id']}"
            )])
    
    keyboard.append([InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        text,
        reply_markup=reply_markup,
        parse_mode="HTML"
    )


def get_handlers():
    """Получить список хендлеров для бронирования."""
    return [
        CallbackQueryHandler(reserve_item, pattern=r"^reserve_\d+"),
        CallbackQueryHandler(cancel_reservation, pattern=r"^cancel_reserve_\d+"),
        CallbackQueryHandler(my_bookings_callback, pattern=r"^my_bookings$"),
    ]
