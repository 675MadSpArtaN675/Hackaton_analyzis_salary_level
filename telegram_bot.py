from analyzis_module import SalaryAnalyzer
from gigachat_service import START_MESSAGE, ANALYZE_MESSAGE
from dotenv import load_dotenv, find_dotenv

import asyncio, os

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from loguru import logger


load_dotenv(find_dotenv())
bot = Bot(token=os.getenv("BOT_TOKEN"))
dp = Dispatcher()

sc = SalaryAnalyzer(
    os.getenv("LINK_TO_STATISTIC"), START_MESSAGE, os.getenv("GIGACHAT_TOKEN")
)
filename = None

logger.add(
    "bot.log",
    rotation="10 MB",
    retention="10 days",
    level="INFO",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
)


def get_main_keyboard():
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=[
            [types.KeyboardButton(text="Анализ нынешнего квартала с предыдущим")],
            [types.KeyboardButton(text="Анализ с этим же кварталом предыдущего года")],
        ],
        resize_keyboard=True,
    )
    return keyboard


@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    logger.info(f"User {message.from_user.id} started the bot")
    await message.answer("Выберите тип анализа:", reply_markup=get_main_keyboard())

    global filename
    filename = sc.DownloadFilesFromWebSite()


@dp.message(lambda message: message.text == "Анализ нынешнего квартала с предыдущим")
async def handle_quarter_comparison(message: types.Message):
    logger.info(f"User {message.from_user.id} selected quarter comparison")
    await message.answer("Запускается анализ нынешнего квартала с предыдущим...")

    global filename
    message_analyz = sc.PerformAnalysis(sc.GetData(), filename, ANALYZE_MESSAGE)

    await message.answer("\n".join(map(lambda x: x.message, message_analyz.choices)))


@dp.message(
    lambda message: message.text == "Анализ с этим же кварталом предыдущего года"
)
async def handle_year_comparison(message: types.Message):
    logger.info(f"User {message.from_user.id} selected year comparison")
    await message.answer("Запускается анализ с этим же кварталом предыдущего года...")


@dp.message()
async def handle_other_messages(message: types.Message):
    logger.info(f"User {message.from_user.id} sent unexpected message: {message.text}")
    await message.answer("Пожалуйста, используйте кнопки для выбора действия.")


@dp.errors()
async def errors_handler(update, exception):
    logger.error(f"Update {update} caused error: {exception}")
    return True


async def main():
    logger.info("Starting bot...")
    try:
        await dp.start_polling(bot)
    except Exception as e:
        logger.error(f"Bot stopped with error: {e}")
    finally:
        logger.info("Bot stopped")
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
