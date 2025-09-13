import asyncio
import logging
import os
from datetime import datetime, timedelta, timezone
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from zoneinfo import ZoneInfo
from dotenv import load_dotenv
from holidays_parser import get_holidays

offset = timedelta(hours=3)
timezone(offset, name='МСК')

load_dotenv()
API_TOKEN = os.getenv("BOT_TOKEN")

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

subscribed_chats = set()  # для рассылки

# --- Кнопки ---
def main_menu():
    markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎉 Праздник сегодня", callback_data="today")],
        [InlineKeyboardButton(text="📅 Праздник на дату", callback_data="by_date")]
    ])
    return markup

# --- Хэндлеры ---
@dp.message(Command("start"))
async def start(message: types.Message):
    subscribed_chats.add(message.chat.id)
    await message.answer("Привет! Выберите действие:", reply_markup=main_menu())

@dp.callback_query(lambda c: c.data == "today")
async def callback_today(callback: types.CallbackQuery):
    holidays = get_holidays()
    text = "🎉 Сегодня праздники:\n" + "\n".join(holidays)
    await callback.message.answer(text)

@dp.callback_query(lambda c: c.data == "by_date")
async def callback_by_date(callback: types.CallbackQuery):
    await callback.message.answer("Введите дату в формате ДД.ММ (например, 12.09):")
    dp.message.register(handle_date_input)

async def handle_date_input(message: types.Message):
    date_str = message.text.strip()
    holidays = get_holidays(date_str)
    if holidays:
        text = f"🎉 На {date_str} праздники:\n" + "\n".join(holidays)
    else:
        text = f"На {date_str} праздников не найдено."
    await message.answer(text)

# --- Ежедневная рассылка ---
async def send_daily_holiday():
    holidays = get_holidays()
    text = "🎉 Сегодня праздники:\n" + "\n".join(holidays)
    for chat_id in subscribed_chats:
        try:
            await bot.send_message(chat_id, text)
        except Exception as e:
            logging.warning(f"Не удалось отправить сообщение в чат {chat_id}: {e}")

# --- Основная функция ---
async def main():
    scheduler = AsyncIOScheduler(timezone=ZoneInfo("Europe/Moscow"))
    scheduler.add_job(send_daily_holiday, "cron", hour=7, minute=0)
    scheduler.start()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
