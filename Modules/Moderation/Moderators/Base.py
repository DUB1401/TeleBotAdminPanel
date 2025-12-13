from typing import Callable, TYPE_CHECKING
from dataclasses import dataclass

if TYPE_CHECKING:
	from ..Storage import Storage
	from .... import Panel

	from dublib.TelebotUtils.Users import UserData

@dataclass
class ModerationSignal:
	value: str
	status: bool | None

class BaseModerator:
	"""Базовый модератор контента."""

	#==========================================================================================#
	# >>>>> СВОЙСТВА <<<<< #
	#==========================================================================================#

	@property
	def storage(self) -> "Storage":
		"""Хранилище очереди контента для модерации."""

		return self._Storage

	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __init__(self, panel: "Panel", storage: "Storage"):
		"""
		Базовый модератор контента.

		:param panel: Панель управления.
		:type panel: Panel
		:param storage: Хранилище элементов, ожидающих модерацию.
		:type storage: Storage
		"""

		self._Panel = panel
		self._Storage = storage

		self._Callback = None

		self._MasterBot = self._Panel.master_bot
		self._Bot = self._Panel.bot

	def emit_callback(self, value: str, status: bool | None = None):
		"""
		Испускает сигнал о модерации в callback-функцию и удаляет значение из хранилища.

		:param value: Отмодерированное значение.
		:type value: str
		:param status: Статус модерации.
		:type status: bool
		"""

		self._Storage.remove(value)
		if self._Callback: self._Callback(ModerationSignal(value, status))

	def set_callback(self, callback: Callable):
		"""
		Задаёт функцию или метод, в который передаётся результат модерации.

		:param callback: Функция или метод.
		:type callback: Callable
		"""

		self._Callback = callback

	def run(self, user: "UserData"):
		"""
		Запускает обработку очереди модерации.

		:param user: Пользователь, выполняющий обработку.
		:type user: UserData
		"""

		pass