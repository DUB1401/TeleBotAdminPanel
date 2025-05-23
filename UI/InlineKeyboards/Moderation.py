from ...Core.Moderation import Moderator

from dublib.TelebotUtils.Users import UsersManager
from dublib.TelebotUtils.Master import TeleMaster

from telebot import TeleBot, types

class ModerationInlineKeyboards:
	"""Шаблоны Inline-интерфейсов."""

	def moderation_start():
		"""Строит Inline-интерфейс: запуск модерации."""

		Menu = types.InlineKeyboardMarkup()

		if Moderator.get_content_length():
			Start = types.InlineKeyboardButton("Приступить", callback_data = "ap_moderation_start")
			Menu.add(Start)
		
		Close = types.InlineKeyboardButton("Закрыть", callback_data = "ap_delete")
		Menu.add(Close)

		return Menu
	
	def moderation_item():
		"""Строит Inline-интерфейс: модерация контента."""

		Menu = types.InlineKeyboardMarkup()
		Good = types.InlineKeyboardButton("✅ Одобрить", callback_data = "ap_moderate_true")
		Bad = types.InlineKeyboardButton("❌ Отклонить", callback_data = "ap_moderate_false")
		Menu.add(Good, Bad, row_width = 2)

		return Menu
		
def ModerationInlineDecorators(bot: TeleBot, users: UsersManager):
	"""
	Набор декораторов: Inline-кнопки модерации.
		bot – экземпляр бота;\n
		users – менеджер пользователей.
	"""

	@bot.callback_query_handler(func = lambda Callback: Callback.data == "ap_moderation_start")
	def ModerationStart(Call: types.CallbackQuery):
		TeleMaster(bot).safely_delete_messages(Call.message.chat.id, Call.message.id)

		bot.send_message(
			chat_id = Call.message.chat.id,
			text = Moderator.get_content_item(),
			parse_mode = "HTML",
			reply_markup = ModerationInlineKeyboards.moderation_item()
		)

	@bot.callback_query_handler(func = lambda Callback: Callback.data.startswith("ap_moderate"))
	def Moderate(Call: types.CallbackQuery):
		TeleMaster(bot).safely_delete_messages(Call.message.chat.id, Call.message.id)

		Value = Call.message.text
		Status = Call.data[12:] == "true"

		Moderator.moderate(Value, Status)
		NewItem = Moderator.get_content_item()

		if NewItem: bot.send_message(
			chat_id = Call.message.chat.id,
			text = NewItem,
			parse_mode = "HTML",
			reply_markup = ModerationInlineKeyboards.moderation_item()
		)
			
		else: bot.send_message(
			chat_id = Call.message.chat.id,
			text = "Вы завершили модерацию всех доступных записей."
		)