from typing import Callable

class Moderator:
	"""Обработчик модерации контента."""

	#==========================================================================================#
	# >>>>> СТАТИЧЕСКИЕ АТРИБУТЫ <<<<< #
	#==========================================================================================#

	ENABLED: bool = False
	CONTENT_GETTER: Callable = None
	CALLBACK: Callable = None

	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def get_content_item() -> str | None:
		"""
		Возвращает первую модерируемую строку из последовательности.

		:return: Модерируемая строка или `None` в случае пустой последовательности.
		:rtype: str | None
		"""

		Content = Moderator.CONTENT_GETTER()
		if Content: return Content[0]

	def get_content_length() -> int:
		"""
		Возвращает длину последовательности модерируемых строк.

		:return: Длина последовательности.
		:rtype: int
		"""

		if not Moderator.CONTENT_GETTER: return
		
		return len(Moderator.CONTENT_GETTER())

	def initialize(content_getter: Callable, callback: Callable):
		"""
		Инициализирует модуль модерации.

		:param content_getter: Функция, возвращающая итерируемую последовательность модерируемых строк.
		:type content_getter: Callable
		:param callback: Функция, в которую будет передан результат модерации в качестве двух аргументов: модерируемого текста `str` и статуса модерации `bool`.
		:type callback: Callable
		"""

		#---> Проверка переданных аргументов.
		#==========================================================================================#
		Moderator.ENABLED = True
		Moderator.CONTENT_GETTER = content_getter
		Moderator.CALLBACK = callback

	def is_enabled() -> bool:
		"""
		Возвращает статус активации модуля модерации.

		:return: Если модуль инициализирован, возвращает `True`.
		:rtype: bool
		"""

		return Moderator.ENABLED

	def moderate(value: str, status: bool):
		"""
		Отправляет результат модерации контента в Callback-функцию.

		:param value: Модерируемый текст.
		:type value: str
		:param status: Статус модерации.
		:type status: bool
		"""

		Moderator.CALLBACK(value, status)