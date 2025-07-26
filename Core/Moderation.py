from dublib.CLI.TextStyler import FastStyler

from typing import Callable

class ModeratorsStorage:
	"""Хранилище модераторов контента."""

	MODERATORS: dict[str, "Moderator"] = dict()

	@staticmethod
	def add_moderator(moderator: "Moderator", name: str):
		"""
		Регистрирует обработчик модерации.

		:param moderator: Модератор контента.
		:type moderator: Moderator
		:param name: Имя модератора.
		:type name: str
		"""

		ModeratorsStorage.MODERATORS[name] = moderator

	@staticmethod
	def get_names() -> tuple[str]:
		"""
		Возвращает имена модераторов.

		:return: Последовательность имён модераторов.
		:rtype: tuple[str]
		"""

		return tuple(ModeratorsStorage.MODERATORS.keys())
	
	@staticmethod
	def get_moderator_by_index(index: int) -> "Moderator":
		"""
		Возвращает модератор по его индексу.

		:param index: Индекс модератора.
		:type index: int
		:raise IndexError: Выбрасывается при отсутствии модератора с указанным индексом.
		:return: Обработчик модерации контента.
		:rtype: Moderator
		"""

		return tuple(ModeratorsStorage.MODERATORS.values())[index]
	
	@staticmethod
	def get_moderator_by_name(name: str) -> "Moderator":
		"""
		Возвращает модератор по его индексу.

		:param index: Индекс модератора.
		:type index: str
		:raise KeyError: Выбрасывается при отсутствии модератора с указанным именем.
		:return: Обработчик модерации контента.
		:rtype: Moderator
		"""

		return ModeratorsStorage.MODERATORS[name]
	
	@staticmethod
	def get_index_by_name(name: str) -> int:
		"""
		Возвращает индекс модератора по его имени.

		:param name: Имя модератора.
		:type name: str
		:return: Индекс модератора.
		:rtype: int
		"""

		return list(ModeratorsStorage.MODERATORS.keys()).index(name)
	
class Moderator:
	"""Обработчик модерации контента."""

	#==========================================================================================#
	# >>>>> СВОЙСТВА <<<<< #
	#==========================================================================================#

	@property
	def items_count(self) -> int:
		"""Количество строк в очереди на модерацию."""

		return len(self.__ContentGetter())

	@property
	def first_item(self) -> str | None:
		"""Первая строка из очереди модерации."""

		try: return self.__ContentGetter()[0]
		except IndexError: pass

	#==========================================================================================#
	# >>>>> ПРИВАТНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __PrintModeration(self, value: str, status: bool, edited_value: str | None = None):
		"""
		Выводит результат модерации в консоль.

		:param value: Модерируемая строка.
		:type value: str
		:param status: Статус модерации.
		:type status: bool
		:param edited_value: Новое значение, если оригинальное модерировалось.
		:type edited_value: str | None
		"""

		print(FastStyler("Value:").decorate.bold, value)

		print(FastStyler("Edited value:").decorate.bold, FastStyler(edited_value).decorate.italic if edited_value else FastStyler("false").colorize.red)

		StatusString = str(status).lower()
		print(FastStyler("Moderation status:").decorate.bold, FastStyler(StatusString).colorize.green if status else FastStyler(StatusString).colorize.red)
	
	#==========================================================================================#
	# >>>>> ПЕРЕОПРЕДЕЛЯЕМЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def _PostInitMethod(self):
		"""Метод, вызывающийся после инициализации объекта. Предназначен для переопределения."""

		pass

	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __init__(self, content_getter: Callable, callback: Callable | None = None, print: bool = False):
		"""
		Обработчик модерации контента.

		:param content_getter: Функция, возвращающая последовательность элементов для модерации.
		:type content_getter: Callable
		:param callback: Функция, в которую передаётся результат модерации в виде трёх параметров: `Union[str, bool, str]`. Оригинальная строка, статус модерации, отредактированная строка соответственно.
		:type callback: Callable | None
		:param print: Указывает, нужно ли выводить данные модерации в консоль.
		:type print: bool
		"""

		self.__ContentGetter = content_getter
		self.__Callback = callback
		self.__Print = print

		self._PostInitMethod()

	def catch(self, value: str, status: bool, edited_value: str | None = None):
		"""
		В этот метод передаётся результат модерации. Автоматически удаляет первый элемент из последовательности и вызывает `_ProcessModeration()` для дальнейшей обработки.

		:param value: Модерируемая строка.
		:type value: str
		:param status: Статус модерации.
		:type status: bool
		:param edited_value: Новое значение, если оригинальное модерировалось.
		:type edited_value: str | None
		"""

		if self.__Print: self.__PrintModeration(value, status, edited_value)
		if self.__Callback: self.__Callback(value, status, edited_value)