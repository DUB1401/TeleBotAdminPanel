from typing import TYPE_CHECKING

if TYPE_CHECKING:
	from .PanelOptions import Path

class Tree:
	"""Древо навигации."""

	#==========================================================================================#
	# >>>>> СВОЙСТВА <<<<< #
	#==========================================================================================#

	@property
	def data(self) -> dict:
		"""Словарное представление древа навигации."""

		return self.__Tree
	
	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __init__(self):
		"""Древо навигации."""

		self.__Tree = dict()

	def get_layer_by_path(self, path: "Path") -> dict:
		"""
		Возвращает словарь слоя по пути.

		:param path: Путь к слою.
		:type path: Path
		:raises KeyError: Выбрасывается при ошибке перехода по пути.
		:raises TypeError: Выбрасывается при попытке получить модуль вместо слоя.
		:return: Словарь слоя.
		:rtype: dict
		"""

		path = path.value
		if not path: return self.__Tree

		Keys = path.value.split("/")
		Current = self.__Tree
		for Key in Keys: Current = Current[Key]
		if type(Current) != dict: raise TypeError("Path must point to dictionary.")
		
		return Current

	def set(self, tree: dict):
		"""
		Задаёт древо навигации.

		:param tree: Древо навигации.
		:type tree: dict
		"""

		self.__Tree = tree