import telebot
from telebot import types
import re

TOKEN = '8080966559:AAGvsCE5cL1FfREmrJqTTNO1WfZmiR5-Bug'
bot = telebot.TeleBot(TOKEN)

TARGET_CHAT_ID = -1002860241295  # чат в который отправляются формы
FEEDBACK_THREAD_ID = 20  # message_thread_id для темы обратной связи
ISSUES_THREAD_ID = 21    # message_thread_id для темы неисправностей

user_states = {}

# --- Модуль клавиатур ---
def create_main_keyboard():
    keyboard = types.InlineKeyboardMarkup()
    btn_suggestion = types.InlineKeyboardButton('💡 Предложение', callback_data='suggestion')
    btn_complaint = types.InlineKeyboardButton('😠 Жалоба', callback_data='complaint')
    btn_gratitude = types.InlineKeyboardButton('❤️ Благодарность', callback_data='gratitude')
    btn_malfunction = types.InlineKeyboardButton('⚠️ Неисправность / поломка', callback_data='malfunction')
    keyboard.add(btn_suggestion, btn_complaint, btn_gratitude, btn_malfunction)
    return keyboard

def create_form_keyboard():
    keyboard = types.InlineKeyboardMarkup()
    btn_cancel = types.InlineKeyboardButton('❌ Отмена', callback_data='cancel')
    keyboard.add(btn_cancel)
    return keyboard

def create_gratitude_keyboard():
    keyboard = types.InlineKeyboardMarkup()
    btn_anonymous = types.InlineKeyboardButton('🤫 Анонимно', callback_data='gratitude_anonymous')
    btn_with_name = types.InlineKeyboardButton('📝 С ФИО', callback_data='gratitude_with_name')
    btn_cancel = types.InlineKeyboardButton('❌ Отмена', callback_data='cancel')
    keyboard.add(btn_anonymous, btn_with_name, btn_cancel)
    return keyboard

# --- Модуль управления состоянием пользователя ---
def clear_state(user_id):
    user_states[user_id] = {'state': None, 'data': {}}

def get_user_state(user_id):
    if user_id not in user_states:
        user_states[user_id] = {'state': None, 'data': {}}
    return user_states[user_id]

# --- Модуль валидации ---
def is_valid_email(email):
    email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"  # регулярное выражение
    return re.match(email_pattern, email) is not None

# --- Обработчики ---
@bot.message_handler(commands=['start'])
def start(msg):
    user_id = msg.from_user.id
    clear_state(user_id)
    welcome_message = "Здравствуйте! Что вы хотите сделать?"
    keyboard = create_main_keyboard()
    bot.send_message(user_id, welcome_message, reply_markup=keyboard)

@bot.message_handler(commands=['id'])
def send_chat_id(message):
    bot.reply_to(message, f"Chat ID: {message.chat.id}")

@bot.callback_query_handler(func=lambda call: True)
def handle_callback_query(call):
    user_id = call.from_user.id
    message_id = call.message.message_id

    if call.data == 'suggestion':
        bot.answer_callback_query(call.id)
        ask_fio(call.message, message_id)
    elif call.data == 'complaint':
        bot.answer_callback_query(call.id)
        ask_complaint(call.message, message_id)
    elif call.data == 'gratitude':
        bot.answer_callback_query(call.id)
        ask_gratitude_option(call.message, message_id)
    elif call.data == 'gratitude_anonymous':
        bot.answer_callback_query(call.id)
        ask_gratitude_anonymous(call.message, message_id)
    elif call.data == 'gratitude_with_name':
        bot.answer_callback_query(call.id)
        ask_fio(call.message, message_id)
        user_states[user_id]['state'] = 'gratitude_with_name'
    elif call.data == 'malfunction':
        bot.answer_callback_query(call.id)
        ask_malfunction_info(call.message, message_id, 'department')
    elif call.data == 'cancel':
        bot.answer_callback_query(call.id)
        clear_state(user_id)
        bot.edit_message_text(
            chat_id=user_id,
            message_id=message_id,
            text="Вы вернулись в главное меню.",
            reply_markup=create_main_keyboard()
        )
    else:
        bot.send_message(user_id, "Неизвестная команда.")

# --- Обработчики состояний ---
def ask_fio(message, message_id):
    user_id = message.chat.id
    user_states[user_id] = {'state': 'suggestion', 'data': {}}
    bot.edit_message_text(
        chat_id=user_id,
        message_id=message_id,
        text="Пожалуйста, введите ваше ФИО:",
        reply_markup=create_form_keyboard()
    )

def ask_complaint(message, message_id):
    user_id = message.chat.id
    user_states[user_id] = {'state': 'complaint', 'data': {}}
    bot.edit_message_text(
        chat_id=user_id,
        message_id=message_id,
        text="Пожалуйста, опишите вашу проблему:",
        reply_markup=create_form_keyboard()
    )

def ask_gratitude_option(message, message_id):
    user_id = message.chat.id
    user_states[user_id] = {'state': 'gratitude_option', 'data': {}}
    bot.edit_message_text(
        chat_id=user_id,
        message_id=message_id,
        text="Как вы хотите отправить благодарность?",
        reply_markup=create_gratitude_keyboard()
    )

def ask_gratitude_anonymous(message, message_id):
    user_id = message.chat.id
    user_states[user_id] = {'state': 'gratitude_anonymous', 'data': {}}
    bot.edit_message_text(
        chat_id=user_id,
        message_id=message_id,
        text="Пожалуйста, опишите вашу благодарность:",
        reply_markup=create_form_keyboard()
    )

def ask_malfunction_info(message, message_id, step):
    user_id = message.chat.id
    user_state = get_user_state(user_id)

    if step == 'department':
        user_state['state'] = 'malfunction_department'
        bot.edit_message_text(
            chat_id=user_id, message_id=message_id,
            text="Пожалуйста, укажите отделение, в котором произошла неисправность:",
            reply_markup=create_form_keyboard()
        )
    elif step == 'floor':
        user_state['state'] = 'malfunction_floor'
        user_state['data']['department'] = message.text
        bot.send_message(
            user_id,
            "Укажите, на каком этаже произошла неисправность:",
            reply_markup=create_form_keyboard()
        )
    elif step == 'description':
        user_state['state'] = 'malfunction_description'
        user_state['data']['floor'] = message.text
        bot.send_message(
            user_id,
            "Пожалуйста, подробно опишите, что случилось (проблема/поломка):",
            reply_markup=create_form_keyboard()
        )

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
                bot.send_message(TARGET_CHAT_ID, report, parse_mode='Markdown', message_thread_id=FEEDBACK_THREAD_ID)
                bot.send_message(user_id, "Спасибо за ваше предложение!", reply_markup=create_main_keyboard())
                clear_state(user_id)

        elif user_state['state'] == 'complaint':
            user_state['data']['description'] = msg.text
            report = f"*Новая жалоба:*\n*Описание:* {user_state['data']['description']}"
            bot.send_message(TARGET_CHAT_ID, report, parse_mode='Markdown', message_thread_id=FEEDBACK_THREAD_ID)
            bot.send_message(user_id, "Спасибо за вашу жалобу. Мы рассмотрим её.", reply_markup=create_main_keyboard())
            clear_state(user_id)

        elif user_state['state'] == 'gratitude_anonymous':
            user_state['data']['description'] = msg.text
            report = f"*Новая благодарность (анонимно):*\n*Описание:* {user_state['data']['description']}"
            bot.send_message(TARGET_CHAT_ID, report, parse_mode='Markdown', message_thread_id=FEEDBACK_THREAD_ID)
            bot.send_message(user_id, "Спасибо за вашу благодарность!", reply_markup=create_main_keyboard())
            clear_state(user_id)

        elif user_state['state'] == 'gratitude_with_name':
            if 'fio' not in user_state['data']:
                user_state['data']['fio'] = msg.text
                bot.send_message(user_id, "Пожалуйста, опишите вашу благодарность:")
            else:
                user_state['data']['description'] = msg.text
                report = (
                    "*Новая благодарность:*\n"
                    f"*ФИО:* {user_state['data']['fio']}\n"
                    f"*Описание:* {user_state['data']['description']}"
                )
                bot.send_message(TARGET_CHAT_ID, report, parse_mode='Markdown', message_thread_id=FEEDBACK_THREAD_ID)
                bot.send_message(user_id, "Спасибо за вашу благодарность!", reply_markup=create_main_keyboard())
                clear_state(user_id)

        elif user_state['state'] == 'malfunction_department':
            user_state['data']['department'] = msg.text
            ask_malfunction_info(msg, msg.message_id, 'floor')

        elif user_state['state'] == 'malfunction_floor':
            user_state['data']['floor'] = msg.text
            ask_malfunction_info(msg, msg.message_id, 'description')

        elif user_state['state'] == 'malfunction_description':
            user_state['data']['description'] = msg.text
            report = (
                "*Новая заявка на неисправность/поломку:*\n"
                f"*Отделение:* {user_state['data'].get('department', 'Не указано')}\n"
                f"*Этаж:* {user_state['data'].get('floor', 'Не указано')}\n"
                f"*Описание проблемы:* {user_state['data']['description']}"
            )
            bot.send_message(TARGET_CHAT_ID, report, parse_mode='Markdown', message_thread_id=ISSUES_THREAD_ID)
            bot.send_message(user_id, "Спасибо! Ваша заявка принята.", reply_markup=create_main_keyboard())
            clear_state(user_id)

        else:
            welcome_message = "Здравствуйте! Пожалуйста, используйте кнопки в меню."
            keyboard = create_main_keyboard()
            bot.send_message(user_id, welcome_message, reply_markup=keyboard)

    except Exception as e:
        print(f"Ошибка при обработке сообщения: {e}")
        bot.send_message(
            user_id,
            "Произошла непредвиденная ошибка. Пожалуйста, попробуйте позже или начните заново с команды /start.",
            reply_markup=create_main_keyboard(),
        )
        clear_state(user_id)

if __name__ == '__main__':
    print("Bot is running...")
    bot.polling(none_stop=True)