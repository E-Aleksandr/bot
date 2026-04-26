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
    now = datetime.datetime.now()
    
    if not top_players:
        return "Пока нет данных об игроках."
    
    message = "Таблица лидеров в челлендже\n‼️<b>КОЛЛЕКЦИОНЕР</b>‼️\n\n<blockquote>🏆 <b>Задроты:</b>\n\n"
    
    for idx, player in enumerate(top_players, 1):
        if idx == 1:
            medal = "🥇"
        elif idx == 2:
            medal = "🥈"
        elif idx == 3:
            medal = "🥉"
        else:
            medal = f"{idx}."
        
        message += f"{medal} {player['name']}\n"
        message += f"       {player['destroyed_count']}/88\n"
        
        if idx == 3:
            message += "</blockquote>\n"
    
    if len(top_players) < 3:
        message += "</blockquote>\n"
    
    message += f"\n\n<i>На момент {now.strftime('%d.%m.%Y %H:%M')} по МСК</i>"
    return message

@dp.callback_query(lambda c: c.data == "refresh_top")
async def refresh_top_callback(callback: types.CallbackQuery):
    if callback.from_user.id not in ADMIN_IDS:
        await callback.answer("❌ Обновлять результаты может только организатор", show_alert=True)
        return
    
    top_text = await format_top_message()
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Прогресс", url="https://t.me/c/1657644603/630188/630190")],
        [InlineKeyboardButton(text="ℹ️ Правила", url="https://t.me/c/1657644603/630188/630190"),
         InlineKeyboardButton(text="💰 Донат", url="https://t.me/B_HATYPE_KOH4EHblU")],
        [InlineKeyboardButton(text="🔄 Обновить топ", callback_data="refresh_top")]
    ])
    
    await callback.message.edit_text(top_text, parse_mode="HTML", reply_markup=keyboard)
    
    await callback.answer("✅ Топ обновлён")

@dp.message(Command("post"))
async def post_cmd(message: types.Message):
    if message.from_user.id not in ADMIN_IDS:
        return

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Прогресс", url="https://t.me/c/1657644603/630188/630190")],
        [InlineKeyboardButton(text="ℹ️ Правила", url="https://t.me/c/1657644603/630188/630190"),
         InlineKeyboardButton(text="💰 Донат", url="https://t.me/B_HATYPE_KOH4EHblU")],
        [InlineKeyboardButton(text="🔄 Обновить топ", callback_data="refresh_top")]
    ])

    top_text = await format_top_message()

    await message.answer(top_text, parse_mode="HTML", reply_markup=keyboard)
    
async def main():
    print("✅ Бот запущен! v1.2")
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
