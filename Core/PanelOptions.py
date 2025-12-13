from dublib.TelebotUtils.Users import UserData
from dublib.Methods.Data import Copy, Zerotify

from typing import Any

class Path:
	"""Путь к слою в древе."""

	#==========================================================================================#
	# >>>>> СВОЙСТВА <<<<< #
	#==========================================================================================#

	@property
	def value(self) -> str | None:
		"""Значение пути."""

		return self.__Path

	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __init__(self, options: "PanelOptions", path: str | None):
		"""
		Путь к слою в древе.

		:param options: Параметры панели управления.
		:type options: PanelOptions
		:param path: Путь к слою.
		:type path: str | None
		"""

		self.__Options = options
		self.__Path: str | None = Zerotify(path)

	def __str__(self) -> str:
		"""Возвращает строковое представление пути."""

		return self.as_str()
	
	def append(self, catalog: str) -> str:
		"""
		Добавляет каталог к концу пути.

		:param catalog: Название каталога.
		:type catalog: str
		:return: Строковое представление пути.
		:rtype: str
		"""

		Path = self.as_str() + "/" + catalog
		self.__Path = Path.strip("/")

		return self.as_str()

	def as_str(self) -> str:
		"""Возвращает строковое представление пути."""

		return self.__Path or ""

	def up(self) -> str:
		"""
		Переводит путь на один уровень выше.

		:return: Строковое представление пути.
		:rtype: str
		"""

		if self.__Path:
			PathParts = self.__Path.split("/")

			if len(PathParts) > 1:
				PathParts = PathParts[:-1]
				self.__Path = "/".join(PathParts).strip("/")

			else: self.__Path = None

		self.__Options.save()

		return self.as_str()

class PanelOptions:
	"""Параметры панели управления."""

	#==========================================================================================#
	# >>>>> СВОЙСТВА <<<<< #
	#==========================================================================================#

	@property
	def is_open(self) -> bool:
		"""Состояние: открыта ли панель управления."""

		return self.__Data["is_open"]
	
	@property
	def current_module(self) -> str | None:
		"""Идентификатор текущего модуля."""

		return self.__Data["current_module"]
	
	@property
	def path(self) -> Path:
		"""Путь к слою в древе."""

		return self.__Data["path"]
	
	#==========================================================================================#
	# >>>>> ПРИВАТНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#
	
	def __ParseData(self):
		"""Парсит параметры и проверяет их валидность."""

		if self.__User.has_property("ap"):
			Data: dict[str, Any] = self.__User.get_property("ap")
			Edited = False

			for Key in self.__Data:

				if Key not in Data: 
					Data[Key] = self.__Data[Key]
					Edited = True

			Data["path"] = Path(self, Data["path"])
			self.__Data = Data
			if Edited: self.save()
			
		else: self.save()

	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __init__(self, user: UserData):
		"""
		Параметры обмена энергией пользователя.

		:param user: Данные пользователя.
		:type user: UserData
		"""

		self.__User = user

		self.__Data = {
			"is_open": False,
			"path": Path(self, None),
			
			"current_module": None,
			"modules_data": dict()
		}

		self.__ParseData()
		
	def save(self):
		"""Сохраняет параметры."""

		Buffer = self.__Data.copy()
		Buffer["path"] = Zerotify(Buffer["path"].as_str())

		self.__User.set_property("ap", Buffer)

	def set_current_module(self, module: str | None):
		"""
		Задаёт текущий модуль.

		:param module: Идентификатор модуля.
		:type module: str | None
		"""

		self.__Data["current_module"] = module
		self.save()

	def set_open_state(self, status: bool):
		"""
		Задаёт состояние: открыта ли панель управления.

		:param status: Состояние.
		:type status: bool
		"""

		self.__Data["is_open"] = status
		self.save()

	#==========================================================================================#
	# >>>>> МЕТОДЫ ОБНОВЛЕНИЯ ДАННЫХ МОДУЛЕЙ <<<<< #
	#==========================================================================================#

	def get_module_data(self, module: str) -> dict:
		"""
		Возвращает копию словаря данных модуля.

		:param module: Имя модуля.
		:type module: str
		:return: Копия словаря данных модуля.
		:rtype: dict
		"""

		if module not in self.__Data["modules_data"]:
			self.__Data["modules_data"][module] = dict()
			self.save()

		return Copy(self.__Data["modules_data"][module])
	
	def set_module_data(self, module: str, data: dict[str, Any]):
		"""
		Задаёт данные модуля.

		:param module: Имя модуля.
		:type module: str
		:param data: Данные модуля в формате словаря.
		:type data: dict[str, Any]
		:raise TypeError: Выбрасывается при указании данных не словарного типа.
		"""

		if type(data) != dict: raise TypeError("Dictionary required for data.")
		self.__Data["modules_data"][module] = Copy(data)
		self.save()