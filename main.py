from random import choice

from telebot.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

from telebot import TeleBot

TOKEN = '6564387804:AAG7DokfxU5wmNQVonwqVKZXPgE9KiGXsBA'

BUTTON_FOR_BOT = {
	'Я выбрал число': '',
	'Не хочу играть': '',
	'Выбрать другую игру': '',
	'Информация об боте': ''
}


games = {}

repeat_mode = set()

bot = TeleBot(TOKEN)


@bot.message_handler(commands=['start'])
def start_game(message):
	chat_id = message.chat.id
	if chat_id in games or chat_id in repeat_mode:
		bot.send_message(chat_id, "Игра уже запущена! Пожалуйста, дайте мне подсказку.")
	else:
		markup = ReplyKeyboardMarkup(resize_keyboard=True)
		for start_bot in BUTTON_FOR_BOT.keys():
			item_button = KeyboardButton(start_bot)
			markup.add(item_button)
	bot.send_message(chat_id, 'Приветствую! Я бот "Jester". Загадайте число от 10 до 100, и я постараюсь его угадать! Нажмите "Я выбрал число", когда будете готовы.', reply_markup=markup)


@bot.message_handler(func=lambda message: message.text == 'Я выбрал число')
def choose_option(message):
	chat_id = message.chat.id
	if chat_id not in games:
		games[chat_id] = {
			'low': 10,
			'high': 100,'attempts': 0,
			'guess': 55
		}
		bot.send_message(chat_id, 'Я готов начинать угадывать! Напишите "меньше", если ваше число меньше, "больше", если больше, или "правильно", если я угадал.')


@bot.message_handler(func=lambda message: message.text.lower() in ['меньше', 'больше', 'правильно'])
def handle_guess(message):
	chat_id = message.chat.id
	if chat_id not in games:
		bot.send_message(chat_id, 'Пожалуйста, начните игру командой /start.')
		return
	game = games[chat_id]
	if message.text.lower() == 'правильно':
		bot.send_message(chat_id, f'Ура! Я угадал ваше число {game["guess"]} за {game["attempts"] + 1} попытки(ок).')
		del games[chat_id]
		return
	if message.text.lower() == 'меньше':
		game['high'] = game['guess'] - 1
	elif message.text.lower() == 'больше':
		game['low'] = game['guess'] + 1
		game['attempts'] += 1
	game['guess'] = (game['low'] + game['high']) // 2
	bot.send_message(chat_id, f'Мое предположение: {game["guess"]}. Напишите "меньше", если ваше число меньше, "больше", если больше, или "правильно", если я угадал.')


@bot.message_handler(func=lambda message: message.text == 'Не хочу играть')
def no_play(message):
	bot.send_message(message.chat.id, 'Если вы не хотите играть, выберите другую игру.')


@bot.message_handler(func=lambda message: message.text == 'Выбрать другую игру')
def choose_game(message):
	markup = InlineKeyboardMarkup()
	markup.row(InlineKeyboardButton('Орел решка', callback_data='Orel'))
	markup.row(InlineKeyboardButton('Угадай число', callback_data='guess'))
	markup.row(InlineKeyboardButton('Повторяй за мной', callback_data='repeat')) # Кнопка для повторения
	bot.send_message(message.chat.id, 'Вот все мои внутренние игры, выберите одну из них.', reply_markup=markup)


@bot.message_handler(func=lambda message: message.text == 'Информация об боте')
def info(message):
	bot.send_message(message.chat.id, 'Jester это телеграмм бот, который создан для развлечения.')


@bot.callback_query_handler(func=lambda call: call.data in ['Orel', 'guess', 'repeat'])
def handle_callback_query(call):
	chat_id = call.message.chat.id
	if call.data == 'Orel':
		result = choice(['Орел', 'Решка'])
		bot.send_message(chat_id, f'Выпало: {result}')
	elif call.data == 'guess':
		bot.send_message(chat_id, 'Отлично! Загадано число, и я начну угадывать.')
	elif call.data == 'repeat':
		repeat_mode.add(chat_id)
		bot.send_message(chat_id, 'Теперь я буду повторять все ваши сообщения. Напишите "Закончить игру", чтобы прекратить.')


@bot.message_handler(func=lambda message: message.chat.id in repeat_mode)
def repeat_message(message):
	chat_id = message.chat.id
	if message.text.lower() == 'закончить игру':
		repeat_mode.remove(chat_id)
		bot.send_message(chat_id, 'Режим повторения завершен.')
	else:
		bot.send_message(chat_id, message.text)


bot.infinity_polling()
