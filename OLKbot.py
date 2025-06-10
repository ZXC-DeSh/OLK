import telebot
from telebot import types
import re

TOKEN = '8080966559:AAGvsCE5cL1FfREmrJqTTNO1WfZmiR5-Bug'
bot = telebot.TeleBot(TOKEN)

TARGET_CHAT_ID = -1002860241295  # Чат в который отправляются формы

user_states = {}

# --- Модуль клавиатур ---
def create_inline_keyboard():
    keyboard = types.InlineKeyboardMarkup()
    btn_suggestion = types.InlineKeyboardButton('💡 Предложение', callback_data='suggestion')
    btn_complaint = types.InlineKeyboardButton('😠 Жалоба', callback_data='complaint')
    btn_gratitude = types.InlineKeyboardButton('❤️ Благодарность', callback_data='gratitude')
    keyboard.add(btn_suggestion, btn_complaint, btn_gratitude)
    return keyboard

# --- Модуль управления состоянием ---
def clear_state(user_id):
    user_states[user_id] = {'state': None, 'data': {}}

def get_user_state(user_id):
    if user_id not in user_states:
        user_states[user_id] = {'state': None, 'data': {}}
    return user_states[user_id]

# --- Модуль валидации ---
def is_valid_email(email):
    email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return re.match(email_pattern, email) is not None

# --- Обработчики ---
@bot.message_handler(commands=['start'])
def start(msg):
    user_id = msg.from_user.id
    clear_state(user_id)
    welcome_message = "Здравствуйте! Что вы хотите сделать?"
    keyboard = create_inline_keyboard()
    bot.send_message(user_id, welcome_message, reply_markup=keyboard)

@bot.callback_query_handler(func=lambda call: True)
def handle_callback_query(call):
    user_id = call.from_user.id
    if call.data == 'suggestion':
        bot.answer_callback_query(call.id)
        ask_fio(call.message)
    elif call.data == 'complaint':
        bot.answer_callback_query(call.id)
        ask_complaint(call.message)
    elif call.data == 'gratitude':
        bot.answer_callback_query(call.id)
        ask_gratitude(call.message)
    else:
        bot.send_message(user_id, "Неизвестная команда.")

# --- Обработчики состояний ---
def ask_fio(message):
    user_id = message.chat.id
    user_states[user_id] = {'state': 'suggestion', 'data': {}}
    bot.send_message(user_id, "Пожалуйста, введите ваше ФИО:")

def ask_complaint(message):
    user_id = message.chat.id
    user_states[user_id] = {'state': 'complaint', 'data': {}}
    bot.send_message(user_id, "Пожалуйста, опишите вашу проблему:")

def ask_gratitude(message):
    user_id = message.chat.id
    user_states[user_id] = {'state': 'gratitude', 'data': {}}
    bot.send_message(user_id, "Пожалуйста, опишите вашу благодарность:")

@bot.message_handler(func=lambda msg: True, content_types=['text'])
def process_message(msg):
    user_id = msg.from_user.id
    user_state = get_user_state(user_id)

    try:
        if user_state['state'] == 'suggestion':
            if 'fio' not in user_state['data']:
                user_state['data']['fio'] = msg.text
                bot.send_message(user_id, "Теперь введите ваш email:")
            elif 'email' not in user_state['data']:
                email = msg.text
                if is_valid_email(email):
                    user_state['data']['email'] = email
                    bot.send_message(user_id, "Опишите ваше предложение:")
                else:
                    bot.send_message(
                        user_id,
                        "Неверный формат email. Пожалуйста, введите корректный email.\n"
                        "Пример: example@domain.com",
                    )
                    return
            else:
                user_state['data']['description'] = msg.text
                report = (
                    "*Новое предложение:*\n"
                    f"*ФИО:* {user_state['data']['fio']}\n"
                    f"*Email:* {user_state['data']['email']}\n"
                    f"*Описание:* {user_state['data']['description']}"
                )
                bot.send_message(TARGET_CHAT_ID, report, parse_mode='Markdown')
                bot.send_message(user_id, "Спасибо за ваше предложение!", reply_markup=create_inline_keyboard())
                clear_state(user_id)

        elif user_state['state'] == 'complaint':
            user_state['data']['description'] = msg.text
            report = f"*Новая жалоба:*\n*Описание:* {user_state['data']['description']}"
            bot.send_message(TARGET_CHAT_ID, report, parse_mode='Markdown')
            bot.send_message(user_id, "Спасибо за вашу жалобу. Мы рассмотрим её.", reply_markup=create_inline_keyboard())
            clear_state(user_id)

        elif user_state['state'] == 'gratitude':
            user_state['data']['description'] = msg.text
            report = f"*Новая благодарность:*\n*Описание:* {user_state['data']['description']}"
            bot.send_message(TARGET_CHAT_ID, report, parse_mode='Markdown')
            bot.send_message(user_id, "Спасибо за вашу благодарность!", reply_markup=create_inline_keyboard())
            clear_state(user_id)
        else:
            bot.send_message(user_id, "Пожалуйста, используйте кнопки в меню.", reply_markup=create_inline_keyboard())

    except Exception as e:
        print(f"Ошибка при обработке сообщения: {e}")
        bot.send_message(
            user_id,
            "Произошла непредвиденная ошибка. Пожалуйста, попробуйте позже или начните заново с команды /start.",
            reply_markup=create_inline_keyboard(),
        )
        clear_state(user_id)

if __name__ == '__main__':
    print("Bot is running...")
    bot.polling(none_stop=True)
