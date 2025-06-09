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

		return CellData(user.username)
	
	def get_name(user: UserData) -> CellData:
		"""
		Заполняет колонку: имя.
			user – данные пользователя.
		"""

		FirstName, LastName = None, None
		Name = str()

		try: FirstName = user.get_property("first_name")
		except KeyError: pass 
		try: LastName = user.get_property("last_name")
		except KeyError: pass 

		if FirstName: Name = FirstName
		if LastName: Name += " " + LastName
		
		return CellData(user.username)

	def get_premium(user: UserData) -> CellData:
		"""
		Заполняет колонку: Premium-статус.
			user – данные пользователя.
		"""

		Data = CellData()
		Data.value = str(user.is_premium).lower()
		Data.style = Styles.Green if user.is_premium else Styles.Red

		return Data
	
	def get_chat_forbidden(user: UserData) -> CellData:
		"""
		Заполняет колонку: заблокирован ли бот пользователем.
			user – данные пользователя.
		"""

		Data = CellData()
		if user.is_chat_forbidden == None: return Data

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

		WorkSheet.write(0, 0, "№", StylesDeterminations[Styles.Bold])

		for ColumnIndex in range(len(self.Columns.keys())):
			WorkSheet.write(0, ColumnIndex + 1, tuple(self.Columns.keys())[ColumnIndex], StylesDeterminations[Styles.Bold])

		Number = 0

		for User in users:
			Generators: tuple[Callable] = tuple(self.Columns.values())
			WorkSheet.write(Number + 1, 0, Number + 1)

			for ColumnIndex in range(len(self.Columns.keys())):
				Cell: CellData = Generators[ColumnIndex](User)
				WorkSheet.write(Number + 1, ColumnIndex + 1, Cell.value, StylesDeterminations[Cell.style])

			Number += 1

		WorkSheet.autofit()
		WorkBook.close()