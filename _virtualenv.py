
import telebot
from telebot.types import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# 🔐 Авторизация Google Sheets
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
client = gspread.authorize(creds)
sheet = client.open("Parfumebot").sheet1

# 💾 Функция сохранения без дубликатов
def save_user_data(name, phone_number):
    all_records = sheet.get_all_records()
    for record in all_records:
        if record['name'] == name and record['phone_number'] == phone_number:
            return False  # Дубликат
    sheet.append_row([name, phone_number])
    return True

# 🤖 Инициализация бота
TOKEN = '7725277391:AAEls0OPwsexIrdjiVw_0Y2MUVsPhF0s3VQ'
bot = telebot.TeleBot(TOKEN)

# 🏁 /start
@bot.message_handler(commands=['start'])
def start(message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row('🛍 Каталог', '📍 Адреса')
    markup.row('❓ Вопросы', '📲 Получить консультацию')
    markup.row('📝 Начать покупку')
    bot.send_message(message.chat.id, f'Привет, {message.from_user.first_name}! Добро пожаловать в парфюмерный бот!', reply_markup=markup)

# 🆘 /help
@bot.message_handler(commands=['help'])
def help_command(message):
    bot.send_message(message.chat.id,
        "🆘 *Помощь по боту:*\n\n"
        "• /start — Главное меню\n"
        "• /help — Помощь\n"
        "• 'Начать покупку' — Отправить имя и номер телефона\n"
        "• 'Каталог' — Посмотреть ароматы\n"
        "• 'Адреса' — Где нас найти\n"
        "• 'Получить консультацию' — Связаться через WhatsApp или Instagram",
        parse_mode='Markdown')

# 📝 Начать покупку
@bot.message_handler(func=lambda message: message.text.lower() == '📝 начать покупку')
def start_purchase(message):
    msg = bot.send_message(message.chat.id, "Введите ваше имя:")
    bot.register_next_step_handler(msg, process_name)

def process_name(message):
    name = message.text.strip()
    msg = bot.send_message(message.chat.id, "Введите ваш номер телефона:")
    bot.register_next_step_handler(msg, process_phone, name)

def process_phone(message, name):
    phone_number = message.text.strip()
    success = save_user_data(name, phone_number)
    if success:
        bot.send_message(message.chat.id, "✅ Спасибо, ваши данные сохранены!")
    else:
        bot.send_message(message.chat.id, "⚠️ Эти данные уже были сохранены ранее.")

# 🛍 Каталог
@bot.message_handler(func=lambda m: m.text == '🛍 Каталог')
def show_catalog(message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row('👨 Мужские ароматы', '👩 Женские ароматы')
    markup.row('🌀 Унисекс', '🔙 Назад в меню')
    bot.send_message(message.chat.id, 'Выберите категорию ароматов:', reply_markup=markup)

# 👨 Мужские ароматы
@bot.message_handler(func=lambda m: m.text == '👨 Мужские ароматы')
def men_perfumes(message):
    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton('🛒 Купить', url='https://wa.me/77478076545'),
        InlineKeyboardButton('🔙 Назад', callback_data='back_to_catalog')
    )
    perfume_list = (
        '👨 *Мужские ароматы:* \n\n'
        '• Montblanc Explorer - 1 мл, 1500 тг\n'
        '• Dior Sauvage - 1 мл, 1500 тг\n'
        '• Bleu de Chanel - 1 мл, 1500 тг\n'
        '• Aventus by Creed - 1 мл, 1500 тг\n'
        '• Versace Eros - 1 мл, 1500 тг'
    )
    bot.send_message(message.chat.id, perfume_list, parse_mode='Markdown', reply_markup=markup)

# 👩 Женские ароматы
@bot.message_handler(func=lambda m: m.text == '👩 Женские ароматы')
def women_perfumes(message):
    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton('🛒 Купить', url='https://wa.me/77478076545'),
        InlineKeyboardButton('🔙 Назад', callback_data='back_to_catalog')
    )
    bot.send_message(message.chat.id, '👩 Женские ароматы:\n• White Chocola Extrait Richard', reply_markup=markup)

# 🌀 Унисекс
@bot.message_handler(func=lambda m: m.text == '🌀 Унисекс')
def unisex_perfumes(message):
    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton('🛒 Купить', url='https://wa.me/77478076545'),
        InlineKeyboardButton('🔙 Назад', callback_data='back_to_catalog')
    )
    bot.send_message(message.chat.id, '🌀 Унисекс ароматы:\n• Cassiopea Tiziana Terenzi', reply_markup=markup)

# 🔙 Назад в каталог (inline)
@bot.callback_query_handler(func=lambda call: call.data == 'back_to_catalog')
def callback_back(call):
    show_catalog(call.message)

# 🔙 Назад в меню
@bot.message_handler(func=lambda m: m.text == '🔙 Назад в меню')
def back_to_menu(message):
    start(message)

# 📍 Адреса магазинов
@bot.message_handler(func=lambda m: m.text == '📍 Адреса')
def addresses(message):
    text = (
        '📍 Наши магазины:\n'
        '1️⃣ ТД ГУЛЛИВЕР, бутик 15а, 1 этаж (Назарбаева 48/1)\n'
        '2️⃣ BATYRMALL - GREENWICH (Камзина 67/1)'
    )
    bot.send_message(message.chat.id, text)

# ❓ Часто задаваемые вопросы
@bot.message_handler(func=lambda m: m.text == '❓ Вопросы')
def faqs(message):
    text = (
        '❓ Часто задаваемые вопросы:\n\n'
        '🔹 *Как вас найти?*\nОтвет: блабла\n\n'
        '🔹 *Что мы продаем?*\nОтвет: блаблабла\n\n'
        '🔹 *Какой мне нужен запах?*\nОтвет: бла блаблабла'
    )
    bot.send_message(message.chat.id, text, parse_mode='Markdown')

# 📲 Получить консультацию
@bot.message_handler(func=lambda m: m.text == '📲 Получить консультацию')
def consult(message):
    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton('📞 WhatsApp', url='https://wa.me/77478076545'),
        InlineKeyboardButton('📸 Instagram', url='https://instagram.com/umma_iissu')
    )
    bot.send_message(message.chat.id, 'Свяжитесь с нами для консультации 👇', reply_markup=markup)

# ▶️ Запуск бота
print("Бот запущен...")
bot.polling(none_stop=True)
