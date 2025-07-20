from .Moderation import ModerationInlineKeyboards

from dublib.TelebotUtils import UserData

from telebot import types

class InlineKeyboards:
	"""Шаблоны Inline-интерфейсов."""

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

		Menu = types.InlineKeyboardMarkup()
		OneUser = types.InlineKeyboardButton("Одному пользователю", callback_data = "ap_one_user")
		Menu.add(OneUser, row_width = 1)
		LastSampling = types.InlineKeyboardButton("1K", callback_data = "ap_sampling_last")
		AllSampling = types.InlineKeyboardButton("Все", callback_data = "ap_sampling_all")
		Cancel = types.InlineKeyboardButton("Отмена", callback_data = "ap_sampling_cancel")
		Menu.add(LastSampling, AllSampling, row_width = 2)
		Menu.add(Cancel, row_width = 1)

		return Menu