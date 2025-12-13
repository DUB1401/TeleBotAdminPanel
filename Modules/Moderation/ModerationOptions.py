from ...Core.PanelOptions import PanelOptions

from typing import TYPE_CHECKING

if TYPE_CHECKING:
	from dublib.TelebotUtils.Users import UserData

class ModerationOptions:
	"""Параметры модуля модерации."""

	#==========================================================================================#
	# >>>>> СВОЙСТВА <<<<< #
	#==========================================================================================#

	@property
	def canvas_id(self) -> int | None:
		"""ID текущего сообщения с отображением элемента."""

		return self.__Data["canvas_id"]

	@property
	def current_moderator(self) -> str | None:
		"""Текущий модератор."""

		return self.__Data["current_moderator"]
	
	@property
	def value(self) -> str | None:
		"""Данные, находящиеся на модерации."""

		return self.__Data["value"]

	#==========================================================================================#
	# >>>>> ПРИВАТНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __ParseData(self):
		"""Проверяет валидность опций."""

		Data = self.__PanelOptions.get_module_data("SM_Moderation")

		for Key in self.__Data.keys():
			if Key not in Data: Data[Key] = self.__Data[Key]

		self.__Data = Data

	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __init__(self, user: "UserData"):
		"""
		Параметры модуля модерации.

		:param user: Данные пользователя.
		:type user: UserData
		"""

		self.__PanelOptions = PanelOptions(user)
		self.__Data = {
			"current_moderator": None,
			"value": None,
			"canvas_id": None
		}

		self.__ParseData()

	def drop(self):
		"""Сбрасывает все значения данных."""

		for Key in self.__Data: self.__Data[Key] = None
		self.save()

	def save(self):
		"""Сохраняет данные модуля."""

		self.__PanelOptions.set_module_data("SM_Moderation", self.__Data)

	def set_canvas_id(self, id: int | None):
		"""
		Задаёт ID изменяемого сообщения.

		:param id: ID сообщения.
		:type id: int | None
		"""

		self.__Data["canvas_id"] = id
		self.save()

	def set_current_moderator(self, moderator: str | None):
		"""
		Задаёт текущий модератор.

		:param moderator: Идентификатор текущего модератора.
		:type moderator: str | None
		"""

		self.__Data["current_moderator"] = moderator
		self.save()

	def set_value(self, value: str | None):
		"""
		Задаёт модерируемое значение.

		:param value: Модерируемое значение.
		:type value: str | None
		"""

		self.__Data["value"] = value
		self.save()