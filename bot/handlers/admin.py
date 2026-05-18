"""
Административные хендлеры для управления товарами.
Доступно только пользователю с ADMIN_ID.
"""
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ContextTypes, CommandHandler, ConversationHandler,
    MessageHandler, filters, CallbackQueryHandler
)

from config import ADMIN_IDS
from data.data import get_items, add_item, delete_item
import json

logger = logging.getLogger(__name__)

# Состояния для ConversationHandler
ADD_TITLE, ADD_DESCRIPTION, ADD_PRICE, ADD_PHOTO = range(4)


def is_admin(user_id: int) -> bool:
    """Проверить, является ли пользователь админом."""
    return user_id in ADMIN_IDS


async def admin_check(func):
    """Декоратор для проверки прав администратора."""
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        if not is_admin(update.effective_user.id):
            await update.message.reply_text("❌ У вас нет доступа к этой команде.")
            return
        return await func(update, context, *args, **kwargs)
    return wrapper


async def cmd_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Вывести список всех товаров с ID."""
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("❌ У вас нет доступа к этой команде.")
        return
    
    items = get_items()
    
    if not items:
        await update.message.reply_text("📋 Список товаров пуст.")
        return
    
    text = "📋 <b>Все товары</b>\n\n"
    for item in items:
        status_emoji = "✅" if item["status"] == "available" else "🔒"
        price_formatted = f"{item['price']:,}".replace(",", " ")
        text += f"<b>ID:</b> {item['id']} | {status_emoji} {item['title']} — {price_formatted} ₽\n"
    
    await update.message.reply_text(text, parse_mode="HTML")


async def cmd_add_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Начать добавление товара."""
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("❌ У вас нет доступа к этой команде.")
        return ConversationHandler.END
    
    await update.message.reply_text(
        "➕ <b>Добавление товара</b>\n\n"
        "Введите название товара:",
        parse_mode="HTML"
    )
    return ADD_TITLE


async def add_title_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик названия товара."""
    context.user_data['add_title'] = update.message.text.strip()
    
    await update.message.reply_text(
        "Отлично! Теперь введите описание товара:"
    )
    return ADD_DESCRIPTION


async def add_description_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик описания товара."""
    context.user_data['add_description'] = update.message.text.strip()
    
    await update.message.reply_text(
        "Теперь введите цену товара (только число, в рублях):"
    )
    return ADD_PRICE


async def add_price_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик цены товара."""
    try:
        price = int(update.message.text.strip())
        if price <= 0:
            raise ValueError("Цена должна быть положительной")
        context.user_data['add_price'] = price
        
        await update.message.reply_text(
            "Отправьте фото товара (или напишите 'пропустить' чтобы продолжить без фото):"
        )
        return ADD_PHOTO
    except ValueError:
        await update.message.reply_text(
            "❌ Неверный формат цены. Введите целое положительное число:"
        )
        return ADD_PRICE


async def add_photo_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик фото товара."""
    photo_file_id = None
    
    if update.message.photo:
        # Берём фото наилучшего качества
        photo_file_id = update.message.photo[-1].file_id
    elif update.message.text and update.message.text.lower() == "пропустить":
        photo_file_id = None
    else:
        await update.message.reply_text(
            "Пожалуйста, отправьте фото или напишите 'пропустить':"
        )
        return ADD_PHOTO
    
    # Создаём товар
    title = context.user_data.get('add_title', 'Без названия')
    description = context.user_data.get('add_description', '')
    price = context.user_data.get('add_price', 0)
    
    new_item = add_item(
        title=title,
        description=description,
        price=price,
        city="Не указан",
        condition="Не указан",
        seller_id=update.effective_user.id,
        seller_username=f"@{update.effective_user.username}" if update.effective_user.username else "@username",
        photo_url=photo_file_id
    )
    
    await update.message.reply_text(
        f"✅ <b>Товар добавлен!</b>\n\n"
        f"<b>ID:</b> {new_item['id']}\n"
        f"<b>Название:</b> {title}\n"
        f"<b>Описание:</b> {description}\n"
        f"<b>Цена:</b> {price} ₽\n"
        f"<b>Город:</b> {new_item['city']}\n"
        f"<b>Состояние:</b> {new_item['condition']}\n"
        f"<b>Фото:</b> {'✅' if photo_file_id else '❌'}",
        parse_mode="HTML"
    )
    
    # Очищаем данные
    context.user_data.clear()
    
    return ConversationHandler.END


async def cmd_delete(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Удалить товар по ID."""
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("❌ У вас нет доступа к этой команде.")
        return
    
    if not context.args:
        await update.message.reply_text(
            "❌ Укажите ID товара для удаления.\n"
            "Пример: /delete 5"
        )
        return
    
    try:
        item_id = int(context.args[0])
    except ValueError:
        await update.message.reply_text("❌ ID должен быть числом.")
        return
    
    if delete_item(item_id):
        await update.message.reply_text(f"✅ Товар с ID {item_id} удалён.")
    else:
        await update.message.reply_text(f"❌ Товар с ID {item_id} не найден.")


async def cmd_export(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Экспортировать товары в JSON файл и отправить админу."""
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("❌ У вас нет доступа к этой команде.")
        return
    
    items = get_items()
    
    # Формируем JSON строку
    json_str = json.dumps({"items": items}, ensure_ascii=False, indent=2)
    
    # Отправляем файлом
    from io import BytesIO
    file_bytes = BytesIO(json_str.encode('utf-8'))
    file_bytes.name = "items.json"
    
    await update.message.reply_document(
        document=file_bytes,
        filename="items.json",
        caption="📦 Экспорт товаров завершён!"
    )


async def cancel_conversation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Отменить диалог добавления товара."""
    context.user_data.clear()
    await update.message.reply_text("❌ Добавление товара отменено.")
    return ConversationHandler.END


def get_handlers():
    """Получить список хендлеров для админки."""
    # ConversationHandler для добавления товара
    add_conv_handler = ConversationHandler(
        entry_points=[CommandHandler("add", cmd_add_start)],
        states={
            ADD_TITLE: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_title_handler)],
            ADD_DESCRIPTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_description_handler)],
            ADD_PRICE: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_price_handler)],
            ADD_PHOTO: [
                MessageHandler(filters.PHOTO, add_photo_handler),
                MessageHandler(filters.TEXT & ~filters.COMMAND, add_photo_handler)
            ]
        },
        fallbacks=[CommandHandler("cancel", cancel_conversation)],
        allow_reentry=False,
        per_message=True
    )
    
    return [
        add_conv_handler,
        CommandHandler("list", cmd_list),
        CommandHandler("delete", cmd_delete),
        CommandHandler("export", cmd_export),
    ]
