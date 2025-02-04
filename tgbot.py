import telebot
from telebot import types
import requests
import sqlite3
import threading
from datetime import datetime
import time

# 🔥 ТВОИ ТОКЕНЫ 🔥
BOT_TOKEN = "7941022207:AAGXKVcABZlMItti0sz7KoWhi7NCgnGXPU0"
WEATHER_API_KEY = "f6dae385f5a3d00f4834cf4d5669cca0"

bot = telebot.TeleBot(BOT_TOKEN)

# Подключаем базу данных для напоминаний
conn = sqlite3.connect("reminders.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS reminders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    text TEXT,
    time TEXT,
    repeat INTEGER
)
""")
conn.commit()

# Словарь для хранения городов пользователей
user_cities = {}

# Главная клавиатура
main_kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
main_kb.add(types.KeyboardButton("🌤 Погода"), types.KeyboardButton("🔔 Напоминание"))

### --- ФУНКЦИИ НАПОМИНАНИЙ --- ###
def add_reminder(user_id, text, time, repeat):
    cursor.execute("INSERT INTO reminders (user_id, text, time, repeat) VALUES (?, ?, ?, ?)", (user_id, text, time, repeat))
    conn.commit()

def get_reminders():
    cursor.execute("SELECT * FROM reminders")
    return cursor.fetchall()

def delete_reminder(user_id):
    cursor.execute("DELETE FROM reminders WHERE user_id = ?", (user_id,))
    conn.commit()

def reminder_checker():
    while True:
        now = datetime.now().strftime("%H:%M")
        reminders = get_reminders()
        
        for reminder in reminders:
            rem_id, user_id, text, time, repeat = reminder

            # Разовое напоминание
            if time == now:
                bot.send_message(user_id, f"🔔 Напоминание: {text}")
                cursor.execute("DELETE FROM reminders WHERE id = ?", (rem_id,))
                conn.commit()

            # Каждый час (на 0-й минуте)
            elif repeat == 1 and datetime.now().minute == 0:
                bot.send_message(user_id, f"🔔 Напоминание (каждый час): {text}")

            # Каждый день (в 09:00)
            elif repeat == 2 and datetime.now().hour == 9 and datetime.now().minute == 0:
                bot.send_message(user_id, f"🔔 Напоминание (каждый день): {text}")

        time.sleep(60)  # Проверяем каждую минуту

# Запускаем напоминания в отдельном потоке
threading.Thread(target=reminder_checker, daemon=True).start()

### --- ФУНКЦИИ ПОГОДЫ --- ###
def get_weather(city):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric&lang=ru"
    response = requests.get(url).json()
    if response.get("main"):
        temp = response["main"]["temp"]
        desc = response["weather"][0]["description"]
        return f"🌍 Город: {city}\n🌡 Температура: {temp}°C\n☁️ Погода: {desc.capitalize()}"
    else:
        return "⚠️ Город не найден! Проверьте название."

### --- ОБРАБОТКА КОМАНД --- ###
@bot.message_handler(commands=["start"])
def start(message):
    bot.send_message(message.chat.id, "Привет! Я твой бот! Выбери действие:", reply_markup=main_kb)

@bot.message_handler(func=lambda message: message.text == "🌤 Погода")
def ask_city(message):
    if message.chat.id in user_cities:
        bot.send_message(message.chat.id, f"Использую сохранённый город: {user_cities[message.chat.id]}")
        bot.send_message(message.chat.id, get_weather(user_cities[message.chat.id]))
    else:
        bot.send_message(message.chat.id, "🌍 Введите название города:")

@bot.message_handler(func=lambda message: message.text == "🔔 Напоминание")
def reminder_prompt(message):
    bot.send_message(message.chat.id, "Что тебе напомнить? Напиши текст и время (например: 'Напомни купить молоко в 18:30')")

@bot.message_handler(func=lambda message: "напомни" in message.text.lower())
def set_reminder(message):
    try:
        text = message.text.lower().replace("напомни", "").strip()

        # Разовое напоминание (например, "в 18:30")
        if "в " in text:
            parts = text.split(" в ")
            reminder_text = parts[0].strip()
            reminder_time = parts[1].strip()
            add_reminder(message.chat.id, reminder_text, reminder_time, 0)
            bot.send_message(message.chat.id, f"✅ Напоминание добавлено: \"{reminder_text}\" в {reminder_time}")

        # Напоминание каждый час
        elif "каждый час" in text:
            add_reminder(message.chat.id, text.replace("каждый час", "").strip(), "00:00", 1)
            bot.send_message(message.chat.id, f"✅ Напоминание будет приходить **каждый час**!")

        # Напоминание каждый день
        elif "каждый день" in text:
            add_reminder(message.chat.id, text.replace("каждый день", "").strip(), "00:00", 2)
            bot.send_message(message.chat.id, f"✅ Напоминание будет приходить **каждый день**!")

        else:
            bot.send_message(message.chat.id, "⚠️ Формат: Напомни [текст] в [время]. Например: 'Напомни купить хлеб в 15:00'.")

    except IndexError:
        bot.send_message(message.chat.id, "⚠️ Формат: Напомни [текст] в [время] или 'каждый час'.")

@bot.message_handler(commands=["отменить"])
def cancel_reminder(message):
    delete_reminder(message.chat.id)
    bot.send_message(message.chat.id, "❌ Все напоминания удалены!")

@bot.message_handler(content_types=["text"])
def send_weather(message):
    if message.text.strip().isalpha():
        user_cities[message.chat.id] = message.text
        bot.send_message(message.chat.id, get_weather(message.text))
    else:
        bot.send_message(message.chat.id, "⚠️ Введите название города буквами.")

@bot.message_handler(content_types=["photo"])
def get_photo(message):
    bot.reply_to(message, "Что за дерьмо? 😂")

# Запуск бота
bot.polling(none_stop=True)