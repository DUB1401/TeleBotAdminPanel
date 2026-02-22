# SM_Switchers
Данный модуль предназначен управления глобальными логическими флагами-переключателями. Состояния флагов восстанавливаются при перезапуске.

## Пример использования
```Python
from TeleBotAdminPanel import Panel, Modules

from dublib.TelebotUtils import UserData

# Инициализация панели управления.
# ...

# Получение объекта модуля.
SM_Switchers: Modules.SM_Switchers = AdminPanel.get_module_object(Modules.SM_Switchers.__name__)
# Добавление флага. При существовании в системе флага с указанным ID операция игнорируется.
SM_Switchers.add_flag("subscription", "Подписка", True)

# Получение флага.
Flag = SM_Switchers.get_flag("subscription")
# Переключение состояния флага.
Flag.switch()
# Флаг интерпретируется как логическое значение.
if Flag: print(Flag.id)

# В других модулях проекта обращение к флагам возможно через статический атрибут.
from TeleBotAdminPanel.Modules.Switchers import SM_Switchers
# Получение флага из статического атрибута.
Flag = SM_Switchers.SWITCHERS["subscription"]
```