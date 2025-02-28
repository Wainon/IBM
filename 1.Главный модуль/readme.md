# Главный модуль, написан на С++

ВАЖНО!!! Вся информация о моей части можно узнать при нажитии на мой ник.

## Рабтал на ним:
[Чакир Максим](https://github.com/t-chakir/KFU/tree/main/IBM-project)

# Сценарй 
Пользователь может находится в одном из состояний:

Неизвестный --(обращение к сервису)--> Анонимный --(вход)--> Авторизованный --(выход)--> Не известный.

<br/>

#### Приходит запрос к Главному модулю

Главный модуль предоставляет ряд эндпоинтов (маршрутов, *URL*) для каждого действия в системе.

1. Приходит запрос на *URL*;
2. Главный модуль проверяет наличие *JWT* токена доступа;
3. Если токена нет или он устарел или подпись не соответствует содержимому, отправляется ответ 401;
4. Если токен есть и подписан правильно, проверяется наличие в токене разрешение на выполнение действия запрошенного пользователем;
   - Если разрешения нет, то отправляется ответ 403;
   - Если разрешение есть выполняем запрос, получаем/создаём/меняем данные и отправляет ответ. Ответ зависит от запрошенного действия. Список действий и разрешений далее.

<br/>

#### Список действий и разрешений доступных в системе

Система предоставляет доступ к набору ресурсов. С каждым ресурсом можно выполнять определённый набор действий (классическое CRUD). Действие может быть разрешено по умолчанию или запрещено. Если действие запрещено по умолчанию, то можно получить к нему доступ при наличии соответствующего разрешения.

Одно действие может иметь несколько вариаций доступа по умолчанию. Например я могу посмотреть информацию о пользователе, если ID запрашиваемого пользователя совпадает с моим и не могу, если ID другой. Или я могу посмотреть список  студентов записанных на дисциплину, если ID преподавателя дисциплины совпадает с моим и т.п.

Перед выполнением любого действия в системе нужно проверить, есть ли у пользователя доступ по умолчанию или разрешение. Список разрешений пользователя формируется модулем авторизации и записывается в JWT токен доступа. Токен доступа подписывается модулем авторизации, чтобы можно было проверить его подлинность.

Пользователю не присваиваются разрешения по одному. Пользователь получает их группой в соответствии с ролями: Студент, Преподаватель и Админ. Пользователь может иметь одну или более ролей. Каждая роль имеет свой набор разрешений, по сути роли соответствует массив разрешений. Если хоть у одной роли пользователя присутствует разрешение, то пользователь его получает.

##### Ресурс: Пользователи

| Действие                                                    | Эффект                                                       | По умолчанию             | Разрешение            |
| ----------------------------------------------------------- | ------------------------------------------------------------ | ------------------------ | --------------------- |
| Посмотреть список пользователей                             | Возвращает массив содержащий ФИО и ID каждого пользователя зарегистрированного в системе | -                        | `user:list:read`      |
| Посмотреть информацию о пользователе (ФИО)                  | Возвращает ФИО пользователя по его ID                        | + О себе<br />+ О другом |                       |
| Изменить ФИО пользователя                                   | Заменяет ФИО пользователя на указанное по его ID             | + Себе<br />- Другому    | `user:fullName:write` |
| Посмотреть информацию о пользователе (курсы, оценки, тесты) | Возвращает список дисциплин, список тестов, список оценок пользователя по его ID. Возвращается только та информация которую запросили | + О себе<br />- О другом | `user:data:read`      |
| Посмотреть информацию о пользователе (роли)                 | Возвращает массив ролей пользователя по его ID               | - Свои<br />- Чужие      | `user:roles:read`     |
| Изменить роли пользователя                                  | Заменяет роли пользователя на указанные по его ID            | - Себе<br />- Другому    | `user:roles:write`    |
| Посмотреть заблокирован ли пользователь                     | Для пользователя с указанным ID возвращает значение показывающее заблокирован пользователь или нет | - О себе<br />- О другом | `user:block:read`     |
| Заблокировать/Разблокировать пользователя                   | Для пользователя запрещены все действия, даже те, которые разрешены по умолчанию. На любой запрос нужно отвечать кодом 418 | - Себя<br />- Другого    | `user:block:write`    |

##### Ресурс: Дисциплина

| Действие                                                     | Эффект                                                       | По умолчанию                                                 | Разрешение          |
| ------------------------------------------------------------ | ------------------------------------------------------------ | ------------------------------------------------------------ | ------------------- |
| Посмотреть список дисциплин                                  | Возвращает массив содержащий Название, Описание и ID каждой дисциплины зарегистрированной в системе | +                                                            |                     |
| Посмотреть информацию о дисциплине (Название, Описание, ID преподавателя) | Возвращает Название, Описание, ID преподавателя для дисциплины по её ID | +                                                            |                     |
| Изменить информацию о дисциплине (Название, Описание)        | Заменяет Название и(или) Описание дисциплины на указанные по её ID | + Для своей дисциплины<br />- Для чужих                      | `course:info:write` |
| Посмотреть информацию о дисциплине (Список тестов)           | Возвращает массив содержащий Название и ID для каждого теста присутствующего в дисциплине по её ID | + Для своей дисциплины<br />+ Для чужих, но если записан на неё<br />- Для чужих | `course:testList`   |
| Посмотреть информацию о тесте (Активный тест или нет)        | Для дисциплины с указанным ID и теста с указанным ID возвращает значение показывающее активен он или нет. Если тест НЕ активен, он отображается в списке, но пройти его нельзя | + Для своей дисциплины<br />+ Для чужих, но если записан на неё<br />- Для чужих | `course:test:read`  |
| Активировать/Деактивировать тест                             | Для дисциплины с указанным ID и теста с указанным ID устанавливает значение активности. Если тест установлен в состояние Не активный, все начатые попытки автоматически отмечаются завершёнными | + Для своей дисциплины<br />- Для чужих                      | `course:test:write` |
| Добавить тест в дисциплину                                   | Добавляет новый тест в дисциплину с ID новый тест с указанным названием, пустым списком вопросов и автором и возвращает ID теста. По умолчанию тест не активен. | + Для своей дисциплины<br />- Для чужих                      | `course:test:add`   |
| Удалить тест из дисциплины                                   | Отмечает тест как удалённый (реально ничего не удаляется). Все оценки перестают отображаться, но тоже не удаляются. | + Для своей дисциплины<br />- Для чужих                      | `course:test:del`   |
| Посмотреть информацию о дисциплине (Список студентов)        | Возвращает массив содержащий ID каждого студента записанного на дисциплину по её ID | + Для своей дисциплины<br />- Для чужих                      | `course:userList`   |
| Записать пользователя на дисциплину                          | Добавляет пользователя с указанным ID на дисциплину с указанным ID | + Себя<br />- Других                                         | `course:user:add`   |
| Отчислить пользователя с дисциплины                          | Отчисляет пользователя с указанным ID с дисциплины с указанным ID | + Себя<br />- Других                                         | `course:user:del`   |
| Создать дисциплину                                           | Создаёт дисциплину с указанным названием, описанием и преподавателем. Как результат возвращает её ID | -                                                            | `course:add`        |
| Удалить дисциплину                                           | Отмечает дисциплину как удалённую (реально ничего не удаляется). Все тесты и оценки перестают отображаться, но тоже не удаляются. | + Для своей дисциплины<br />- Для чужих                      | `course:del`        |

##### Ресурс: Вопросы

Для простоты считаем, что поддерживается только один тип вопросов - вопрос с выбором единственного правильного ответа.

| Действие                                                | Эффект                                                       | По умолчанию                                                 | Разрешение        |
| ------------------------------------------------------- | ------------------------------------------------------------ | ------------------------------------------------------------ | ----------------- |
| Посмотреть список вопросов                              | Возвращает массив содержащий Название вопроса, его версию и ID автора для каждого теста в системе. Если у вопроса есть несколько версий, показывается только последняя | +Свои<br />- Чужие                                           | `quest:list:read` |
| Посмотреть информацию о вопросе                         | Для указанного ID вопроса и версии возвращает Название, Текст вопроса, Варианты ответов, Номер правильного ответа | + Свои<br />+ Студент у которого есть попытка ответа содержащая этот вопрос<br />- Остальные | `quest:read`      |
| Изменить текст вопроса/ответов (создаётся новая версия) | Для указанного ID вопроса создаёт новую версию с заданным Названием, Тексом вопроса, Вариантами ответов, Номером правильного ответа | + Свои<br />- Чужие                                          | `quest:update`    |
| Создать вопрос                                          | Создаёт новый вопрос с заданным Названием, Тексом вопроса, Вариантами ответов, Номером правильного ответа. Версия вопроса 1. В качестве ответа возвращается ID вопроса | -                                                            | `quest:create`    |
| Удалить вопрос                                          | Если вопрос не используется в тестах (даже удалённых), то вопрос отмечается как удалённый (но реально не удаляется) | + Свой<br />- Чужой                                          | `quest:del`       |

##### Ресурс: Тесты

Тест состоит из `id`, id дисциплины, названия, массива идентификаторов вопросов и массива попыток, состояние теста (актив/не актив), существование теста (существует/удалён). 

| Действие                                       | Эффект                                                       | По умолчанию                                                 | Разрешение          |
| ---------------------------------------------- | ------------------------------------------------------------ | ------------------------------------------------------------ | ------------------- |
| Удалить вопрос из теста                        | Если у теста ещё не было попыток прохождения, то удаляет у теста с указанным ID вопрос с указанным ID | + Если пользователь преподаватель на курсе<br />- Для остальных | `test:quest:del`    |
| Добавить вопрос в тест                         | Если у теста ещё не было попыток прохождения, то добавляет в теста с указанным ID вопрос с указанным ID в последнюю позицию | + Если пользователь преподаватель на курсе и автор вопроса<br />- Для остальных | `test:quest:add`    |
| Изменить порядок следования вопросов в тесте   | Если у теста ещё не было попыток прохождения, то для теста с указанным ID устанавливает указанную последовательность вопросов | + Если пользователь преподаватель на курсе<br />- Для остальных | `test:quest:update` |
| Посмотреть список пользователей прошедших тест | Для теста с указанным ID выбирает все попытки и возвращает ID пользователей выполнивших эти попытки | + Если пользователь преподаватель на курсе<br />- Для остальных | `test:answer:read`  |
| Посмотреть оценку пользователя                 | Для теста с указанным ID выбирает все попытки и возвращает оценки и ID пользователей выполнивших эти попытки | + Если пользователь преподаватель на курсе<br />+ Если пользователь смотрит свою оценку<br />- Для остальных | `test:answer:read`  |
| Посмотреть ответы пользователя                 | Для теста с указанным ID выбирает все попытки и возвращает оценки и ID пользователей выполнивших эти попытки | + Если пользователь преподаватель на курсе<br />+ Если пользователь смотрит свои ответы<br />- Для остальных | `test:answer:read`  |

##### Ресурс: Попытка

Когда пользователь начинает проходить тест, для него автоматически создаётся попытка. Попытка всегда одна. Попытка состоит из id, id пользователя-владельца, идентификатора теста, массива идентификаторов вопросов и их версий, массива ответов, состояние попытки.

Во время создания попытки, выбирается самая последняя версия вопроса с указанным ID.

| Действие           | Эффект                                                       | По умолчанию                                                 | Разрешение         |
| ------------------ | ------------------------------------------------------------ | ------------------------------------------------------------ | ------------------ |
| Создать            | Если пользователь с ID ещё не отвечал на тест с ID и тест находится в активном состоянии, то создаётся новая попытка и возвращается её ID | + Если пользователь отвечающий на тест<br />- Для остальных  | нет                |
| Изменить           | Если тест находится в активном состоянии и пользователь ещё не закончил попытку, то для попытки с ID изменяет значение ответа с ID | + Если пользователь отвечающий на тест<br />- Для остальных  | нет                |
| Завершить попытку  | Если тест находится в активном состоянии и пользователь ещё не закончил попытку, то устанавливает попытку в состояние: завершено.<br />Если тест переключили в состояние не активный, то все попытки для него автоматически устанавливаются в состояние: завершено | + Если пользователь отвечающий на тест<br />- Для остальных  | нет                |
| Посмотреть попытку | Для пользователя с ID и теста с ID возвращается массив ответов и статус состояние попытки | + Если пользователь преподаватель на курсе<br />+ Если пользователь смотрит свои ответы<br />- Для остальных | `test:answer:read` |

##### Ресурс: Ответы

Ответ состоит из id, id вопроса и его версии, id попытки, числового поля для ответа.

| Действие   | Эффект                                                       | По умолчанию                                                 | Разрешение                                                   |
| ---------- | ------------------------------------------------------------ | ------------------------------------------------------------ | ------------------------------------------------------------ |
| Создать    | Для вопроса с ID создается ответ. Изначально ответ отмечается как `-1` (не определённый). | -                                                            | Нет разрешения. Ответ автоматически создаётся системой во время создания попытки для каждого вопроса. |
| Посмотреть | Возвращает ID вопроса, и индекс выбранного варианта ответа от 0. Значение `-1` - пользователь не дал ответ на вопрос. | + Если пользователь преподаватель на курсе<br />+ Если пользователь смотрит свои ответы<br />- Для остальных | `answer:read`                                                |
| Изменить   | Если попытка которой принадлежит ответ не завершена, то изменяет индекс варианта ответа на указанный. | + Если пользователь отвечающий на тест<br />- Для остальных  | `answer:update`                                              |
| Удалить    | Если попытка которой принадлежит ответ не завершена, то изменяет индекс варианта ответа на `-1`. | + Если пользователь отвечающий на тест<br />- Для остальных  | `answer:del`                                                 |
