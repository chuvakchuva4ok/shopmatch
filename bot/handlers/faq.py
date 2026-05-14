"""
Хендлеры для FAQ (часто задаваемые вопросы).
"""
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CallbackQueryHandler

from data.data import get_faq, get_faq_answer

logger = logging.getLogger(__name__)


async def show_faq(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показать меню FAQ."""
    faq_list = get_faq()
    
    if not faq_list:
        await update.message.reply_text("❓ Раздел FAQ временно недоступен.")
        return
    
    text = "❓ <b>Часто задаваемые вопросы</b>\n\nВыберите вопрос, чтобы получить ответ:"
    
    keyboard = []
    for faq in faq_list:
        keyboard.append([InlineKeyboardButton(faq["question"], callback_data=f"faq_{faq['id']}")])
    
    keyboard.append([InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        text,
        reply_markup=reply_markup,
        parse_mode="HTML"
    )


async def faq_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик нажатий на кнопки FAQ."""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    
    if data.startswith("faq_"):
        faq_id = data.split("_", 1)[1]
        answer = get_faq_answer(faq_id)
        
        if answer:
            # Находим вопрос для отображения
            faq_list = get_faq()
            question_text = next((f["question"] for f in faq_list if f["id"] == faq_id), "Вопрос")
            
            response_text = f"<b>{question_text}</b>\n\n{answer}"
            
            # Создаём клавиатуру с кнопкой назад
            keyboard = [
                [InlineKeyboardButton("← Назад к FAQ", callback_data="back_to_faq")],
                [InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                response_text,
                reply_markup=reply_markup,
                parse_mode="HTML"
            )
        else:
            await query.edit_message_text("❌ Ответ не найден.")
    
    elif data == "back_to_faq":
        await show_faq_from_callback(query, context)
    
    elif data == "main_menu":
        from handlers.main_menu import show_main_menu
        await show_main_menu(query, context)


async def show_faq_from_callback(query, context: ContextTypes.DEFAULT_TYPE):
    """Показать меню FAQ из callback запроса."""
    faq_list = get_faq()
    
    if not faq_list:
        await query.edit_message_text("❓ Раздел FAQ временно недоступен.")
        return
    
    text = "❓ <b>Часто задаваемые вопросы</b>\n\nВыберите вопрос, чтобы получить ответ:"
    
    keyboard = []
    for faq in faq_list:
        keyboard.append([InlineKeyboardButton(faq["question"], callback_data=f"faq_{faq['id']}")])
    
    keyboard.append([InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        text,
        reply_markup=reply_markup,
        parse_mode="HTML"
    )


def get_handlers():
    """Получить список хендлеров для FAQ."""
    return [
        CallbackQueryHandler(faq_callback, pattern=r"^faq_\w+"),
        CallbackQueryHandler(faq_callback, pattern=r"^back_to_faq$"),
    ]
