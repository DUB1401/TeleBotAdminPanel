# SM_Moderation
Данный модуль используется для модерации контента, например комментариев или сообщений обратной связи. Имеет два режима:

1. **Editable** – контент можно просмотреть, одобрить или отклонить, а также изменить.
2. **View** – весь контент можно только просматривать и перемещаться между элементами.

Для манипуляции очередями необходимо взаимодействовать с полученными при создании модераторов хранилищами.

## Пример использования
```Python
from TeleBotAdminPanel.Modules.Moderation import ModeratorsModes
from TeleBotAdminPanel import Panel, Modules

# Инициализация панели управления.
# ...

# Получение объекта модуля.
SM_Moderation: Modules.SM_Moderation = AdminPanel.get_module_object(Modules.SM_Moderation.__name__)

# Создание модератора комментариев, позволяющего изменять контент.
comments = SM_Moderation.add_moderator("comments", "Комментарии", ModeratorsModes.Editable)
# Добавление комментария в очередь модерации.
comments.append("Новый комментарий.")

# Создание модератора отчётов для управляемого просмотра.
reports = SM_Moderation.add_moderator("reports", "Отчёты", ModeratorsModes.View, print)
# Добавление отчёта в очередь просмотра.
reports.append("Новый отчёт.")
```