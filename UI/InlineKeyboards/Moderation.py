from ...Core.Moderation import ModeratorsStorage

from dublib.TelebotUtils.Users import UsersManager
from dublib.TelebotUtils.Master import TeleMaster

from telebot import TeleBot, types

class ModerationInlineKeyboards:
	"""Шаблоны Inline-интерфейсов."""

	def moderation_start(name: str):
		"""
		Строит Inline-интерфейс: запуск модерации.

		:param name: Имя модератора.
		:type name: str
		"""

		Menu = types.InlineKeyboardMarkup()
		Moderator = ModeratorsStorage.get_moderator_by_name(name)
		Index = ModeratorsStorage.get_index_by_name(name)

		if Moderator.items_count:
			Start = types.InlineKeyboardButton("Приступить", callback_data = f"ap_moderation_start_{Index}")
			Menu.add(Start)
		
		Close = types.InlineKeyboardButton("Закрыть", callback_data = "ap_delete")
		Menu.add(Close)

		return Menu
	
	def moderation_item(index: int):
		"""
		Строит Inline-интерфейс: модерация контента.

		:param index: Индекс модератора.
		:type index: int
		"""

		Menu = types.InlineKeyboardMarkup()
		Good = types.InlineKeyboardButton("✅ Одобрить", callback_data = f"ap_moderate_{index}_true")
		Bad = types.InlineKeyboardButton("❌ Отклонить", callback_data = f"ap_moderate_{index}_false")
		Edit = types.InlineKeyboardButton("✏️ Исправить", callback_data = f"ap_edit_{index}")
		Close = types.InlineKeyboardButton("Закрыть", callback_data = f"ap_delete")
		Menu.add(Good, Bad, row_width = 2)
		Menu.add(Edit, Close, row_width = 1)

		return Menu
		
def ModerationInlineDecorators(bot: TeleBot, users: UsersManager):
	"""
	Набор декораторов: Inline-кнопки модерации.
		bot – экземпляр бота;\n
		users – менеджер пользователей.
	"""

	@bot.callback_query_handler(func = lambda Callback: Callback.data.startswith("ap_moderation_start"))
	def ModerationStart(Call: types.CallbackQuery):
		TeleMaster(bot).safely_delete_messages(Call.message.chat.id, Call.message.id)
		ModeratorIndex = int(Call.data[20:])
		Moderator = ModeratorsStorage.get_moderator_by_index(ModeratorIndex)

		bot.send_message(
			chat_id = Call.message.chat.id,
			text = Moderator.first_item,
			parse_mode = "HTML",
			reply_markup = ModerationInlineKeyboards.moderation_item(ModeratorIndex)
		)

	@bot.callback_query_handler(func = lambda Callback: Callback.data.startswith("ap_moderate"))
	def Moderate(Call: types.CallbackQuery):
		TeleMaster(bot).safely_delete_messages(Call.message.chat.id, Call.message.id)

		Value = Call.message.text
		Index, Status,  = Call.data[12:].split("_")
		Index, Status = int(Index), Status == "true"

		Moderator = ModeratorsStorage.get_moderator_by_index(Index)
		Moderator.catch(Value, Status)

		if Moderator.items_count: bot.send_message(
			chat_id = Call.message.chat.id,
			text = Moderator.first_item,
			parse_mode = "HTML",
			reply_markup = ModerationInlineKeyboards.moderation_item(Index)
		)
			
		else: bot.send_message(
			chat_id = Call.message.chat.id,
			text = "Вы завершили модерацию всех доступных записей."
		)