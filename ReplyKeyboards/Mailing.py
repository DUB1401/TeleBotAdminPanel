from dublib.TelebotUtils import UserData

from telebot import types

class MailingReplyTemplates:
	"""Генератор Reply-интерфейса."""

	def mailing(user: UserData) -> types.ReplyKeyboardMarkup:
		"""
		Строит кнопочный интерфейс: рассылка.
			user – администратор.
		"""

		Options = user.get_property("ap")

		ButtonText = "Удалить" if Options["button_link"] else "Добавить"
		Status = "🔴 Остановить" if Options["mailing"] else "🟢 Запустить"
		Menu = types.ReplyKeyboardMarkup(resize_keyboard = True)
		Start = types.KeyboardButton(Status)
		Sampling = types.KeyboardButton("🎯 Выборка")
		View = types.KeyboardButton("🔎 Просмотр")
		Edit = types.KeyboardButton("✏️ Редактировать")
		Button = types.KeyboardButton(f"🕹️ {ButtonText} кнопку")
		Back = types.KeyboardButton("↩️ Назад")
		Menu.add(Start, Sampling, View, Edit, Button, Back, row_width = 1)

		return Menu