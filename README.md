# TeleBotAdminPanel
**TeleBotAdminPanel** – это легко встраиваемая панель администрирования для ботов Telegram, использующих [pyTelegramBotAPI](https://github.com/eternnoir/pyTelegramBotAPI?ysclid=m4fkp3hare559827384) и [dublib](https://github.com/DUB1401/dublib).

**Основные возможности:**
* просмотр статистики по пользователям;
* выгрузка списка пользователей в формат _*.xlsx_ (файл совместим со [SpamBot](https://github.com/DUB1401/SpamBot));
* рассылка сообщения пользователям бота, поддерживающая множество типов вложений.

## Порядок установки и использования
Панель управления распространяется как импортируемый модуль, который можно быстро интегрировать в ваш проект в качестве подмодуля Git.
1. Открыть каталог со скриптом в консоли: можно воспользоваться командой `cd` или встроенными возможностями файлового менеджера.
2. Добавьте подмодуль Git.
```Bash
# Добавляет последний commit в качестве подмодуля. 
# PATH указывает, куда расположить подмодуль. По умолчанию TeleBotAdminPanel.
git submodule add https://github.com/DUB1401/TeleBotAdminPanel.git {PATH}
```
3. Встройте декораторы и процедуры в необходимые места внутри обработчиков вашего бота (см. [подробнее](#структура)).
4. Выполните commit для фиксации подмодуля.
5. Если всё настроено верно, то после выгрузки репозитория в удалённое хранилище в последнем дожен появиться каталог-ссылка подмодуля.

## Структура
Вся панель представлена одним классом, собирающим в себе требующие компоненты. Для удобства выделяются следующие понятия:

**Декораторы** – наборы декораторов Python, фильтрующих определённые типы сигналов от пользователя и обрабатывающего их.

**Процедуры** – методы-инъекции, выполняющиеся внутри ваших собственных декораторов. Как правило, возвращают логическое значение, свидетельствующее о том, предназначалось ли сообщение для процедуры или же нужно продолжить его обработку вашими силами.

### Пример инициализации
```Python
from TeleBotAdminPanel.Core.Moderation import Moderator
from TeleBotAdminPanel import Panel

# Требуемые значения.
TOKEN = ""
ADMIN_PASSWORD = "1234"

# Инициализация необходимых объектов.
Bot = TeleBot(TOKEN)
Users = UsersManager("Data/Users")
AdminPanel = Panel()

# Опциональное включение модуля модерации контента.
Moderator.initialize(lambda: ["Unmoderated content."], print)

# Поместить в секцию обработки команд бота.
AdminPanel.decorators.commands(Bot, Users, ADMIN_PASSWORD)

# Обработка текстовых сообщений.
@Bot.message_handler(content_types = ["text"])
def Text(Message: types.Message):
	User = Users.auth(Message.from_user)
	# Если процедура сработала, прервать обработку.
	if AdminPanel.procedures.text(Bot, Users, Message): return

# Поместить в секцию обработки Inline-кнопок бота.
# Все Callback-запросы начинаются с "ap_".
AdminPanel.decorators.inline_keyboards(Bot, Users)

# Поместить в секцию обработки вложений.
AdminPanel.decorators.photo(Bot, Users)

# Обработка вложений.
@Bot.message_handler(content_types = ["audio", "document", "video"])
def File(Message: types.Message):
	User = Users.auth(Message.from_user)
	# Если процедура сработала, прервать обработку.
	if AdminPanel.procedures.files(Bot, User, Message): return
```
