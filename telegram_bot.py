import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

from analyzis_module import SalaryAnalyzer
from gigachat_service import START_MESSAGE, ANALYZE_MESSAGE

import os

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Токен вашего бота (замените на свой)


# Инициализация бота и диспетчера
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
sa = SalaryAnalyzer(
    os.getenv("LINK_TO_STATISTIC"), START_MESSAGE, os.getenv("GIGACHAT_TOKEN")
)
filename = None


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
    filename = sa.DownloadFilesFromWebSite()
    await message.answer("Выберите тип анализа:", reply_markup=get_main_keyboard())


# Обработчик первой кнопки
@dp.message(lambda message: message.text == "Анализ нынешнего квартала с предыдущим")
async def handle_current_vs_previous_quarter(message: types.Message):
    # Здесь будет ваша логика для первого анализа
    await message.answer("Запускается анализ нынешнего квартала с предыдущим...")
    message_sended = sa.PerformAnalysis(sa.GetData(), filename, ANALYZE_MESSAGE)
    ready_message = "\n".join(map(lambda x: x.message, message_sended.choices))

    await message.answer(ready_message)


# Обработчик второй кнопки
@dp.message(
    lambda message: message.text == "Анализ с этим же кварталом предыдущего года"
)
async def handle_current_vs_previous_year_quarter(message: types.Message):
    # Здесь будет ваша логика для второго анализа
    await message.answer("Запускается анализ с этим же кварталом предыдущего года...")


# Обработчик всех остальных сообщений (игнорирует текст)
@dp.message()
async def ignore_other_messages(message: types.Message):
    # Просто игнорируем текстовые сообщения, но показываем клавиатуру
    await message.answer(
        "Пожалуйста, используйте кнопки для выбора действия:",
        reply_markup=get_main_keyboard(),
    )


# Основная функция
async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
