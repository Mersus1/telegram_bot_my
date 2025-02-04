import telebot
from telebot import types
import requests

# Токен Telegram-бота
BOT_TOKEN = "7941022207:AAGXKVcABZlMItti0sz7KoWhi7NCgnGXPU0"

# API-ключ OpenWeather (получите на https://openweathermap.org/api)
WEATHER_API_KEY = "f6dae385f5a3d00f4834cf4d5669cca0"

bot = telebot.TeleBot(BOT_TOKEN)

# Функция для получения погоды
def get_weather(city):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric&lang=ru"
    response = requests.get(url)
    data = response.json()

    if data.get("cod") != 200:
        return "❌ Город не найден. Попробуйте снова."

    weather_desc = data["weather"][0]["description"].capitalize()
    temp = data["main"]["temp"]
    feels_like = data["main"]["feels_like"]
    humidity = data["main"]["humidity"]
    wind_speed = data["wind"]["speed"]

    return (f"🌤 Погода в городе {city}:\n"
            f"🌡 Температура: {temp}°C (ощущается как {feels_like}°C)\n"
            f"💨 Ветер: {wind_speed} м/с\n"
            f"💧 Влажность: {humidity}%\n"
            f"🌍 {weather_desc}")

# Обработчик команды /start
@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn_insta = types.KeyboardButton("📸 Instagram")
    btn_weather = types.KeyboardButton("🌤 Погода")
    markup.add(btn_insta, btn_weather)
   
    bot.send_message(
        message.chat.id,
        f"Привет, {message.from_user.first_name}!\nВыбери действие:",
        reply_markup=markup
    )

# Обработчик кнопки "Instagram"
@bot.message_handler(func=lambda message: message.text == "📸 Instagram")
def send_instagram(message):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("Моя Insta", url="https://www.instagram.com/i_play_beatifully?igsh=ZzR5dHY3MjFpd3dh"))
    bot.send_message(message.chat.id, "📸 Нажмите на кнопку ниже:", reply_markup=markup)

# Обработчик кнопки "Погода"
@bot.message_handler(func=lambda message: message.text == "🌤 Погода")
def ask_city(message):
    bot.send_message(message.chat.id, "🌍 Введите название города:")

# Обработчик ввода города
@bot.message_handler(content_types=["text"])
def send_weather(message):
    city = message.text
    weather_info = get_weather(city)
    bot.send_message(message.chat.id, weather_info)

# Обработчик отправки фото (из твоего кода)
@bot.message_handler(content_types=["photo"])
def get_photo(message):
    bot.reply_to(message, "Что за дерьмо? 😂")

# Запуск бота
bot.polling(none_stop=True)