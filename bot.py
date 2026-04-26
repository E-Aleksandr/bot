# bot.py
import os
import asyncio
import datetime
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from aiogram.filters import Command
from aiogram.types import FSInputFile
import libsql_experimental as libsql

BOT_TOKEN = os.environ.get("BOT_TOKEN")
ADMIN_IDS = [1723402881, 5659860044]

bot = Bot(token=BOT_TOKEN)
TURSO_DB_URL = os.environ.get("TURSO_DB_URL")
TURSO_DB_TOKEN = os.environ.get("TURSO_DB_TOKEN")

db = libsql.connect(database=TURSO_DB_URL, auth_token=TURSO_DB_TOKEN)
dp = Dispatcher()

async def get_top_players(limit=10):
    query = """
        SELECT 
            p.name,
            COUNT(CASE WHEN tp.destroyed = 1 THEN 1 END) as destroyed_count,
            COUNT(tp.id) as total_tanks,
            ROUND(CAST(COUNT(CASE WHEN tp.destroyed = 1 THEN 1 END) AS FLOAT) / COUNT(tp.id) * 100, 1) as percent
        FROM players p
        JOIN tank_progress tp ON p.id = tp.player_id
        GROUP BY p.id
        ORDER BY destroyed_count DESC, percent DESC
        LIMIT ?
    """
    
    result = await db.execute(query, [limit])
    return result.rows

async def format_top_message(limit=10):
    top_players = await get_top_players(limit)
    
    if not top_players:
        return "Пока нет данных об игроках."
    
    message = "**Результаты:**\n\n"
    
    for idx, player in enumerate(top_players, 1):
        medal = "🥇" if idx == 1 else "🥈" if idx == 2 else "🥉" if idx == 3 else f"\n{idx}."
        message += f"{medal} **{player['name']}**\n"
        message += f" - {player['destroyed_count']}/{player['total_tanks']}\n"
    
    message += f"__На момент {datetime.date} {datetime.time} по МСК__"
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

    top_text = await format_top_message(limit=10)

    await message.answer(top_text, parse_mode="Markdown", reply_markup=keyboard)
    
async def main():
    print("✅ Бот запущен! v1.2")
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
