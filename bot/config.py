"""
Конфигурация бота.
Загружает переменные окружения и предоставляет доступ к настройкам.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Загружаем переменные из .env файла
load_dotenv()

# Основной путь к директории проекта
BASE_DIR = Path(__file__).parent.absolute()

# Telegram настройки
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", 0))
SELLER_CONTACT = os.getenv("SELLER_CONTACT", "@SellerName")

# Пути к файлам данных
DATA_DIR = BASE_DIR / "data"
ITEMS_FILE = DATA_DIR / "items.json"
FAQ_FILE = DATA_DIR / "faq.json"
BOOKINGS_FILE = DATA_DIR / "bookings.json"

# Настройки пагинации каталога
ITEMS_PER_PAGE = 5

# Время жизни брони в часах (опционально, для будущего расширения)
BOOKING_EXPIRY_HOURS = 24
