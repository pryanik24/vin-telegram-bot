import logging
import re
import requests
import os
from bs4 import BeautifulSoup
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# Получаем токен из переменных окружения
TELEGRAM_TOKEN = os.getenv("BOT_TOKEN")

# Логгирование
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

# Проверка VIN
def is_valid_vin(vin: str) -> bool:
    return bool(re.fullmatch(r"[A-HJ-NPR-Z0-9]{17}", vin.upper()))

# Парсинг данных с сайта vin-01.ru
def get_vin_info(vin: str) -> str:
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        url = f"https://vin-01.ru/checks/{vin}"
        response = requests.get(url, headers=headers, timeout=10)

        if response.status_code != 200:
            return "⚠️ Не удалось получить доступ к vin-01.ru."

        soup = BeautifulSoup(response.text, "html.parser")

        if "не найден" in soup.text.lower():
            return "❌ По этому VIN ничего не найдено."

        title = soup.find("h1").text.strip()

        # Сборка текста из блоков с результатами
        result_blocks = soup.select(".block-result")
        result_text = "\n\n".join(
            block.get_text(separator="\n", strip=True) for block in result_blocks
        )

        return f"🔍 Отчет по VIN: {vin}\n\n{title}\n\n{result_text}"

    except Exception as e:
        logging.error(f"Ошибка при парсинге: {e}")
        return "⚠️ Произошла ошибка при обработке VIN. Попробуй позже."

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет! Отправь мне VIN номер (17 символов), и я найду информацию об авто 🚗"
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
