# SM_Mailing
Данный модуль используется для рассылки сообщений с поддержкой вложений и кнопки перехода по ссылке. Способен приостанавливать процесс и автоматически обходить ошибки ограничения частоты запросов.

## Пример использования
```Python
from TeleBotAdminPanel.Modules.Moderation import ModeratorsModes
from TeleBotAdminPanel import Panel, Modules

# Инициализация панели управления.
# ...

# Получение объекта модуля.
SM_Mailing: Modules.SM_Mailing = AdminPanel.get_module_object(Modules.SM_Mailing.__name__)
# Настройка интервала между запросами на отправку сообщений. По умолчанию 0.5 секунды.
SM_Mailing.set_delay(1.0)
```