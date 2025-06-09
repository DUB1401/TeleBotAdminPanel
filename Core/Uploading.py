from dublib.Methods.Data import ToIterable

from typing import Iterable
from os import PathLike

class Uploader:
	"""Оператор выгрузки файлов."""

	#==========================================================================================#
	# >>>>> СТАТИЧЕСКИЕ АТРИБУТЫ <<<<< #
	#==========================================================================================#

	FILES: list[PathLike] = list()

	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def set_uploadable_files(files: Iterable[PathLike] | PathLike):
		"""
		Задаёт пути к выгружаемым файлам.

		:param files: Один или несколько путей к файлам.
		:type files: Iterable[PathLike] | PathLike
		"""

		Uploader.FILES = ToIterable(files, iterable_type = list)