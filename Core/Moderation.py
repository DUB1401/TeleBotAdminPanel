from dublib.CLI.TextStyler import FastStyler
from dublib.Methods.Data import ToIterable

from typing import Iterable

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

		return len(self.__Items)

	@property
	def first_item(self) -> str | None:
		"""Первая строка из очереди модерации."""

		return self.__Items[0] if self.__Items else None
	
	#==========================================================================================#
	# >>>>> ПЕРЕОПРЕДЕЛЯЕМЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def _PostInitMethod(self):
		"""Метод, вызывающийся после инициализации объекта. Предназначен для переопределения."""

		pass

	def _ProcessModeration(self, value: str, status: bool):
		"""
		Переопределите данный метод для обработки модерации. По умолчанию выводит результат модерации в консоль.

		:param value: Отмодерированная строка.
		:type value: str
		:param status: Статус модерации.
		:type status: bool
		"""

		print(FastStyler("Value:").decorate.bold, value)
		StatusString = str(status).lower()
		print(FastStyler("Moderation status:").decorate.bold, FastStyler(StatusString).colorize.green if status else FastStyler(StatusString).colorize.red)

	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __init__(self):
		"""Обработчик модерации контента."""

		self.__Items = list()

		self._PostInitMethod()

	def extend(self, items: Iterable[str] | str):
		"""
		Добавляет элементы в последовательность для модерации. Дубликаты удаляются.

		:param items: Несколько или один элемент для модерации.
		:type items: Iterable[str] | str
		"""

		self.__Items.extend(ToIterable(items))
		self.__Items = list(set(self.__Items))

	def catch(self, value: str, status: bool):
		"""
		В этот метод передаётся результат модерации. Автоматически удаляет первый элемент из последовательности и вызывает `_ProcessModeration()` для дальнейшей обработки.

		:param value: Отмодерированная строка.
		:type value: str
		:param status: Статус модерации.
		:type status: bool
		"""

		self.__Items.pop(0)
		self._ProcessModeration(value, status)