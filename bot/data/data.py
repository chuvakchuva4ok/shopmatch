"""
Модуль для работы с данными (товары, FAQ, бронирования).
Все данные хранятся в JSON-файлах.
"""
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, List

from config import ITEMS_FILE, FAQ_FILE, BOOKINGS_FILE, DATA_DIR

logger = logging.getLogger(__name__)


def ensure_data_dir():
    """Убедиться, что директория данных существует."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def load_json(filepath: Path, default: Any = None) -> Any:
    """Загрузить данные из JSON файла."""
    if default is None:
        default = {}
    try:
        if filepath.exists():
            with open(filepath, "r", encoding="utf-8") as f:
                return json.load(f)
        else:
            # Создаём файл с дефолтными данными
            save_json(filepath, default)
            return default
    except json.JSONDecodeError as e:
        logger.error(f"Ошибка чтения JSON из {filepath}: {e}")
        return default
    except Exception as e:
        logger.error(f"Неожиданная ошибка при чтении {filepath}: {e}")
        return default


def save_json(filepath: Path, data: Any) -> None:
    """Сохранить данные в JSON файл."""
    ensure_data_dir()
    try:
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"Ошибка записи JSON в {filepath}: {e}")
        raise


# ==================== ТОВАРЫ ====================

def get_default_items() -> Dict[str, Any]:
    """Возвращает структуру товаров по умолчанию с примерами."""
    return {
        "items": [
            {
                "id": 1,
                "title": "Наушники Sony WH-1000XM4",
                "description": "Беспроводные наушники с шумоподавлением. Отличное звучание, до 30 часов работы.",
                "price": 25000,
                "photo": None,
                "status": "available",
                "reserved_by": None,
                "reserved_at": None
            },
            {
                "id": 2,
                "title": "iPhone 13 Pro 128GB",
                "description": "Смартфон в отличном состоянии. Цвет: графит. Комплект: коробка, кабель.",
                "price": 75000,
                "photo": None,
                "status": "available",
                "reserved_by": None,
                "reserved_at": None
            },
            {
                "id": 3,
                "title": "MacBook Air M1",
                "description": "Ноутбук Apple MacBook Air на чипе M1. 8GB RAM, 256GB SSD. Серебристый.",
                "price": 85000,
                "photo": None,
                "status": "available",
                "reserved_by": None,
                "reserved_at": None
            },
            {
                "id": 4,
                "title": "Apple Watch Series 7",
                "description": "Умные часы 45mm. GPS + Cellular. Ремешок в комплекте.",
                "price": 35000,
                "photo": None,
                "status": "available",
                "reserved_by": None,
                "reserved_at": None
            },
            {
                "id": 5,
                "title": "iPad Air 5th Gen",
                "description": "Планшет 64GB Wi-Fi. Цвет: голубой. Идеальное состояние.",
                "price": 55000,
                "photo": None,
                "status": "available",
                "reserved_by": None,
                "reserved_at": None
            },
            {
                "id": 6,
                "title": "Sony PlayStation 5",
                "description": "Игровая консоль с дисководом. Два контроллера DualSense в комплекте.",
                "price": 50000,
                "photo": None,
                "status": "available",
                "reserved_by": None,
                "reserved_at": None
            },
            {
                "id": 7,
                "title": "Canon EOS R6",
                "description": "Беззеркальная камера. Полный кадр. В комплекте объектив 24-105mm.",
                "price": 180000,
                "photo": None,
                "status": "available",
                "reserved_by": None,
                "reserved_at": None
            },
            {
                "id": 8,
                "title": "Dyson V15 Detect",
                "description": "Беспроводной пылесос с лазерной подсветкой. Все насадки в комплекте.",
                "price": 65000,
                "photo": None,
                "status": "available",
                "reserved_by": None,
                "reserved_at": None
            },
            {
                "id": 9,
                "title": "Bose SoundLink Revolve+",
                "description": "Портативная Bluetooth-колонка. 360° звук, до 16 часов работы.",
                "price": 18000,
                "photo": None,
                "status": "available",
                "reserved_by": None,
                "reserved_at": None
            },
            {
                "id": 10,
                "title": "GoPro Hero 11 Black",
                "description": "Экшн-камера с 5K видео. Водонепроницаемая до 10м. Крепления в комплекте.",
                "price": 42000,
                "photo": None,
                "status": "available",
                "reserved_by": None,
                "reserved_at": None
            },
            {
                "id": 11,
                "title": "Kindle Paperwhite",
                "description": "Электронная книга 8GB. Подсветка, защита от воды. Черный цвет.",
                "price": 14000,
                "photo": None,
                "status": "available",
                "reserved_by": None,
                "reserved_at": None
            },
            {
                "id": 12,
                "title": "Logitech MX Master 3S",
                "description": "Беспроводная мышь для продуктивной работы. Тихие клики, эргономика.",
                "price": 9000,
                "photo": None,
                "status": "available",
                "reserved_by": None,
                "reserved_at": None
            },
            {
                "id": 13,
                "title": "Keychron K2 Mechanical",
                "description": "Механическая клавиатура 75%. Hot-swap, RGB подсветка. Switches: Gateron Brown.",
                "price": 12000,
                "photo": None,
                "status": "available",
                "reserved_by": None,
                "reserved_at": None
            },
            {
                "id": 14,
                "title": "Samsung Odyssey G7",
                "description": "Игровой монитор 27\" 240Hz 1ms. Изогнутый VA-экран, QHD разрешение.",
                "price": 55000,
                "photo": None,
                "status": "available",
                "reserved_by": None,
                "reserved_at": None
            },
            {
                "id": 15,
                "title": "AirPods Pro 2nd Gen",
                "description": "Беспроводные наушники с активным шумоподавлением. Магсейф кейс.",
                "price": 22000,
                "photo": None,
                "status": "available",
                "reserved_by": None,
                "reserved_at": None
            }
        ]
    }


def get_items() -> List[Dict[str, Any]]:
    """Получить список всех товаров."""
    data = load_json(ITEMS_FILE, get_default_items())
    return data.get("items", [])


def get_item_by_id(item_id: int) -> Optional[Dict[str, Any]]:
    """Получить товар по ID."""
    items = get_items()
    for item in items:
        if item["id"] == item_id:
            return item
    return None


def save_items(items: List[Dict[str, Any]]) -> None:
    """Сохранить список товаров."""
    save_json(ITEMS_FILE, {"items": items})


def add_item(title: str, description: str, price: int, photo: Optional[str] = None) -> Dict[str, Any]:
    """Добавить новый товар."""
    items = get_items()
    # Генерируем новый ID
    new_id = max((item["id"] for item in items), default=0) + 1
    new_item = {
        "id": new_id,
        "title": title,
        "description": description,
        "price": price,
        "photo": photo,
        "status": "available",
        "reserved_by": None,
        "reserved_at": None
    }
    items.append(new_item)
    save_items(items)
    return new_item


def delete_item(item_id: int) -> bool:
    """Удалить товар по ID."""
    items = get_items()
    original_len = len(items)
    items = [item for item in items if item["id"] != item_id]
    if len(items) < original_len:
        save_items(items)
        return True
    return False


def search_items(query: str) -> List[Dict[str, Any]]:
    """Поиск товаров по названию и описанию."""
    query_lower = query.lower()
    items = get_items()
    results = []
    for item in items:
        if query_lower in item["title"].lower() or query_lower in item["description"].lower():
            results.append(item)
    return results


# ==================== FAQ ====================

def get_default_faq() -> Dict[str, Any]:
    """Возвращает структуру FAQ по умолчанию."""
    return {
        "questions": [
            {
                "id": "delivery",
                "question": "🚚 Доставка",
                "answer": "Доставка осуществляется по всей России через СДЭК, Почту России или курьером.\n\n📦 Стоимость доставки рассчитывается индивидуально.\n⏱ Срок доставки: 2-7 дней в зависимости от региона.\n\nВозможна самовывоз из Москвы (метро Октябрьская)."
            },
            {
                "id": "payment",
                "question": "💳 Оплата",
                "answer": "Принимаются следующие способы оплаты:\n\n• Наличные при встрече\n• Перевод на карту (Сбербанк, Тинькофф)\n• Безналичный расчёт (для юрлиц)\n\nПредоплата 50% для бронирования товара."
            },
            {
                "id": "return",
                "question": "↩️ Возврат",
                "answer": "Возврат товара возможен в течение 14 дней при сохранении товарного вида и упаковки.\n\n⚠️ Товары надлежащего качества, бывшие в употреблении, возврату не подлежат.\n\nПри обнаружении брака — полный возврат средств или обмен."
            },
            {
                "id": "contacts",
                "question": "📞 Контакты",
                "answer": "Связаться со мной можно:\n\n📱 Telegram: @SellerName\n📧 Email: seller@example.com\n🕒 Время связи: 9:00 - 21:00 (МСК)\n\nОтвечаю обычно в течение часа!"
            },
            {
                "id": "warranty",
                "question": "🛡 Гарантия",
                "answer": "На все товары предоставляется гарантия:\n\n• Техника Apple — 1 год\n• Электроника — 6 месяцев\n• Аксессуары — 14 дней\n\nГарантийный случай — бесплатный ремонт или замена."
            }
        ]
    }


def get_faq() -> List[Dict[str, Any]]:
    """Получить список вопросов FAQ."""
    data = load_json(FAQ_FILE, get_default_faq())
    return data.get("questions", [])


def get_faq_answer(faq_id: str) -> Optional[str]:
    """Получить ответ на вопрос по ID."""
    faq_list = get_faq()
    for faq in faq_list:
        if faq["id"] == faq_id:
            return faq["answer"]
    return None


# ==================== БРОНИРОВАНИЯ ====================

def get_default_bookings() -> Dict[str, Any]:
    """Возвращает структуру бронирований по умолчанию."""
    return {"bookings": {}}


def get_bookings() -> Dict[str, Any]:
    """Получить все бронирования."""
    return load_json(BOOKINGS_FILE, get_default_bookings())


def save_bookings(bookings: Dict[str, Any]) -> None:
    """Сохранить бронирования."""
    save_json(BOOKINGS_FILE, bookings)


def create_booking(user_id: int, item_id: int) -> Optional[int]:
    """
    Создать бронирование товара.
    Возвращает номер брони или None если товар недоступен.
    """
    item = get_item_by_id(item_id)
    if not item or item["status"] != "available":
        return None

    bookings_data = get_bookings()
    # Генерируем уникальный номер брони
    booking_number = max((int(b) for b in bookings_data.get("bookings", {}).keys()), default=0) + 1
    
    booking_info = {
        "user_id": user_id,
        "item_id": item_id,
        "created_at": datetime.now().isoformat(),
        "status": "active"
    }
    
    bookings_data["bookings"][str(booking_number)] = booking_info
    save_bookings(bookings_data)

    # Обновляем статус товара
    items = get_items()
    for i, it in enumerate(items):
        if it["id"] == item_id:
            items[i]["status"] = "reserved"
            items[i]["reserved_by"] = user_id
            items[i]["reserved_at"] = datetime.now().isoformat()
            break
    save_items(items)

    return booking_number


def cancel_booking(booking_number: int, user_id: int) -> bool:
    """
    Отменить бронирование.
    Проверяет, что пользователь является владельцем брони.
    """
    bookings_data = get_bookings()
    bookings = bookings_data.get("bookings", {})
    
    if str(booking_number) not in bookings:
        return False
    
    booking = bookings[str(booking_number)]
    if booking["user_id"] != user_id or booking["status"] != "active":
        return False

    # Отменяем бронь
    booking["status"] = "cancelled"
    save_bookings(bookings_data)

    # Освобождаем товар
    items = get_items()
    for i, item in enumerate(items):
        if item["id"] == booking["item_id"]:
            items[i]["status"] = "available"
            items[i]["reserved_by"] = None
            items[i]["reserved_at"] = None
            break
    save_items(items)

    return True


def get_user_bookings(user_id: int) -> List[Dict[str, Any]]:
    """Получить все активные бронирования пользователя."""
    bookings_data = get_bookings()
    bookings = bookings_data.get("bookings", {})
    items = get_items()
    
    user_bookings = []
    for booking_num, booking in bookings.items():
        if booking["user_id"] == user_id and booking["status"] == "active":
            item = next((it for it in items if it["id"] == booking["item_id"]), None)
            user_bookings.append({
                "booking_number": int(booking_num),
                "booking": booking,
                "item": item
            })
    
    return user_bookings


def get_booking_item_id(booking_number: int) -> Optional[int]:
    """Получить ID товара по номеру брони."""
    bookings_data = get_bookings()
    booking = bookings_data.get("bookings", {}).get(str(booking_number))
    if booking:
        return booking["item_id"]
    return None
