from ...Core.BaseModule import BaseModule

from dublib.CLI.Templates.Bus import PrintWarning

from typing import TYPE_CHECKING
from os import PathLike
import os

from telebot import types

from dublib.TelebotUtils import UserData

if TYPE_CHECKING:
	from dublib.TelebotUtils.Users import UserData

class SM_Extraction(BaseModule):
	"""Модуль извлечения файлов."""

	#==========================================================================================#
	# >>>>> СВОЙСТВА <<<<< #
	#==========================================================================================#

	@property
	def files(self) -> dict[str, PathLike]:
		"""Словарь данных извлекаемых файлов."""

		return self.__Files

	#==========================================================================================#
	# >>>>> ПРИВАТНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __SendFilesList(self, user: "UserData"):
		"""
		Отправляет список помеченных к выгрузке файлов.

		:param user: Данные пользователя.
		:type user: UserData
		"""

		
		Menu = types.ReplyKeyboardMarkup(resize_keyboard = True)
		for Name in self.__Files: Menu.add(types.KeyboardButton(Name))
		Menu.add("↩️ Назад")
		self._Bot.send_message(user.id, "Список файлов для выгрузки:", reply_markup = Menu)

	#==========================================================================================#
	# >>>>> ЗАЩИЩЁННЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def _PostInitMethod(self):
		"""Метод, выполняющийся после инициализации объекта."""

		self.__Files = dict()

	#==========================================================================================#
	# >>>>> ОБЩИЕ ПУБЛИЧНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def close(self, user: "UserData"):
		"""
		Обрабатывает закрытие модуля.

		:param user: Данные пользователя.
		:type user: UserData
		"""

		super().close(user)
		LayerMarkup = self._Panel.get_current_layer_reply_markup(user)

		self._Panel.bot.send_message(
			chat_id = user.id,
			text = "Модуль выгрузки закрыт.",
			reply_markup = LayerMarkup
		)
		
	def open(self, user: "UserData"):
		"""
		Обрабатывает открытие модуля.

		:param user: Данные пользователя.
		:type user: UserData
		"""

		if not self.__Files:
			self._Bot.send_message(user.id, "Файлы для выгрузки не указаны.")
			super().close(user)
			return
		
		self.__SendFilesList(user)

	def process_message(self, message: types.Message):
		"""
		Обрабатывает текстовое сообщение от пользователя.

		:param message: Данные сообщения.
		:type message: types.Message
		"""

		User = self._Panel.users_manager.auth(message.from_user)

		match message.text:
			case "📃 Список": self.__SendFilesList(User)
			case "↩️ Назад": self.close(User)
			case _:

				if message.text in self.__Files:
					FilePath = self.__Files[message.text]

					if not os.path.exists(FilePath): 
						self._Bot.send_message(User.id, "Файл не найден.")

					else:
						try:
							self._Bot.send_document(
								chat_id = User.id,
								document = open(FilePath, "rb")
							)

						except Exception as ExceptionData: 
							self._Bot.send_message(
								chat_id = User.id,
								text = f"Не удалось отправить файл из-за следующей ошибки:\n\n{ExceptionData}"[:4096]
							)

	#==========================================================================================#
	# >>>>> СПЕЦИАЛЬНЫЕ ПУБЛИЧНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def set_files(self, files: dict[str, PathLike]):
		"""
		Задаёт словарь с определениями файлов.

		:param files: Словарь, в котором ключ – отображаемое название файла, а значение – путь к нему.
		:type files: dict[str, PathLike]
		"""

		self.__Files = files.copy()

		for Key in self.__Files:
			FilePath = self.__Files[Key]
			if not os.path.exists(FilePath): PrintWarning(f"File \"{FilePath}\" not found.", "TelegramBotAdminPanel:SM_Extraction")