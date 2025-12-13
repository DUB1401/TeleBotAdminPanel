from . import InlineKeyboards, ReplyKeyboards
from ...Core.BaseModule import BaseModule

from typing import Callable, TYPE_CHECKING
from datetime import datetime
import os

from telebot import types
import xlsxwriter

from dublib.TelebotUtils import UserData

from dataclasses import dataclass
from typing import Callable
import enum

if TYPE_CHECKING:
	from dublib.TelebotUtils.Users import UserData

#==========================================================================================#
# >>>>> ВСПОМОГАТЕЛЬНЫЕ СТРУКТУРЫ ДАННЫХ <<<<< #
#==========================================================================================#

class Styles(enum.Enum):
	"""Стили содержимого ячеек."""

	Bold = {"bold": True}
	Green = {"font_color": "green"}
	Red = {"font_color": "red"}

@dataclass
class CellData:
	"""Данные ячейки."""

	value: str | None = None
	style: Styles | None = None

class ColumnsMethods:
	"""Контейнер методов заполнения колонок."""

	def get_username(user: UserData) -> CellData:
		"""
		Заполняет колонку: никнейм.
			user – данные пользователя.
		"""

		Data = CellData()
		if user.username: Data.value = user.username

		return Data

	def get_premium(user: UserData) -> CellData:
		"""
		Заполняет колонку: Premium-статус.
			user – данные пользователя.
		"""

		Data = CellData()

		if user.is_premium != None:
			Data.value = str(user.is_premium).lower()
			Data.style = Styles.Green if user.is_premium else Styles.Red

		return Data
	
	def get_chat_forbidden(user: UserData) -> CellData:
		"""
		Заполняет колонку: заблокирован ли бот пользователем.
			user – данные пользователя.
		"""

		Data = CellData()

		if user.is_chat_forbidden != None:
			Data.value = str(user.is_chat_forbidden).lower()
			Data.style = Styles.Red if user.is_chat_forbidden else Styles.Green

		return Data
	
#==========================================================================================#
# >>>>> ОСНОВНОЙ КЛАСС <<<<< #
#==========================================================================================#

class SM_Statistics(BaseModule):
	"""Модуль статистики."""

	#==========================================================================================#
	# >>>>> СВОЙСТВА <<<<< #
	#==========================================================================================#

	@property
	def columns(self) -> dict[str, Callable]:
		"""Определения колонок из пары: название и функция получения значения."""

		return self.__Columns

	#==========================================================================================#
	# >>>>> ПРИВАТНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __SendStatistics(self, user: "UserData"):

		UsersCount = len(self._Panel.users_manager.users)
		BlockedUsersCount = 0

		for user in  self._Panel.users_manager.users:
			if user.is_chat_forbidden: BlockedUsersCount += 1

		Counts = [len(self._Panel.users_manager.premium_users), len(self._Panel.users_manager.get_active_users()), BlockedUsersCount]
		Percentages = [None, None, None]

		for Index in range(len(Counts)):
			Percentages[Index] = round(Counts[Index] / UsersCount * 100, 1)
			if str(Percentages[Index]).endswith(".0"): Percentages[Index] = int(Percentages[Index])

		Text = (
			"<b>📊 Статистика</b>\n",
			f"👤 Всего пользователей: <b>{UsersCount}</b>",
			f"⭐ Из них Premium: <b>{Counts[0]}</b> (<i>{Percentages[0]}%</i>)",
			f"🧩 Активных за сутки: <b>{Counts[1]}</b> (<i>{Percentages[1]}%</i>)",
			f"⛔ Заблокировали: <b>{Counts[2]}</b> (<i>{Percentages[2]}%</i>)"
		)

		self._Panel.bot.send_message(
			chat_id = user.id,
			text = "\n".join(Text),
			parse_mode = "HTML",
			reply_markup = InlineKeyboards.Extract() 
		)

	def __GenerateFile(self, filename: str, users: list[UserData]):
		"""
		Генерирует файл выписки из статистики бота.

		:param filename: Имя файла.
		:type filename: str
		:param users: Список пользоваталей.
		:type users: list[UserData]
		"""

		WorkBook = xlsxwriter.Workbook(filename)
		WorkSheet = WorkBook.add_worksheet("Пользователи")

		StylesDeterminations = {
			Styles.Bold: WorkBook.add_format(Styles.Bold.value),
			Styles.Red: WorkBook.add_format(Styles.Red.value),
			Styles.Green: WorkBook.add_format(Styles.Green.value),
			None: None
		}

		for ColumnIndex in range(len(self.__Columns.keys())):
			WorkSheet.write(0, ColumnIndex, tuple(self.__Columns.keys())[ColumnIndex], StylesDeterminations[Styles.Bold])

		Number = 0

		for User in users:
			Generators: tuple[Callable] = tuple(self.__Columns.values())

			for ColumnIndex in range(len(self.__Columns.keys())):
				Cell: CellData = Generators[ColumnIndex](User)
				WorkSheet.write(Number + 1, ColumnIndex, Cell.value, StylesDeterminations[Cell.style])

			Number += 1

		WorkSheet.autofit()
		WorkBook.close()

	#==========================================================================================#
	# >>>>> ЗАЩИЩЁННЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def _PostInitMethod(self):
		"""Метод, выполняющийся после инициализации объекта."""

		self.__Columns: dict[str, Callable] = {
			"Username": ColumnsMethods.get_username,
			"Premium": ColumnsMethods.get_premium,
			"Chat Forbidden": ColumnsMethods.get_chat_forbidden
		}

	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ <<<<< #
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
			text = "Модуль статистики закрыт.",
			reply_markup = LayerMarkup
		)
		
	def open(self, user: "UserData"):
		"""
		Обрабатывает открытие модуля.

		:param user: Данные пользователя.
		:type user: UserData
		"""
		
		self._Panel.bot.send_message(
			chat_id = user.id,
			text = "Модуль статистики открыт.",
			reply_markup = ReplyKeyboards.Start()
		)

	def process_call(self, call: types.CallbackQuery):
		"""
		Обрабатывает вызов от пользователя.

		:param call: Данные вызова.
		:type call: types.CallbackQuery
		"""

		if call.data == "ap_extract":

			User = self._Panel.users_manager.auth(call.from_user)
			Date = datetime.now().date().strftime("%d.%m.%Y")
			Filename = self._Panel.get_module_workdir(SM_Statistics.__name__) + f"/{Date}.xlsx"
			self.__GenerateFile(Filename, self._Panel.users_manager.users)

			try:
				self._Panel.master_bot.safely_delete_messages(User.id, call.message.id)
				self._Panel.bot.send_document(
					chat_id = User.id,
					document = open(Filename, "rb"), 
					caption = f"Выписка из статистики бота за {Date}. Данный файл совместим с системой <a href=\"https://github.com/DUB1401/SpamBot\">SpamBot</a>.",
					parse_mode = "HTML"
				)
				os.remove(Filename)

			except Exception as ExceptionData: print(ExceptionData)

	def process_message(self, message: types.Message):
		"""
		Обрабатывает текстовое сообщение от пользователя.

		:param message: Данные сообщения.
		:type message: types.Message
		"""

		User = self._Panel.users_manager.auth(message.from_user)

		match message.text:
			case "📊 Отобразить": self.__SendStatistics(User)
			case "↩️ Назад": self.close(User)