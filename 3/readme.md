# Telegram клиент, написан на Python 
## Рабтал на ним:
Тычинин Илья
# Сценарий 
Пользователь может находится в одном из состояний:
Неизвестный --(обращение к сервису)--> Анонимный --(вход)--> Авторизованный --(выход)--> Не известный.
<br/>
#### Пользователь обращается к системе через Telegram в первый раз или после выхода (неизвестный пользователь)
1. Пользователь через приложение Telegram отправляет сообщение (любое) на сервера Telegram;
2. Компонент *Telegram Client* обращается к серверам Telegram и получает список всех новых сообщений;
3. Компонент *Telegram Client* достаёт из списка новых сообщений наше (предполагается, что оно первое в списке) затем обрабатываются остальные;
4. Компонент *Telegram Client* проверяет сообщение пользователя на предусмотренное в боте.
5. Если мы не предусмотрели ответ на такое сообщение, то отвечаем:
   - Нет такой команды;
6. Если обработчик для сообщения пользователя найден, то *Telegram Client* перенаправляет запрос компоненту *Bot Logic* (перед ним сидит компонент *Nginx*);
7. *Nginx* перенаправляет запрос одной из рабочих копий компонента *Bot Logic*;
8. *Bot Logic* делает запрос к компоненту *Redis* используя `chat_id` в качестве ключа. `chat_id` присылается сервером Telegram вместе с сообщением пользователя. Он всегда одинаковый для пары пользователь-бот и позволяет однозначно идентифицировать пользователя;
9. *Redis* сообщает, что такого ключа нет;
10. Если обработчик `login` без параметров или любой другой:
    - *Bot Logic* формирует ответ сообщающий, что пользователь не заголинен и предлагающий пользователю авторизоваться через: GitHub, Яндекс ID или через код; Ответ уходит пользователю.
11. Если обработчик `login` с параметром `type`:
    - Генерируем новый токен входа;
    - Делаем запрос *Redis* чтобы он запомнил текущий `chat_id` как ключ, а в качестве значения: статус пользователя: Анонимный и токен входа;
    - *Bot Logic* делает запрос к модулю Авторизации (указывая токен входа);
    - Ждём ответа от модуль Авторизации и перенаправляем его пользователю.
#### Пользователь обращается к системе через Telegram (имея статус Анонимный)
1. Пользователь через приложение Telegram отправляет сообщение (любое) на сервера Telegram;
2. Компонент *Telegram Client* обращается к серверам Telegram и получает список всех новых сообщений;
3. Компонент *Telegram Client* достаёт из списка новых сообщений наше (предполагается, что оно первое в списке) затем обрабатываются остальные;
4. Компонент *Telegram Client* проверяет сообщение пользователя на предусмотренное в боте.
5. Если мы не предусмотрели ответ на такое сообщение, то отвечаем:
   - Нет такой команды;
6. Если обработчик для сообщения пользователя найден, то *Telegram Client* перенаправляет запрос компоненту *Bot Logic* (перед ним сидит компонент *Nginx*);
7. *Nginx* перенаправляет запрос одной из рабочих копий компонента *Bot Logic*;
8. *Bot Logic* делает запрос к компоненту *Redis* используя `chat_id` в качестве ключа. На этот раз он 100% есть, иначе продолжение по сценарию Неизвестного пользователя;
9. *Redis* сообщает, что такой ключ есть и присылает данные соответствующие ключу;
10. *Bot Logic* достаёт из ответа статус пользователя. Он равен: Анонимный;
11. Если обработчик `login` с параметром `type`:
    - Генерируем новый токен входа;
    - Делаем запрос *Redis* чтобы он заменил текущий токен входа на новый для ключа `chat_id`;
    - *Bot Logic* делает запрос к модулю Авторизации (указывая токен входа);
    - Ждём ответа от модуль Авторизации и перенаправляем его пользователю.
12. Если обработчик `login` без параметров или любой другой:
13. *Bot Logic* достаёт из ответа от *Redis* токен входа и делает запрос модулю Авторизации отправляя токен входа для проверки;
14. Модуль Авторизации проверяет есть ли у него запись для указанного токена входа и отвечает;
15. Если ответ от модуля Авторизации: не опознанный токен или время действия токена закончилось:
    - *Bot Logic* делает запрос *Redis*, чтобы тот удалил ключ `chat_id`. Пользователь переходит в статус Неизвестный;
    - *Bot Logic* формирует ответ сообщающий, что пользователь не заголинен и предлагающий пользователю авторизоваться через: GitHub, Яндекс ID или через код; Ответ уходит пользователю.
16. Если ответ от модуля Авторизации: в доступе отказано (пользователь нажал Нет во время входа):
    - *Bot Logic* делает запрос *Redis*, чтобы тот удалил ключ `chat_id`. Пользователь переходит в статус Неизвестный;
    - *Bot Logic* формирует ответ сообщающий: неудачная авторизация; Ответ уходит пользователю;
17. Если ответ от модуля Авторизации: доступ предоставлен (пользователь нажал Да во время входа), то:
    - *Bot Logic* проверяет, что в ответе от модуля авторизации присутствуют 2 *JWT* токена: токен доступа (*Access Token*) и токен обновления (*Refresh Token*);
    - Они присутствуют. *Bot Logic* меняет статус пользователя на Авторизованный и делает запрос *Redis* сохранить новый статус пользователя и оба *JWT* токена (токен входа больше не нужен). В качестве ключа используется `chat_id`;
    - *Bot Logic* продолжает обрабатывать текущий запрос пользователя так, как будто бы пользователь сразу был в статусе Авторизованный.
#### Пользователь обращается к системе через Telegram (имея статус Авторизованный)
1. Пользователь через приложение Telegram отправляет сообщение (любое) на сервера Telegram;
2. Компонент *Telegram Client* обращается к серверам Telegram и получает список всех новых сообщений;
3. Компонент *Telegram Client* достаёт из списка новых сообщений наше (предполагается, что оно первое в списке) затем обрабатываются остальные;
4. Компонент *Telegram Client* проверяет сообщение пользователя на предусмотренное в боте.
5. Если мы не предусмотрели ответ на такое сообщение, то отвечаем:
   - Нет такой команды;
6. Если обработчик для сообщения пользователя найден, то *Telegram Client* перенаправляет запрос компоненту *Bot Logic* (перед ним сидит компонент *Nginx*);
7. *Nginx* перенаправляет запрос одной из рабочих копий компонента *Bot Logic*;
8. *Bot Logic* делает запрос к компоненту *Redis* используя `chat_id` в качестве ключа. На этот раз он 100% есть, иначе продолжение по сценарию Неизвестного пользователя;
9. *Redis* сообщает, что такой ключ есть и присылает данные соответствующие ключу;
10. *Bot Logic* достаёт из ответа статус пользователя. Он равен: Авторизованный;
11. Если обработчик `login` не важно с параметром `type` или без, то *Bot Logic* формирует ответ сообщающий: вы уже авторизованы; Ответ уходит пользователю;
12. Если обработчик `logout` без параметров (выйти из системы на этом устройстве):
    - *Bot Logic* делает запрос к компоненту *Redis* и просит удалить ключ. В качестве ключа используется `chat_id`. Пользователь переходит в статус Неизвестный.
    - *Вot Logic* формирует ответ сообщающий: сеанс завершён; Ответ уходит пользователю;
13. Если обработчик `logout` с параметром `all=true` (выйти из системы на всех устройствах):
    - *Bot Logic* делает запрос к компоненту *Redis* и просит удалить ключ. В качестве ключа используется `chat_id`. Пользователь переходит в статус Неизвестный.
    - *Bot Logic* делает запрос к модулю Авторизации на `/logout` и отправляет ему токен обновления;
    - *Вot Logic* формирует ответ сообщающий: сеанс завершён на всех устройствах; Ответ уходит пользователю;
14. Если обработчик другой (самостоятельно назначить для каждого действия которое можно выполнить в системе):
    - *Вot Logic* делает соответствующий запрос к Главному модулю передавая токен доступа в заголовках запроса;
    - Если токен доступа не устарел и у пользователя есть право на выполнение действия:
      - Главный модуль обрабатывает запрос и отвечает данными;
      - *Вot Logic* формирует ответ на основе данных. Ответ уходит пользователю;
    - Если токен доступа не устарел, но у пользователя нет права на выполнение действия:
      - Главный модуль отвечает 403 кодом;
      - *Вot Logic* формирует ответ: не достаточно прав для этого действия. Ответ уходит пользователю;
    - Если токен доступа устарел:
      - Главный модуль отвечает 401 кодом;
      - *Вot Logic* формирует запрос к модулю Авторизации и отправляет токен обновления.
        - Если токен обновления устарел или не существует:
          - Модуль Авторизации отвечает 401 кодом и удаляет у себя устаревший токен;
          - *Вot Logic* отправляет запрос *Redis* и просит удалить указанный ключ. В качестве ключа используется `chat_id`. Пользователь переходит в статус Неизвестный;
          - *Bot Logic* формирует ответ сообщающий, что пользователь не заголинен и предлагающий пользователю авторизоваться через: GitHub, Яндекс ID или через код; Ответ уходит пользователю.
        - Если токен обновления валидный:
          - Модуль Авторизации создаёт новую пару токен доступа + токен обновления и заменяет у себя старый токен обновления новым. Новую пару отправляет в качестве ответа;
          - *Вot Logic* отправляет запрос *Redis* и просит заменить токены на новые для указанного ключа. В качестве ключа используется `chat_id`;
          - Повторно пытаемся выполнить запрос пользователя (переходим в начало этого пункта);
#### Циклические запросы внутри модуля Telegram клиент (проверка входа)
Компонент *Telegram Client* обрабатывает не только запросы от пользователей но и периодически срабатывает по таймеру.
1. Сработал таймер компонента *Telegram Client*;
2. *Telegram Client* делает запрос компоненту *Bot Logic* (перед ним сидит компонент *Nginx*);
3. *Nginx* перенаправляет запрос одной из рабочих копий компонента *Bot Logic*;
4. *Bot Logic* обращается к *Redis* и просит у него всех пользователей находящихся в статусе Анонимный;
5. Для каждого Анонимного пользователя делаем запрос к модулю Авторизации отправляя токен входа для проверки;
   - Если модуль авторизации ответил: не опознанный токен или время действия токена закончилось:
     - *Bot Logic* делает запрос *Redis*, чтобы тот удалил ключ `chat_id`. Пользователь переходит в статус Неизвестный;
   - Если модуль авторизации ответил: в доступе отказано (пользователь нажал Нет во время входа):
     - *Bot Logic* делает запрос *Redis*, чтобы тот удалил ключ `chat_id`. Пользователь переходит в статус Неизвестный;
     - *Bot Logic* добавляет в массив/словарь ответов: `chat_id` и Статус входа: неудачная авторизация; 
   - Если ответ от модуля Авторизации: доступ предоставлен (пользователь нажал Да во время входа), то:
     - *Bot Logic* проверяет, что в ответе от модуля авторизации присутствуют 2 *JWT* токена: токен доступа (*Access Token*) и токен обновления (*Refresh Token*);
     - Они присутствуют. *Bot Logic* меняет статус пользователя на Авторизованный и делает запрос *Redis* сохранить новый статус пользователя и оба *JWT* токена (токен входа больше не нужен). В качестве ключа используется `chat_id`;
     - *Bot Logic* добавляет в массив/словарь ответов: `chat_id` и Статус входа: успешная авторизация; 
6. *Bot Logic* отправляет компоненту *Telegram Client* массив/словарь ответов;
7. *Telegram Client* отправляет сообщение каждому пользователю из полученного массива/словаря.
#### Циклические запросы внутри модуля Telegram клиент (проверка уведомлений)
1. Сработал таймер компонента *Telegram Client*;
2. *Telegram Client* делает запрос компоненту *Bot Logic* (перед ним сидит компонент *Nginx*);
3. *Nginx* перенаправляет запрос одной из рабочих копий компонента *Bot Logic*;
4. *Bot Logic* обращается к *Redis* и просит у него всех пользователей находящихся в статусе Авторизованный;
5. Для каждого Авторизованного пользователя делаем запрос к Главному модулю на *URL* `/notification` отправляя его *JWT* токен доступа:
   - Если для текущего пользователя есть уведомления, *Bot Logic* добавляет их в массив/словарь ответов: `chat_id` и массив уведомлений;
   - *Bot Logic* отправляет Главному модулю запрос на удаление уведомлений для текущего пользователя отправляя его  *JWT* токен доступа;
6. *Bot Logic* отправляет компоненту *Telegram Client* массив/словарь ответов;
7. *Telegram Client* отправляет сообщение каждому пользователю из полученного массива/словаря.
<br/>

