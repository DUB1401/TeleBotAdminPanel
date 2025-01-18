from dublib.TelebotUtils import UserData

from telebot import types

class InlineKeyboards:
	"""Генератор Inline-интерфейса."""

	def __init__(self):
		"""Генератор Inline-интерфейса."""

		pass

	def extract():
		"""Строит Inline-интерфейс: выгрузка."""

		#---> Генерация кнопочного интерфейса.
		#==========================================================================================#
		Menu = types.InlineKeyboardMarkup()
		Extract = types.InlineKeyboardButton("Выгрузить", callback_data = "ap_extract")
		Menu.add(Extract)

		return Menu
	
	def sampling(admin: UserData):
		"""
		Строит Inline-интерфейс: выборка.
			admin – администратор.
		"""

		#---> Генерация кнопочного интерфейса.
		#==========================================================================================#
		Menu = types.InlineKeyboardMarkup()
		LastSampling = types.InlineKeyboardButton("1K", callback_data = "ap_sampling_last")
		AllSampling = types.InlineKeyboardButton("Все", callback_data = "ap_sampling_all")
		Cancel = types.InlineKeyboardButton("Отмена", callback_data = "ap_sampling_cancel")
		Menu.add(LastSampling, AllSampling, row_width = 2)
		Menu.add(Cancel, row_width = 1)

		return Menu
		