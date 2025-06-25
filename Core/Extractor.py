from dublib.TelebotUtils import UserData

from dataclasses import dataclass
from typing import Callable
import enum

import xlsxwriter

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

class Extractor:
	"""Генератор Excel-выписки."""

	#==========================================================================================#
	# >>>>> СТАТИЧЕСКИЕ АТРИБУТЫ <<<<< #
	#==========================================================================================#

	Columns: dict[str, Callable] = {
		"Username": ColumnsMethods.get_username,
		"Premium": ColumnsMethods.get_premium,
		"Chat Forbidden": ColumnsMethods.get_chat_forbidden
	}

	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def generate_file(self, filename: str, users: list[UserData]):
		"""
		Генерирует файл выписки из статистики бота.
			filename – название файла;\n
			users – список пользователей.
		"""

		WorkBook = xlsxwriter.Workbook(filename)
		WorkSheet = WorkBook.add_worksheet("Пользователи")

		StylesDeterminations = {
			Styles.Bold: WorkBook.add_format(Styles.Bold.value),
			Styles.Red: WorkBook.add_format(Styles.Red.value),
			Styles.Green: WorkBook.add_format(Styles.Green.value),
			None: None
		}

		for ColumnIndex in range(len(self.Columns.keys())):
			WorkSheet.write(0, ColumnIndex, tuple(self.Columns.keys())[ColumnIndex], StylesDeterminations[Styles.Bold])

		Number = 0

		for User in users:
			Generators: tuple[Callable] = tuple(self.Columns.values())

			for ColumnIndex in range(len(self.Columns.keys())):
				Cell: CellData = Generators[ColumnIndex](User)
				WorkSheet.write(Number + 1, ColumnIndex, Cell.value, StylesDeterminations[Cell.style])

			Number += 1

		WorkSheet.autofit()
		WorkBook.close()