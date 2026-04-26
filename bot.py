# bot.py
import os
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from aiogram.filters import Command
from aiogram.types import FSInputFile

BOT_TOKEN = os.environ.get("BOT_TOKEN")
ADMIN_IDS = [1723402881]

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

msg = """
топ
...
...
"""

@dp.message(Command("post"))
async def post_cmd(message: types.Message):
    if message.from_user.id not in ADMIN_IDS:
        await message.reply("Иди нахуй")
        return

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📝 ИНФА И ПРАВИЛА", url="https://t.me/c/1657644603/411360/603092")],
        [InlineKeyboardButton(text="🎬 ЖЕРЕБЬЁВКА", url="https://t.me/c/1657644603/411360/610175"),
         InlineKeyboardButton(text="⚙️ ТУР СЕТКА", url="https://t.me/c/1657644603/411360/615492")],
        [InlineKeyboardButton(text="✅ ПРОГНОЗЫ", url="https://site2-production-29a1.up.railway.app")]
    ])
    await message.answer(msg, parse_mode="HTML", reply_markup=keyboard)
    
async def main():
    print("✅ Бот запущен! v1.2")
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
