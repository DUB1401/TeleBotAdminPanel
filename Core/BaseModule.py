from ..Core.PanelOptions import PanelOptions

from typing import TYPE_CHECKING

from telebot import types

if TYPE_CHECKING:
	from .. import Panel

	from dublib.TelebotUtils.Users import UserData

class BaseModule:
	"""Базовый модуль панели управления."""

	#==========================================================================================#
	# >>>>> ЗАЩИЩЁННЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def _PostInitMethod(self):
		"""Метод, выполняющийся после инициализации объекта."""

		pass

	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __init__(self, panel: "Panel"):
		"""
		Базовый модуль панели управления.

		:param panel: Панель управления.
		:type panel: Panel
		"""

		self._Panel = panel

		self._PostInitMethod()

	def close(self, user: "UserData"):
		"""
		Обрабатывает закрытие модуля.

		:param user: Данные пользователя.
		:type user: UserData
		"""

		Options: PanelOptions = user.get_object("ap_options")
		Options.set_current_module(None)

	def open(self, user: "UserData"):
		"""
		Обрабатывает открытие модуля.

		:param user: Данные пользователя.
		:type user: UserData
		"""

		pass

	def process_call(self, call: types.CallbackQuery):
		"""
		Обрабатывает вызов от пользователя.

		:param call: Данные вызова.
		:type call: types.CallbackQuery
		"""

		pass

	def process_message(self, message: types.Message):
		"""
		Обрабатывает текстовое сообщение от пользователя.

		:param message: Данные сообщения.
		:type message: types.Message
		"""

		pass