# SM_Extraction
Данный модуль предназначается для выгрузки файлов с сервера через интерфейс бота. Необходимо помнить, что бот имеет лимит на отправку в 40 MB.

## Пример использования
```Python
from TeleBotAdminPanel import Panel, Modules

# Инициализация панели управления.
# ...

# Получение объекта модуля.
SM_Extraction: Modules.SM_Extraction = AdminPanel.get_module_object(Modules.SM_Extraction.__name__)
# Определение пар название-путь файла.
FILES = {
	"main": "main.py
}
# Установка файлов для выгрузки.
SM_Extraction.set_files(FILES)
```