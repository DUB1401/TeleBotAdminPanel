# SM_Statistics
Данный модуль предназначен для получения краткой статистики о пользователях, а также способен предоставить Excel-файл с оной. Поддерживает настройку кастомных полей.

## Пример использования
```Python
from TeleBotAdminPanel.Modules.Statistics import CellData
from TeleBotAdminPanel import Panel, Modules

from dublib.TelebotUtils import UserData

# Инициализация панели управления.
# ...

# Реализация функции заполнения ячейки.
def get_age(user: UserData) -> CellData:
	Data = CellData()
	Data.value = user.get_property("age")
	
	return Data

# Получение объекта модуля.
SM_Statistics: Modules.SM_Statistics = AdminPanel.get_module_object(Modules.SM_Statistics.__name__)
# Установка метода для заполнения ячеек колонки "Age".
SM_Statistics.columns["Age"] = get_age
```