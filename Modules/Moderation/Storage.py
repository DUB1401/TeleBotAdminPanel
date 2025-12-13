from dublib.Methods.Filesystem import ReadJSON, WriteJSON

from os import PathLike
import os

from typing import TYPE_CHECKING

if TYPE_CHECKING:
	from ... import Panel

class Storage:
	"""Хранилище элементов, ожидающих модерации."""

	#==========================================================================================#
	# >>>>> СВОЙСТВА <<<<< #
	#==========================================================================================#

	@property
	def first_element(self) -> str | None:
		"""Первый элемент в очереди модерации."""

		return self.__Storage[0] if self.__Storage else None

	@property
	def id(self) -> str:
		"""Идентификатор модератора."""

		return self.__ID
	
	@property
	def elements(self) -> tuple[str]:
		"""Последовательность элементов для модерации."""

		return tuple(self.__Storage)

	#==========================================================================================#
	# >>>>> ЗАЩИЩЁННЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __Load(self) -> PathLike:
		"""
		Читает данные из существующего файла.

		:return: Путь к файлу-хранилищу элементов.
		:rtype: PathLike
		"""

		StorageDirectory = self.__Panel.get_module_workdir("SM_Moderation") + "/storages"
		StoragePath = f"{StorageDirectory}/{self.__ID}.json"
		os.makedirs(StorageDirectory, exist_ok = True)
		if os.path.exists(StoragePath): self._Storage = ReadJSON(StoragePath)

		return StoragePath
	
	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __init__(self, panel: "Panel", id: str):
		"""
		Оператор модерации контента.

		:param panel: Панель управления.
		:type panel: Panel
		:param id: Идентификатор модератора. Используется для общения и файловых операций.
		:type id: str
		"""

		self.__Panel = panel
		self.__ID = id

		self.__Storage: list[str] = list()
		self.__StoragePath = self.__Load()

	def append(self, content: str) -> bool:
		"""
		Добавляет контент в очередь на модерацию.

		:param content: Строка для модерации.
		:type content: str
		:return: Возвращает `False`, если элемент не добавлен в очередь, например из-за наличия такого же элемента.
		:rtype: bool
		"""

		if content in self.__Storage: return False
		self.__Storage.append(content)
		self.__Storage = list(set(self.__Storage))
		self.save()

		return True

	def get_element_with_offset(self, content: str, offset: int = 0) -> str | None:
		"""
		Возвращает элемент со сдвигом по отношению к переданному.

		:param content: Элемент, принимаемый за точку отсчёта.
		:type content: str
		:param offset: Сдвиг в положительную или отрицательную сторону. При указании `0` возвращает тот же элемент.
		:type offset: int
		:return: Целевой элемент. При выходе за пределы хранилища `None`.
		:rtype: str | None
		"""

		try:
			Index = self.__Storage.index(content)
			NewIndex = Index + offset
			if NewIndex < 0 or NewIndex > len(self._Storage) - 1: return
			return self.__Storage[NewIndex]
		
		except (ValueError, IndexError): pass

	def remove(self, content: str):
		"""Удаляет элемент из очереди модерации."""

		try: self.__Storage.remove(content)
		except ValueError: pass
		self.save()

	def replace(self, content: str, value: str) -> int | None:
		"""
		Заменяет элемент в очереди на модерацию.

		:param content: Искомое значение, которое будет заменено.
		:type content: str
		:param value: Новое значение.
		:type value: str
		:return: Индекс элемента в очереди или `None` при отсутствии искомого элемента.
		:rtype: int | None
		"""

		if content not in self.__Storage: return
		Index = self.__Storage.index(content)
		self.__Storage[Index] = value
		self.save()

		return Index

	def save(self):
		"""Сохраняет данные в локальный файл."""

		WriteJSON(self.__StoragePath, self.__Storage)