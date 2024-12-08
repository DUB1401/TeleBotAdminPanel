from dublib.TelebotUtils import UserData

import xlsxwriter

def GenerateExtractFile(filename: str, users: list[UserData]):
	"""
	Генерирует файл выписки из статистики бота.
		filename – название файла;\n
		users – список пользователей.
	"""

	WorkBook = xlsxwriter.Workbook(filename)
	WorkSheet = WorkBook.add_worksheet("Пользователи")

	Bold = WorkBook.add_format({"bold": True})
	Red = WorkBook.add_format({"font_color": "red"})
	Green = WorkBook.add_format({"font_color": "green"})

	WorkSheet.write(0, 0, "№", Bold)
	WorkSheet.write(0, 1, "Username", Bold)
	WorkSheet.write(0, 2, "Phone number", Bold)
	WorkSheet.write(0, 3, "Premium", Bold)

	Number = 0

	for User in users:
		WorkSheet.write(Number + 1, 0, Number + 1)
		WorkSheet.write(Number + 1, 1, User.username)
		# WorkSheet.write(Number + 1, 3, User.phone_number)
		IsPremium = str(User.is_premium).lower()
		Format = Green if User.is_premium else Red
		WorkSheet.write(Number + 1, 3, IsPremium, Format)
		Number += 1

	WorkSheet.autofit()
	WorkBook.close()