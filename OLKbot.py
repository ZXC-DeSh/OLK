import telebot 
import random
from telebot import types

# Музыка - music
# Поэма - poem
# Открытка - img
# Рандомное эмодзи - emoji
# Рандомная игра на сегодня - game
# Выбор жанра - janr
# Старт - start

TOKEN = '5651190184:AAHA3j5Mb5_moQqets5pGo92UBhw9BU_KG4'

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def start(msg):
    welcome = 'Привет, отправь мне команду'
    Keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False, row_width=2)
    but_1 = telebot.types.KeyboardButton('Музыка')
    but_2 = telebot.types.KeyboardButton('Поэма')
    but_3 = telebot.types.KeyboardButton('Открытка')
    but_5 = telebot.types.KeyboardButton('Рандомное эмодзи')
    but_7 = telebot.types.KeyboardButton('Рандомная игра на сегодня')
    but_8 = telebot.types.KeyboardButton('Старт')
    but_9 = telebot.types.KeyboardButton('Выбор жанра')
    Keyboard.add(but_1,but_2,but_3,but_5,but_7,but_8,but_9)
    
    bot.send_message(msg.from_user.id, welcome, reply_markup=Keyboard)

@bot.message_handler(content_types=['text'])
def user_text(msg):
    if msg.text == 'Поэма':
        poem(msg)
    elif msg.text == 'Открытка':
       img(msg) 
    elif msg.text == 'Рандомное эмодзи':
        emoji(msg)
    elif msg.text == 'Рандомная игра на сегодня':
        game(msg)
    elif msg.text == 'Музыка':
        mus(msg)
    elif msg.text == 'Старт':
        start(msg)
    elif msg.text == 'Выбор жанра':
        janr(msg)    

@bot.message_handler(commands=['poem'])
def poem(msg):
    text = "Я помню чудное мгновенье: Передо мной явилась ты, Как мимолетное виденье, Как гений чистой красоты."
    bot.send_message(msg.from_user.id, text)

@bot.message_handler(commands=['img'])
def img(msg):
    image = open('bg.jpg','rb')
    bot.send_photo(msg.from_user.id, image)

@bot.message_handler(commands=['music'])
def mus(msg):
    mp3 = open('vorona.mp3','rb')
    bot.send_audio(msg.from_user.id, mp3)

@bot.message_handler(commands=['emoji'])
def emoji(msg):
    emojis = {
    "smile": "😊",
    "heart": "❤️",
    "laugh": "😂",
    "angry": "😠",
    "surprised": "😮",
    "ok": "👌",
    "yes": "👍",
    "no": "👎",
    "party": "🎉",
    "alien": "👽",
    "robot": "🤖",
    "smirk": "😏",
    "tongue": "😜",
    "wink": "😉",
    "applause": "👏"
}
    random_key = random.choice(list(emojis.keys()))
    random_emoji = emojis[random_key]
    bot.send_message(msg.from_user.id, random_emoji)


@bot.message_handler(commands=['game'])
def game(msg):
    game = {
        'Minecraft': 'Minecraft - это инди-игра в жанре песочницы с элементами выживания и открытым миром. Геймплей в игре прост - игроки добывают ресурсы, чтобы строить дома, замки и целые города. Ограничений в Minecraft фактически нет, кроме высоты уровня - в остальном игроки вольны творить все, что пожелают.',
        'Valorant': 'Valorant - это командная тактическая игра от Riot Games, разработчика League of Legends. Игроки делятся на две команды: атакующие и защитники, и должны выполнить свои задачи, чтобы победить.',
        'Fortnite': 'Fortnite - это игра в жанре battle royale, где игроки сражаются на карте, чтобы стать последним выжившим.',
        'Dota': 'Dota - это многопользовательская онлайн-игра в жанре MOBA, где игроки управляют героями с уникальными способностями и сражаются против другой команды.',
        'Бесконечное лето': 'Бесконечное лето - это визуальный роман, где игроки управляют главным героем, который приехал в летний лагерь и должен развивать отношения с другими персонажами.'
    }
    random_key = random.choice(list(game.keys()))
    random_game = game[random_key]
    bot.send_message(msg.from_user.id, random_game)

@bot.message_handler(commands=['janr'])
def janr(msg):
    markup_inline = types.InlineKeyboardMarkup()
    item_yes = types.InlineKeyboardButton(text='ДА', callback_data='yes')
    item_no = types.InlineKeyboardButton(text='НЕТ', callback_data='no')

    markup_inline.add(item_yes, item_no)
    bot.send_message(msg.from_user.id, 'Хотите узнать об игре вашего любимого жанра?', 
        reply_markup=markup_inline
    )

@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    responses = {
        'yes': {
            'message': 'Выберите жанр:',
            'buttons': [
                types.InlineKeyboardButton(text='Песочница', callback_data='Песочница'),
                types.InlineKeyboardButton(text='Стелс', callback_data='Стелс'),
                types.InlineKeyboardButton(text='РПГ', callback_data='РПГ'),
                types.InlineKeyboardButton(text='Стратегия', callback_data='Стратегия'),
            ]
        },
        'no': {'message': 'Ок, может быть в другой раз'},
        'Песочница': {'message': 'Майнкрафт'},
        'Стелс': {'message': 'Ассасин'},
        'РПГ': {'message': 'The Elder Scrolls V: Skyrim'},
        'Стратегия': {'message': 'Starcraft II'},
    }

    response = responses.get(call.data)
    if response:
        if 'buttons' in response:
            markup = types.InlineKeyboardMarkup()
            markup.add(*response['buttons'])
            bot.edit_message_text(response['message'], call.message.chat.id, call.message.message_id, reply_markup=markup)
        else:
            bot.edit_message_text(response['message'], call.message.chat.id, call.message.message_id)

bot.polling()