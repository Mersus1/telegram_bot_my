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
    text TEXT
)
""")
conn.commit()

# Словарь для хранения городов пользователей
user_cities = {}

# Главное меню
def main_keyboard():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add("🌤 Погода", "🔔 Напоминание", "❌ Отменить напоминание", "📷 Мой Instagram")
    return kb

# Напоминания
def add_reminder(user_id, text):
    cursor.execute("INSERT INTO reminders (user_id, text) VALUES (?, ?)", (user_id, text))
    conn.commit()

def get_reminders(user_id):
    cursor.execute("SELECT text FROM reminders WHERE user_id = ?", (user_id,))
    return cursor.fetchall()

def delete_reminder(user_id):
    cursor.execute("DELETE FROM reminders WHERE user_id = ?", (user_id,))
    conn.commit()

def reminder_checker():
    while True:
        users = cursor.execute("SELECT DISTINCT user_id FROM reminders").fetchall()
        for user in users:
            user_id = user[0]
            reminders = get_reminders(user_id)
            for reminder in reminders:
                bot.send_message(user_id, f"🔔 Напоминание: {reminder[0]}")
        time.sleep(3600)  # Проверяем каждый час

threading.Thread(target=reminder_checker, daemon=True).start()

# Погода
def get_weather(city):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric&lang=ru"
    response = requests.get(url).json()
    if response.get("main"):
        temp = response["main"]["temp"]
        desc = response["weather"][0]["description"]
        return f"🌍 Город: {city}\n🌡 Температура: {temp}°C\n☁️ Погода: {desc.capitalize()}"
    return "⚠️ Город не найден! Проверьте название."

# Команды
@bot.message_handler(commands=["start"])
def start(message):
    bot.send_message(message.chat.id, "Привет! Выбери действие:", reply_markup=main_keyboard())

@bot.message_handler(func=lambda msg: msg.text == "🌤 Погода")
def ask_city(message):
    bot.send_message(message.chat.id, "🌍 Введите название города:")

@bot.message_handler(func=lambda message: message.text and message.text.strip().isalpha())
def send_weather(message):
    city = message.text.strip()
    user_cities[message.chat.id] = city
    bot.send_message(message.chat.id, get_weather(city))

@bot.message_handler(func=lambda msg: msg.text == "🔔 Напоминание")
def reminder_prompt(message):
    bot.send_message(message.chat.id, "Что тебе напоминать каждый час? Напиши текст.")

@bot.message_handler(func=lambda message: message.text and message.text not in ["🌤 Погода", "🔔 Напоминание", "❌ Отменить напоминание", "📷 Мой Instagram"])
def set_reminder(message):
    add_reminder(message.chat.id, message.text)
    bot.send_message(message.chat.id, f"✅ Запомнил! Буду напоминать каждый час: \"{message.text}\"")

@bot.message_handler(func=lambda msg: msg.text == "❌ Отменить напоминание")
def cancel_reminder(message):
    delete_reminder(message.chat.id)
    bot.send_message(message.chat.id, "❌ Напоминание отключено!")

@bot.message_handler(func=lambda msg: msg.text == "📷 Мой Instagram")
def instagram_link(message):
    bot.send_message(message.chat.id, "📷 Мой Instagram: [тык](https://www.instagram.com)", parse_mode="Markdown")

@bot.message_handler(content_types=["photo"])
def get_photo(message):
    bot.reply_to(message, "Что за дерьмо? 😂")

bot.polling(none_stop=True)