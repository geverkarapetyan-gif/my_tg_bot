import asyncio
import sqlite3
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command

# --- НАСТРОЙКИ ---
TOKEN = "8547694322:AAGUYRkPIWDpY5kHDK5YKDHVQjbekGdlEpk"
CHANNEL_ID = -1002252094748
MY_PERSONAL_ID = 5873150269  # Твой цифровой ID
MY_USERNAME = "@desingdyadya" # Твой юзернейм для связи
PORTFOLIO_URL = "https://drive.google.com/drive/u/0/folders/1B6zCjho6g-QpcvFNVxmgSibjLkYUcT3-"

bot = Bot(token=TOKEN)
dp = Dispatcher()

# --- РАБОТА С БАЗОЙ ДАННЫХ ---
def init_db():
    conn = sqlite3.connect("referrals.db")
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            invite_count INTEGER DEFAULT 0
        )
    """)
    conn.commit()
    conn.close()

# --- ГЛАВНОЕ МЕНЮ ---
def get_main_keyboard():
    kb = [
        [types.KeyboardButton(text="🔗 Получить ссылку")],
        [types.KeyboardButton(text="🎨 Купить аву"), types.KeyboardButton(text="📁 Портфолио")]
    ]
    return types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

# --- ОБРАБОТЧИКИ ---

@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer(
        f"Привет, {message.from_user.first_name}! Я бот канала Divine Design.\n"
        "Выбирай нужное действие в меню ниже:",
        reply_markup=get_main_keyboard()
    )

@dp.message(F.text == "🔗 Получить ссылку")
async def create_ref(message: types.Message):
    link = await bot.create_chat_invite_link(
        chat_id=CHANNEL_ID,
        name=f"ref_{message.from_user.id}"
    )
    await message.answer(f"Твоя персональная ссылка:\n{link.invite_link}\n\nПригласи 5 друзей и получишь контакт дизайнера!")

@dp.message(F.text == "📁 Портфолио")
async def show_portfolio(message: types.Message):
    await message.answer(f"Мои работы можно посмотреть здесь:\n{PORTFOLIO_URL}")

@dp.message(F.text == "🎨 Купить аву")
async def buy_ava(message: types.Message):
    price_text = (
        "🔥 Цены на аватарки:\n\n"
        "✅ Норм ава — 200 руб.\n"
        "🚀 Хорошая ава — 500 руб.\n\n"
        f"Для заказа пиши мне: {MY_USERNAME}"
    )
    await message.answer(price_text)

@dp.chat_member()
async def on_chat_member(update: types.ChatMemberUpdated):
    if update.new_chat_member.status == "member":
        if update.invite_link and update.invite_link.name:
            if update.invite_link.name.startswith("ref_"):
                inviter_id = int(update.invite_link.name.replace("ref_", ""))
                
                conn = sqlite3.connect("referrals.db")
                cur = conn.cursor()
                cur.execute("INSERT OR IGNORE INTO users (user_id) VALUES (?)", (inviter_id,))
                cur.execute("UPDATE users SET invite_count = invite_count + 1 WHERE user_id = ?", (inviter_id,))
                cur.execute("SELECT invite_count FROM users WHERE user_id = ?", (inviter_id,))
                count = cur.fetchone()[0]
                conn.commit()
                conn.close()

                # Уведомление тебе
                if count == 5:
                    await bot.send_message(MY_PERSONAL_ID, f"🎁 Юзер {inviter_id} пригласил 5 человек!")
                    # Сообщение пригласившему
                    try:
                        await bot.send_message(
                            inviter_id, 
                            f"🎉 Поздравляем! Ты пригласил 5 друзей.\nВот контакт дизайнера для связи: {MY_USERNAME}"
                        )
                    except:
                        pass # Если юзер заблокировал бота

async def main():
    init_db()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())