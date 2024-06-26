# Pipisa Plus

Телеграм бот - расширенная версия бота Pipisa Bot (или просто пародия на него). Создан с целью поржать.

Текущая версия: 0.9

Для широкой аудитории пока не доступен.

Список изменений:
------------------------------------------------------------------------------------------------------------------------------
Версия 0.9 (Ban Update)
------------------------------------------------------------------------------------------------------------------------------
- Админы теперь могут блокировать игроков.
- Измерения теперь работают только в группах (возможность играть в личных сообщениях отключена).
- Изменены следующие характеристики измерений:
  - Удалены следующие измерения:
    - "Утка";
    - "Рост";
    - "Длина карандаша".
  - Изменены:
    - "Длина плохого кода":
      - Минимальный прирост - -5 см;
      - Максимальный прирост - 23 см;
      - Частота изменения (в часах) - 8.
- Добавление функционала для Админов.
- Переход базы данных на sql.
------------------------------------------------------------------------------------------------------------------------------
Версия 0.8.2
------------------------------------------------------------------------------------------------------------------------------
- Незначительные изменения реплик, отправляемых ботом.
- Время попыток изменения измерений теперь считается по Москве.
------------------------------------------------------------------------------------------------------------------------------
Версия 0.8.1
------------------------------------------------------------------------------------------------------------------------------
- Незначительные изменения реплик, отправляемых ботом (добавлены эмодзи).
- Исправлен номер версии бота в модуле конфигурации.
- Данные о прогрессе игроков перенесены в папку database.
- Добавление функционала для Админов.
- Исправление багов.
------------------------------------------------------------------------------------------------------------------------------
Версия 0.8 (Promocodes Update)
------------------------------------------------------------------------------------------------------------------------------
- Добавлена поддержка промокодов.
- - В личных сообщениях с ботом игроки могут применить промокод через команду "/promo (промокод) (ID группы)", указав группу, о которой есть информация в базе данных бота (группа заносится в базу данных, если в ней ботом пользовался хотя бы 1 человек). Промокод применяется к текущему измерению игрока в этой группе.
- - Каждый игрок может применить промокод столько раз, сколько указано в описании промокода. Использования промокода считаются отдельно для каждой группы.
- - Промокоды являются универсальными - их можно применить к любому измерению.
- Добавлены роли для игроков.
- - Игрокам с ролью "Тестировщик" доступны промокоды, недоступные остальным игрокам и являющиеся наградой за участие в тестировании бота.
- - Игроки с ролью "Админ" обладают привилегиями "Тестировщиков" и могут добавлять новые промокоды в базу данных бота в личных сообщениях с ботом, а также изменять роли других участников.
- Добавлена возможность узнать некоторую информацию о себе и о группах, в которых есть бот:
- - Узнать свою роль и ее возможности можно в личных сообщениях с ботом, введя команду /my_role.
- - Узнать свой ID можно в личных сообщениях с ботом, введя команду /my_id. ID нужен для изменения ролей Админами.
- - Узнать ID группы можно в группах, введя команду /group_id. ID группы нужен для использования промокодов.
------------------------------------------------------------------------------------------------------------------------------
Версия 0.7 (Picture Fix Update)
------------------------------------------------------------------------------------------------------------------------------
- При составлении картинок теперь не учитываются игроки с нулевым или отрицательным измерением.
- Картинки теперь нельзя составить для измерений, не имеющих возможности положительного роста (пример такого измерения: длина карандаша).
------------------------------------------------------------------------------------------------------------------------------
Версия 0.6 (Frequency Update)
------------------------------------------------------------------------------------------------------------------------------
- Добавлены ограничения на частоту изменений (по умолчанию - 24 часа).
- Добавлены следующие характеристики по умолчанию:
- - Частота изменения (в часах) - 24.
- Изменены следующие характеристики измерений:
- - Измерение "Утка":
- - - Частота изменения (в часах) - 12.
- - Измерение "Длина карандаша":
- - - Частота изменения (в часах) - 1.
- - Измерение "Длина плохого кода":
- - - Частота изменения (в часах) - 12.
- Изменены реплики бота:
- - Добавлена реплика бота, оповещающая о слишком частых попытках изменения (в связи с новым функционалом, добавленным в 0.6);
- - Реплика бота с информацией дополнена сведениями о частоте изменения.
------------------------------------------------------------------------------------------------------------------------------
Версия 0.5 (Autosaves Update)
------------------------------------------------------------------------------------------------------------------------------
- Реализованы автосохранения вместо псевдоавтосохранений, описанных в версии 0.3.
- Изменены следующие характеристики измерений:
- - Измерение "Пенис":
- - - Минимальный прирост - -5 см;
- - Измерение "Утка":
- - - Минимальный прирост - -5 см.
- Изменены следующие характеристики по умолчанию:
- - Минимальный прирост - -5 см.
------------------------------------------------------------------------------------------------------------------------------
Версия 0.4 (Pictures Update)
------------------------------------------------------------------------------------------------------------------------------
- Добавлена база данных с названиями групп.
- Незначительный рефакторинг кода в связи с предыдущим пунктом.
- Реализована отправка картинки с топ-10 игроков по каждому измерению; добавлена команда для этого действия.
------------------------------------------------------------------------------------------------------------------------------
Версия 0.3 (Top 10 Update)
------------------------------------------------------------------------------------------------------------------------------
- Добавлены псевдоавтосохранения (что значит, что при каждом получении сообщения происходит сохранение, если после последнего сохранения прошло больше 5 минут).
- Изменено содержание команды "help".
- Изменена логика отправки сообщений.
- Добавлена возможность просмотра топ-10 игроков по каждому измерению.
- Бот перенесен на aiogram 3.2.0.
------------------------------------------------------------------------------------------------------------------------------
Версия 0.2 (Backend Update)
------------------------------------------------------------------------------------------------------------------------------
- Реализованы бэкенд и работа с базой данных на json. 
- Добавлены некоторые команды во фронтенде.
- Исправлено поведение бота: теперь он отвечает только на адресованные ему команды.
------------------------------------------------------------------------------------------------------------------------------
Версия 0.1 (Frontend Update)
------------------------------------------------------------------------------------------------------------------------------
Создан основной фронтенд бота (ответы на команды). Бэкенда нет.
