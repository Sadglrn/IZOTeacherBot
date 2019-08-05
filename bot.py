from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters, ConversationHandler)
from dbhelper_2 import DBHelper
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackQueryHandler
import logging
import os
import time
import random
import utils
import telegram
import scraping-info as scrap

questions = ['Кто нарисовал эту картину? Выбери ответ.', 'Кто художник этой картины? Выбери ответ.',
			'Красивая картина! А кто её художник? Выбери ответ.']
logger = logging.getLogger(__name__)

class Bot:
	download_enable = False
	
	def __init__(self, token, type_proxy, ip):
		request_kwargs={type_proxy:ip}
		self.updater = Updater(token, request_kwargs=request_kwargs)
		#self.updater = Updater(token = token)
		
		self.dp = self.updater.dispatcher
		
		# Enable logging
		logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
                    
		# on different commands - answer in Telegram   
		self.dp.add_handler(CommandHandler("game", self.game))
		self.dp.add_handler(CommandHandler("scores", self.user_results))
		self.dp.add_handler(CallbackQueryHandler(self.check_answer))
		self.dp.add_handler(CommandHandler("im", self.download_image, pass_args=True))
		self.dp.add_handler(CommandHandler("afisha", self.afisha)
		self.dp.add_handler(CommandHandler("help", self.user_help))
		self.dp.add_handler(MessageHandler(Filters.photo, self.image_handler))
	
		# log all errors
		self.dp.add_error_handler(self.error)
		
		return
		
#=======================================================================
	def afisha(self, bot, update):
		data = scrap.get_afisha()
		update.message.reply_text
#=======================================================================
	def download_image(self, bot, update, args):
		''' Разрешение/запрещение загрузки изображений в БД '''
		if args[0][0] == '+':
			self.download_enable = True
			update.message.reply_text("Загрузка изображений разрешена.")
		elif args[0][0] == '-':
			self.download_enable = False
			update.message.reply_text("Загрузка изображений запрещена.")
		elif args[0] == 'статус':
			update.message.reply_text("Текущий статус: " + str(self.download_enable))
		else:
			update.message.reply_text("Неверный пароль!")
		
		return

#=======================================================================
	def game(self, bot, update):
		# Подключаемся к базе данных
		db_worker = DBHelper()
	
		# Считаем количество столбцев
		utils.count_rows()
		
		# Получаем случайную строчку из БД
		picture_info = db_worker.select_single_pic_infos(utils.get_rand_num())
		
		# Выбираем из БД три случайных художника и формируем из них строку
		f = db_worker.select_author_name(utils.get_rand_num())
		wrong_answers = f[0][0]
		for number in range(2):
			f = db_worker.select_author_name(utils.get_rand_num())
			wrong_answers += ", " + f[0][0]
				
		# Формируем разметку
		reply_markup = utils.generate_markup(picture_info[0][2], wrong_answers)
	
		bot.send_photo(chat_id = update.message.chat_id, photo=picture_info[0][1])
		update.message.reply_text(random.choice(questions), reply_markup=reply_markup)
	
		# Включаем "игровой режим"
		''' Сформировать словарь и отправить его на запись в shelve'''
		user_info = {}
		user_info['user_id'] = update.message.chat_id
		user_info['right_answers'] = utils.get_right_answers()
		user_info['wrong_answers'] = utils.get_wrong_answers()
		user_info['current_answer'] = picture_info[0][2]
		utils.set_user_game(chat_id = update.message.chat_id, user_info = user_info)
	
		# Отсоединяемся от БД
		db_worker.close_connect()
		
		return

#=======================================================================	
	def check_answer(self, bot, update):
		query = update.callback_query

		# Если функция возвращает None -> Человек не в игре
		answer = utils.get_answer_for_user(query.message.chat_id)
		# Как Вы помните, answer может быть либо текст, либо None
		# Если None:
		if not answer:
			update.message.reply_text("Чтобы начать игру введи команду /game")
		else:
			# Если ответ правильный/неправильный
			if query.data == answer['current_answer']:
				bot.edit_message_text(text="Верно! Художник картины *{}*. \nВведи /game для следущего вопроса.".format(query.data), 
										chat_id=query.message.chat_id, message_id=query.message.message_id, parse_mode=telegram.ParseMode.MARKDOWN)
				utils.set_right_answers()
			else:
				bot.edit_message_text(text="*Неверно*, художник этой картины не {}. Попробуй ещё раз! \nВведи /game для следущего вопроса.".format(query.data),
										chat_id=query.message.chat_id, message_id=query.message.message_id, parse_mode=telegram.ParseMode.MARKDOWN)
				utils.set_wrong_answers()
		return

#=======================================================================	
	def user_results(self, bot, update):
		answer = utils.get_answer_for_user(update.message.chat.id)
		update.message.reply_text("Правильных ответов - " + str(answer["right_answers"]) + 
									"\nНеправильныз ответов - " + str(answer["wrong_answers"]))
		return
									
#=======================================================================	
	def user_help(self, bot, update):
		update.message.reply_text('Игра "Угадай художника".\n'
										'Доступные команды:\n'
										'/game - начать игру\n'
										'/scores - общая статистика\n'
										'/help - доступные команды и описание бота\n\n'
										'feedback - @ykv_svr')
		return 
		
#=======================================================================
	# Метод для загрузки картинки на сервер в базу данных
	def image_handler(self, bot, update):
		if self.download_enable == True:
			db_worker = DBHelper()
			img = []
			bot.get_file(update.message.photo[-1].file_id)
			img = [update.message.caption.title()]
			
			db_worker.insert_single_to_pic_infos(file_id=str(update.message.photo[-1].file_id), 
													author_name=img[0])
			
			update.message.reply_text("Изображение успещно добавлено.")
			
			db_worker.close_connect()
		else:
			update.message.reply_text("Добавление изобращений запрещено!")

		return

#=======================================================================	
	def error(self, bot, update, error):
		"""Log Errors caused by Updates."""
		logger.warning('Update "%s" caused error "%s"', update, error)
		return
#=======================================================================
	def run(self):
		self.updater.start_polling()
		return	
