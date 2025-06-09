from ...Core.Uploading import Uploader

from dublib.TelebotUtils.Users import UsersManager
from dublib.TelebotUtils.Master import TeleMaster

from pathlib import Path

from telebot import TeleBot, types

class UploadingInlineKeyboards:
	"""Шаблоны Inline-интерфейсов."""
	
	def files():
		"""Строит Inline-интерфейс: список файлов."""

		Menu = types.InlineKeyboardMarkup()
		Buffer = list()

		for Index in range(len(Uploader.FILES)):
			ObjectPath = Path(Uploader.FILES[Index])
			Buffer.append(types.InlineKeyboardButton(ObjectPath.name, callback_data = f"upload_{Index}"))

		Menu.add(*Buffer, row_width = 1)

		return Menu
		
def UploadingInlineDecorators(bot: TeleBot, users: UsersManager):
	"""
	Набор декораторов: Inline-кнопки выгрузки.
		bot – экземпляр бота;\n
		users – менеджер пользователей.
	"""

	@bot.callback_query_handler(func = lambda Callback: Callback.data.startswith("upload_"))
	def Upload(Call: types.CallbackQuery):
		TeleMaster(bot).safely_delete_messages(Call.message.chat.id, Call.message.id)
		Index = int(Call.data[7:])
		ObjectPath = Path(Uploader.FILES[Index])
		bot.send_chat_action(Call.message.chat.id, "typing")
		
		if ObjectPath.exists(): bot.send_document(Call.message.chat.id, types.InputFile(ObjectPath.as_posix()),)
		else: bot.send_message(Call.message.chat.id, "Файл не найден.")