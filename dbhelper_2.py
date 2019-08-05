import os
import psycopg2

class DBHelper:
	
	def __init__(self):
		""" Устанавливаем соединение с БД """
		DATABASE_URL = os.environ['DATABASE_URL']
		self.connect = psycopg2.connect(DATABASE_URL, sslmode='require')
		print("Database opened successfully")
		self.cursor = self.connect.cursor()

#=======================================================================	
	def create_pic_infos_table(self):
		""" Cоздаём табдицу для хранения информации о картинах """
		self.cursor.execute(''' CREATE TABLE IF NOT EXISTS pic_infos
							(ID SERIAL PRIMARY KEY,
							FILE_ID TEXT NOT NULL,
							AUTHOR_NAME TEXT NOT NULL); ''')
		
		print("Table pic_infos created successfully")
		self.connect.commit()
		self.cursor.close()
		
#=======================================================================	
	def insert_single_to_pic_infos(self, file_id, author_name):
		''' Добавление картинки в БД '''
		self.cursor.execute(
				"INSERT INTO pic_infos (FILE_ID, AUTHOR_NAME) VALUES (%s, %s)", 
						(file_id, author_name)
						)
					
		print("Record inserted successfully")
		self.connect.commit()
		self.cursor.close()
		
#=======================================================================	
	def select_all_from_pic_infos(self):
		""" Получаем все строки """
		self.cursor.execute("SELECT ID, FILE_ID, AUTHOR_NAME FROM pic_infos")
		
		rows = self.cursor.fetchall()

		for row in rows:
			print("ID = ", row[0])
			print("FILE_ID = ", row[1])
			print("AUTHOR_NAME = ", row[2], "\n")
			
		print("Operation done successfully")
		self.cursor.close()
		return rows
		
#=======================================================================	
	def select_single_pic_infos(self, rownum):
		""" Получаем одну строку с номером rownum """
		self.cursor.execute("SELECT * FROM pic_infos WHERE id = %s", 
							(rownum,))
		
		row = self.cursor.fetchall()
		return row
		
#=======================================================================
	def select_author_name(self, name):
		""" Получаем одно имя художника """
		self.cursor.execute("SELECT author_name FROM pic_infos WHERE id = %s", 
							(name,))
		
		name = self.cursor.fetchall()
		return name
		
#=======================================================================	
	def count_rows_pic_infos(self):
		""" Считаем количество строк """
		self.cursor.execute("SELECT * FROM pic_infos")
		
		result = self.cursor.fetchall()
		self.cursor.close()
		return len(result)
		
#=======================================================================	
	def delete_pic_infos(self):
		''' Удаляем таблицу pic_infos '''
		self.cursor.execute("DROP TABLE pic_infos")
		
		print("Table delete successfully")
		self.connect.commit()
		self.cursor.close()
		
#=======================================================================
	def close_connect(self):
		''' Закрываем соединение с БД '''
		self.connect.close()
