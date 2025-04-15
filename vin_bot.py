import logging
import re
import requests
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

import os  # добавь в начало, если ещё нет

TELEGRAM_TOKEN = os.getenv("BOT_TOKEN")
if not TELEGRAM_TOKEN:
    logging.error("❌ BOT_TOKEN не установлен. Проверь переменные окружения.")
    exit(1)


# Логгирование
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

# Проверка формата VIN
def is_valid_vin(vin: str) -> bool:
    return bool(re.fullmatch(r"[A-HJ-NPR-Z0-9]{17}", vin.upper()))

# Получение данных по VIN с VIN01.ru (если получится, иначе фейковый ответ)
def get_vin_info(vin: str) -> str:
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        url = f"https://vin-01.ru/checks/{vin}"
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200 and "Информация о VIN" in response.text:
            return f"🔍 Найдена информация по VIN: {vin}\n(содержимое страницы или парсинг тут)"
        else:
            return "❌ Не удалось найти данные по этому VIN. Попробуй другой."
    except Exception as e:
        logging.error(f"Ошибка при запросе VIN: {e}")
        return "⚠️ Произошла ошибка при обращении к сервису VIN."

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет! Отправь мне VIN номер, и я постараюсь найти информацию об автомобиле 🚗"
    )

# Обработка VIN
async def handle_vin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    vin = update.message.text.strip().upper()
    
    if not is_valid_vin(vin):
        await update.message.reply_text("❗ Введи корректный VIN (17 символов, латинские буквы и цифры).")
        return
    
    await update.message.reply_text("🔎 Ищу данные по VIN... Подожди немного ⏳")
    info = get_vin_info(vin)
    await update.message.reply_text(info)

# Запуск бота
def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_vin))
    app.run_polling()

if __name__ == "__main__":
    main()