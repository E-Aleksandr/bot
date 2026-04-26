# bot.py
import os
import asyncio
import datetime
import aiohttp
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from aiogram.filters import Command
from aiogram.types import FSInputFile

BOT_TOKEN = os.environ.get("BOT_TOKEN")
ADMIN_IDS = [1723402881, 5659860044]
API_BASE_URL = "https://progress-g6mm.onrender.com/g83dsh21tdsg9sa/topGet"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

async def get_top_players():
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(API_BASE_URL) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return data.get("top", [])
                else:
                    print(f"Ошибка API: {resp.status}")
                    return []
        except Exception as e:
            print(f"Ошибка запроса: {e}")
            return []

async def format_top_message():
    top_players = await get_top_players()
    
    if not top_players:
        return "Пока нет данных об игроках."
    
    message = "**Результаты:**\n\n"
    
    for idx, player in enumerate(top_players, 1):
        medal = "🥇" if idx == 1 else "🥈" if idx == 2 else "🥉" if idx == 3 else f"{idx}."
        message += f"{medal}**{player['name']}** - {player['destroyed_count']}/88\n"
    
    message += f"\n\n__На момент {datetime.strftime("%d.%m.%Y %H:%M:%S")} по МСК__"
    return message

@dp.callback_query(lambda c: c.data == "refresh_top")
async def refresh_top_callback(callback: types.CallbackQuery):
    if callback.from_user.id not in ADMIN_IDS:
        await callback.answer("❌ У вас нет прав обновлять топ", show_alert=True)
        return
    
    top_text = await format_top_message(limit=10)
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔄 Обновить топ", callback_data="refresh_top")]
    ])
    
    await callback.message.edit_text(
        top_text,
        parse_mode="Markdown",
        reply_markup=keyboard
    )
    
    await callback.answer("✅ Топ обновлён")

@dp.message(Command("post"))
async def post_cmd(message: types.Message):
    if message.from_user.id not in ADMIN_IDS:
        await message.reply("Иди нахуй")
        return

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔄 Обновить топ", callback_data="refresh_top")]
    ])

    top_text = await format_top_message()

    await message.answer(top_text, parse_mode="Markdown", reply_markup=keyboard)
    
async def main():
    print("✅ Бот запущен! v1.2")
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
