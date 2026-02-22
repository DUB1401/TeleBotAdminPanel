from urllib.parse import urlparse

def IsLinkValid(link: str) -> bool:
	"""
	Проверяет валдиность схемы ссылки.

	:param link: Проверяемая ссылка.
	:type link: str
	:return: Возвращает `True`, если схема ссылки валидна.
	:rtype: bool
	"""

	try:
		Result = urlparse(link)
		return all((Result.scheme, Result.netloc))
	
	except ValueError: return False