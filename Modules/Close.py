from ..Core.BaseModule import BaseModule

from typing import TYPE_CHECKING

from telebot import types

if TYPE_CHECKING:
	from dublib.TelebotUtils.Users import UserData

class SM_Close(BaseModule):
	"""Модуль закрытия панели управления."""

	def open(self, user: "UserData"):
		"""
		Обрабатывает открытие модуля.

		:param user: Данные пользователя.
		:type user: UserData
		"""

		self._Panel.close(user)
		self._Panel.bot.send_message(user.id, "Панель управления закрыта.", reply_markup = types.ReplyKeyboardRemove())