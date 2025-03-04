import telebot
import config
from telebot import types
from random import randint
import wikipedia
import re
import sqlite3

bot = telebot.TeleBot(config.bot)

number = False
game = False
wiki = False
admins = [5026469250]
clients = []
text = ""
link = ""

# Создали базу данных
conn = sqlite3.connect("users.db", check_same_thread=False)
# объект-курсор для запросов в бд (добавить, удалить)
cur = conn.cursor()

cur.execute("CREATE TABLE IF NOT EXISTS users(id INT);")
conn.commit()




# def my_decarator(f):
#     def wrapper():
#         print("Hello")
#         f()
#     return wrapper
#
# @my_decarator
# def say_name():
#     print("Андрей")
#
# say_name()
# #я не понял что произошло




@bot.message_handler(commands=["start"])
def start_command(message):
    if message.chat.id in admins:
        help(message)
    else:
        info = cur.execute("SELECT * FROM users WHERE id=?", (message.chat.id,)).fetchone()
        if not info:
            cur.execute("INSERT INTO users (id) VALUES (?)", (message.chat.id,))
            conn.commit()
            bot.send_message(message.chat.id, "Теперь вы будете получать рассылку!")
    bot.reply_to(message, "Hello, how are you?")

def help(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton("Редактировать текст"))
    markup.add(types.KeyboardButton("Редактировать ссылку"))
    markup.add(types.KeyboardButton("Показать текст"))
    markup.add(types.KeyboardButton("Начать рассылку"))
    markup.add(types.KeyboardButton("Помощь"))
    bot.send_message(message.chat.id, "Команды для бота. \n"
                                      "/edit_text - Редактировать текст. \n"
                                      "/edit_link - Редактировать ссылку. \n"
                                      "/show_message - Показать текст. \n"
                                      "/send or /send_message - Начать рассылку. \n"
                                      "/help - Помощь.", reply_markup=markup)

@bot.message_handler(commands=["show_message"])
def show_message(message):
    if message.chat.id in admins:
        bot.send_message(message.chat.id, f"Подготовленный текст для рассылки: \n"
                     f"{text}\n"
                     f"{link}")



@bot.message_handler(commands=["edit_text"])
def edit_text(message):
    m = bot.send_message(message.chat.id, "Введите сообщение для рассылки")
    bot.register_next_step_handler(m, save_text)
def save_text(message):
    global text
    if message.text not in (message.chat.id, "Изменить ссылку"):
        text = message.text
        bot.send_message(message.chat.id, f"Я сохрнаил текст: {text}")
    else:
        bot.send_message(message.chat.id, "Некорректный текст")



@bot.message_handler(commands=["edit_link"])
def edit_link(message):
    m = bot.send_message(message.chat.id, "Введите сообщение для рассылки")
    bot.register_next_step_handler(m, save_link)
def save_link(message):
    global link
    regex = re.compile(
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # проверка dot
        r'localhost|'
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # проверка ip 
        r'(?::\d+)?'
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    if message.text is not None and regex.search(message.text):
        link = message.text
        bot.send_message(message.chat.id, "Ссылка сохранена")
    else:
        m = bot.send_message(message.chat.id, "Сылка некоректная, исправьте или введите другую")
        bot.register_next_step_handler(m, save_link)


@bot.message_handler(commands=["send", "send_message"])
def send_message(message):
    global text, link
    if message.chat.id in admins:
        if text != "":
            if link != "":
                cur.execute("SELECT id FROM users")
                massive = cur.fetchall()
                print(massive)
                for client in massive:
                    id = client[0]
                    sending(id)
                else:
                    text = ""
                    link = ""
            else:
                bot.send_message(message.chat.id, "Ссылка не приложена!")
        else:
            bot.send_message(message.chat.id, "Текст не приложена")
    #if message.chat.id in admins and len(text) != 0 and len(link) != 0:
        #for client in clients:
            #print(client)
def sending(id):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton(text="Click me", url=link))
    bot.send_message(id, text, reply_markup=markup)






@bot.message_handler(commands=["хэппи"])
def test(message):
    print(message)
    bot.send_message(message.chat.id, "Бёздэй")






@bot.message_handler(commands=["play"])
def bot_play_service(message):
    markup_inline = types.InlineKeyboardMarkup()  # 1 - создать клавиатуру
    btn_y = types.InlineKeyboardButton(text="yes", callback_data="yes")  # 2 - создать кнопку для клавиатуры
    btn_n = types.InlineKeyboardButton(text="no", callback_data="no")  # 3 - создать кнопку2 для клавиатуры
    markup_inline.add(btn_y, btn_n)
    bot.send_message(message.chat.id, "You want to play games?", reply_markup=markup_inline)


@bot.callback_query_handler(func=lambda call:True)
def callback_buttons(call):
    if call.data == "yes":
        markup = types.ReplyKeyboardMarkup()
        btn_re = types.KeyboardButton("угадайка")
        btn_wi = types.KeyboardButton("википедия")
        markup.add(btn_re, btn_wi)
        bot.send_message(call.message.chat.id, "Поздравляю! Вы в игре", reply_markup=markup)
    elif call.data == "no":
        bot.send_message(call.message.chat.id, "Ну чтож такое..")






@bot.message_handler(content_types=["text"])
def text(message):
    global number, game, wiki
    text = message.text.lower()
    if wiki:
        bot.send_message(message.chat.id, get_wiki(text))
    if text == "привет":
        print(message)
        bot.send_message(message.chat.id, "Привет, как ты?")
    elif text == "угадайка":
        game_random_number(message)
        game = True
    elif text == str(number) and text in ("1", "2", "3") and game:
        game = False
        bot.send_message(message.chat.id, "УГАДААЛ!")
    elif text == "википедия":
        bot.send_message(message.chat.id, "Что хотите найти?")
        wiki = True
    elif text == "редактировать текст":
        edit_text(message)


def game_random_number(message):
    global number
    number = randint(1, 3)
    print(number)
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)

    btn_an = types.KeyboardButton("1") # 1 sposob
    markup.add(btn_an) # 1 sposob

    markup.add(types.KeyboardButton("2")) # 2 sposob

    btn_an3 = types.KeyboardButton("3")

    markup.add(btn_an3)
    bot.send_message(message.chat.id, "Угадай число", reply_markup=markup)
wikipedia.set_lang("ru")
def get_wiki(word):
    try:
        w = wikipedia.page(word)
        wikitext = w.content[:1000]
        wikimas = wikitext.split(".")
        wikimas = wikimas[:-1] # Убирает последний элемент из списка

        wiki_result = ""
        for i in wikimas:
            if not ("==" in i):
                wiki_result = wiki_result + i + "."
            else:
                break

        wiki_result = re.sub("\([^()]*\)", "", wiki_result)
        return wiki_result
    except Exception as erroe:
        return f"Ничего не нашёл {error}"
print(get_wiki("Екатеринбург"))






bot.infinity_polling() #контролирует, когда боту приходят сообщения и позволяет работать