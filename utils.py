from dbhelper_2 import DBHelper
from config import shelve_name
from random import shuffle
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
import shelve
import random

def count_rows():
	"""
	Данный метод считает общее количество строк в базе данных и сохраняет в хранилище.
	Потом из этого количества будем выбирать картинки.
	"""
	db = DBHelper()
	rowsnum = db.count_rows_pic_infos()
	with shelve.open(shelve_name, writeback=True) as storage:
		storage['rows_count'] = rowsnum

def get_rows_count():
	"""
	Получает из хранилища количество строк в БД
	:return: (int) Число строк
	"""
	with shelve.open(shelve_name, writeback=True) as storage:
		rowsnum = storage['rows_count']
	return rowsnum

def set_wrong_answers():
	with shelve.open(shelve_name, writeback=True) as storage:
		if "wrong_answers" in storage:
			ans = get_wrong_answers() + 1
			storage["wrong_answers"] = ans
		else:
			storage["wrong_answers"] = 1

def get_wrong_answers():
	with shelve.open(shelve_name, writeback=True) as storage:
		if "wrong_answers" in storage:
			ans = storage["wrong_answers"]
			return ans
		else:
			storage["wrong_answers"] = 0

def set_right_answers():
	with shelve.open(shelve_name, writeback=True) as storage:
		if "right_answers" in storage:
			ans = get_right_answers() + 1
			storage["right_answers"] = ans
		else:
			storage["right_answers"] = 1

def get_right_answers():
	with shelve.open(shelve_name, writeback=True) as storage:
		if "right_answers" in storage:
			ans = storage["right_answers"]
			return ans
		else:
			storage["right_answers"] = 0
			
def get_prev_img():
	with shelve.open(shelve_name, writeback=True) as storage:
		if "previous_imgs" in storage:
			prev = storage["previous_imgs"]
			return prev
		else:
			return 0

def set_prev_img(num_img):
	with shelve.open(shelve_name, writeback=True) as storage:
		storage["previous_imgs"] = num_img

def set_user_game(chat_id, user_info):
	"""
	Записываем юзера в игроки и запоминаем, что он должен ответить.
	:param chat_id: id юзера
	"""
	with shelve.open(shelve_name, writeback=True) as storage:
		storage[str(chat_id)] = user_info
		
def get_answer_for_user(chat_id):
	"""
	Получаем правильный ответ для текущего юзера.
	В случае, если человек просто ввёл какие-то символы, не начав игру, возвращаем None
	:param chat_id: id юзера
	:return: (str) Правильный ответ / None
	"""
	with shelve.open(shelve_name, writeback=True) as storage:
		try:
			answer = storage[str(chat_id)]
			return answer
		# Если человек не играет, то ничего не возвращаем
		except KeyError:
			return None

def finish_user_game(chat_id):
	"""
	Заканчиваем игру текущего пользователя и удаляем правильный ответ из хранилища
	:param chat_id: id юзера
	"""
	with shelve.open(shelve_name, writeback=True) as storage:
		del storage[str(chat_id)]

	
def get_rand_num():
	''' Проверяем чтобы следующее число не было таким же как и предыдущее '''
	prev_img = get_prev_img()
	for i in range(5):
		r = random.randint(1, get_rows_count())
		if r == prev_img:
			continue
		else:
			break
	set_prev_img(r)
	
	return r


def generate_markup(right_answer, wrong_answers):
	"""
	Создаем кастомную клавиатуру для выбора ответа
	:param right_answer: Правильный ответ
	:param wrong_answers: Набор неправильных ответов
	:return: Объект кастомной клавиатуры
	"""
	# Склеиваем правильный ответ с неправильными
	all_answers = '{},{}'.format(right_answer, wrong_answers)
	
	# Создаем лист (массив) и записываем в него все элементы
	list_items = []
	for item in all_answers.split(','):
		list_items.append(item)
	
	# Хорошенько перемешиваем все элементы	
	shuffle(list_items)
	
	# Заполняем клавиатуру перемешанными элементами
	keyboard = [[InlineKeyboardButton(list_items[0], callback_data=list_items[0])],
				[InlineKeyboardButton(list_items[1], callback_data=list_items[1])],
				[InlineKeyboardButton(list_items[2], callback_data=list_items[2])],
				[InlineKeyboardButton(list_items[3], callback_data=list_items[3])]]	
	
	# Формируем клавиатуру			
	reply_markup = InlineKeyboardMarkup(keyboard)
	
	return reply_markup
