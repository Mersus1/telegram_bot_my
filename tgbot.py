import telebot
from telebot import types
import requests
import sqlite3

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

