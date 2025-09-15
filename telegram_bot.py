import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

from analyzis_module import SalaryAnalyzer
from gigachat_service import START_MESSAGE, ANALYZE_MESSAGE

import os
from dotenv import load_dotenv, find_dotenv

# Загрузка переменных окружения
load_dotenv(find_dotenv())

# Настройка логирования
logging.basicConfig(level=logging.INFO)


BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Инициализация бота и диспетчера
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Откладываем инициализацию анализатора до первого использования
sa = None
filename = None


def get_salary_analyzer():
    """Ленивая инициализация анализатора"""
    global sa
    if sa is None:
        sa = SalaryAnalyzer(
            os.getenv("LINK_TO_STATISTIC"), START_MESSAGE, os.getenv("GIGACHAT_TOKEN")
        )
    return sa


# Создаем клавиатуру с кнопками
def get_main_keyboard():
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=[
            [
                types.KeyboardButton(text="Анализ нынешнего квартала с предыдущим"),
                types.KeyboardButton(
                    text="Анализ с этим же кварталом предыдущего года"
                ),
            ]
        ],
        resize_keyboard=True,
    )
    return keyboard


# Обработчик команды /start
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    global filename
    try:
        analyzer = get_salary_analyzer()
        filename = analyzer.DownloadFilesFromWebSite()
        await message.answer(
            "Данные загружены. Выберите тип анализа:", reply_markup=get_main_keyboard()
        )
    except Exception as e:
        logging.error(f"Ошибка при загрузке данных: {e}")
        await message.answer("Произошла ошибка при загрузке данных. Попробуйте позже.")


# Обработчик первой кнопки
@dp.message(lambda message: message.text == "Анализ нынешнего квартала с предыдущим")
async def handle_current_vs_previous_quarter(message: types.Message):
    if filename is None:
        await message.answer("Сначала загрузите данные командой /start")
        return

    await message.answer("Запускается анализ нынешнего квартала с предыдущим...")
    try:
        analyzer = get_salary_analyzer()
        message_sended = analyzer.PerformAnalysis(
            analyzer.GetData(), filename, ANALYZE_MESSAGE
        )
        ready_message = "\n".join(
            [choice.message.content for choice in message_sended.choices]
        )
        await message.answer(ready_message)
    except Exception as e:
        logging.error(f"Ошибка при анализе: {e}")
        await message.answer("Произошла ошибка при анализе данных.")


# Обработчик второй кнопки
@dp.message(
    lambda message: message.text == "Анализ с этим же кварталом предыдущего года"
)
async def handle_current_vs_previous_year_quarter(message: types.Message):
    if filename is None:
        await message.answer("Сначала загрузите данные командой /start")
        return

    await message.answer("Запускается анализ с этим же кварталом предыдущего года...")
    # Здесь можно добавить логику для второго типа анализа


# Обработчик всех остальных сообщений (игнорирует текст)
@dp.message()
async def ignore_other_messages(message: types.Message):
    await message.answer(
        "Пожалуйста, используйте кнопки для выбора действия:",
        reply_markup=get_main_keyboard(),
    )


# Основная функция
async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
