"""
Обработчик для добавления товаров на продажу.
"""
import logging
import re
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
    CommandHandler,
    MessageHandler,
    filters,
    CallbackQueryHandler
)

from data.data import add_item
from config import ADMIN_IDS

logger = logging.getLogger(__name__)

# Состояния конверсации
TITLE, DESCRIPTION, PRICE, CITY, CONDITION = range(5)

CONDITIONS = ["Новое", "Б/У"]

MENU_BUTTONS_REGEX = r"^(?:🛍\s*)?Покупать$|^(?:⭐\s*)?Избранное$|^(?:❓\s*)?FAQ$|^(?:[➕+]\s*)?Продать\s*$"


def is_menu_navigation(text: str) -> bool:
    return bool(text and re.match(MENU_BUTTONS_REGEX, text.strip()))


async def cancel_sell_and_route_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data.clear()
    from handlers.main_menu import menu_button_handler
    await menu_button_handler(update, context)
    return ConversationHandler.END


async def sell_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Начало процесса продажи товара."""
    user = update.effective_user
    
    await update.message.reply_text(
        "Создание объявления о продаже\n\n"
        "Давайте заполним информацию о товаре пошагово.\n\n"
        "Сначала напишите <b>название товара</b>:",
        parse_mode="HTML"
    )
    return TITLE


async def title_received(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Получение названия товара."""
    if is_menu_navigation(update.message.text):
        return await cancel_sell_and_route_menu(update, context)

    context.user_data["title"] = update.message.text
    
    await update.message.reply_text(
        "Спасибо! Теперь напишите <b>подробное описание товара</b>.\n"
        "Укажите состояние, комплектацию, какие-либо недостатки и т.д.:",
        parse_mode="HTML"
    )
    return DESCRIPTION


async def description_received(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Получение описания товара."""
    if is_menu_navigation(update.message.text):
        return await cancel_sell_and_route_menu(update, context)

    context.user_data["description"] = update.message.text
    
    await update.message.reply_text(
        "Отлично! Теперь укажите <b>цену товара</b> в рублях\n"
        "(только число, например: 5000):",
        parse_mode="HTML"
    )
    return PRICE


async def price_received(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Получение цены товара."""
    if is_menu_navigation(update.message.text):
        return await cancel_sell_and_route_menu(update, context)

    try:
        price = int(update.message.text)
        if price <= 0:
            await update.message.reply_text("Цена должна быть положительным числом!")
            return PRICE
        context.user_data["price"] = price
    except ValueError:
        await update.message.reply_text("Пожалуйста, введите корректную цену (только число)!")
        return PRICE
    
    await update.message.reply_text(
        "Спасибо! Теперь укажите <b>город</b>, где находится товар:",
        parse_mode="HTML"
    )
    return CITY


async def city_received(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Получение города."""
    if update.message.text and re.match(MENU_BUTTONS_REGEX, update.message.text.strip()):
        context.user_data.clear()
        from handlers.main_menu import menu_button_handler
        await menu_button_handler(update, context)
        return ConversationHandler.END

    context.user_data["city"] = update.message.text
    
    # Создаем клавиатуру для выбора состояния
    keyboard = [
        [InlineKeyboardButton("Новое", callback_data="condition_new")],
        [InlineKeyboardButton("Б/У", callback_data="condition_used")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "Выберите <b>состояние товара</b>:",
        parse_mode="HTML",
        reply_markup=reply_markup
    )
    return CONDITION


async def condition_selected(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Обработка выбора состояния товара."""
    query = update.callback_query
    await query.answer()
    
    condition = "Новое" if query.data == "condition_new" else "Б/У"
    context.user_data["condition"] = condition
    
    # Создаем товар сразу после выбора состояния
    user = query.from_user
    try:
        item = add_item(
            title=context.user_data["title"],
            description=context.user_data["description"],
            price=context.user_data["price"],
            city=context.user_data["city"],
            condition=context.user_data["condition"],
            seller_id=user.id,
            seller_username=f"@{user.username}" if user.username else "@username",
            photo_url=None
        )
        
        summary = (
            f"<b>Объявление успешно создано!</b>\n\n"
            f"Название: {item['title']}\n"
            f"💰 Цена: {item['price']} ₽\n"
            f"📍 Город: {item['city']}\n"
            f"🛠 Состояние: {item['condition']}\n"
            f"Описание: {item['description'][:100]}...\n\n"
            f"ID объявления: #{item['id']}\n\n"
            f"Объявление опубликовано и доступно для других пользователей."
        )
        
        await query.edit_message_text(summary, parse_mode="HTML")
        
        for admin_id in ADMIN_IDS:
            try:
                await context.bot.send_message(
                    chat_id=admin_id,
                    text=f"Новое объявление:\n\n{summary}",
                    parse_mode="HTML"
                )
            except Exception as e:
                logger.error(f"Не удалось отправить уведомление админу {admin_id}: {e}")
        
        context.user_data.clear()
        return ConversationHandler.END
    except Exception as e:
        logger.error(f"Ошибка при создании товара: {e}")
        await query.edit_message_text(
            "Произошла ошибка при создании объявления. Пожалуйста, попробуйте позже."
        )
        context.user_data.clear()
        return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Отмена процесса создания объявления."""
    await update.message.reply_text(
        "Создание объявления отменено.",
        reply_markup=ReplyKeyboardMarkup(
            [["Продать", "Покупать", "Избранное"]], 
            resize_keyboard=True
        )
    )
    context.user_data.clear()
    return ConversationHandler.END


def get_handlers():
    """Возвращает список обработчиков для продажи товаров."""
    sell_handler = ConversationHandler(
        entry_points=[
            CommandHandler("sell", sell_start),
            MessageHandler(filters.Regex(r"^(?:[➕+]\s*)?Продать\s*$"), sell_start)
        ],
        states={
            TITLE: [MessageHandler(filters.TEXT & ~filters.COMMAND, title_received)],
            DESCRIPTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, description_received)],
            PRICE: [MessageHandler(filters.TEXT & ~filters.COMMAND, price_received)],
            CITY: [MessageHandler(filters.TEXT & ~filters.COMMAND, city_received)],
            CONDITION: [CallbackQueryHandler(condition_selected)]
        },
        fallbacks=[CommandHandler("cancel", cancel), CommandHandler("sell", sell_start)],
        allow_reentry=True
    )
    
    return [sell_handler]
