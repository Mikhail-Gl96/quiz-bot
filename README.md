# Бот с викторинами
Данный чат бот проводит викторины для участников.

Заявленный базовый функционал:
1. кнопочное меню
2. база данных
3. анализе ответов пользователей

#### Бот работает с версиями Python 3.6+ <br>С версиями ниже бот не работает!!!

## Настройка для использования на личном ПК
1. Скачайте проект с гитхаба
2. Перейдите в папку с ботом с помощью консоли и команды `cd <путь до проекта>`<br>
3. Установить зависимости из файла `requirements.txt`<br>
   Библиотеки к установке: `requests`, `python-telegram-bot`, `python-dotenv`, `redis`, `vk-api`.<br>
   
   Возможные команды для установки:<br>
   `pip3 install -r requirements.txt`<br>
   `python -m pip install -r requirements.txt`<br>
   `python3.6 -m pip install -r requirements.txt`
4. Создайте файл .env
5. Запишите в файл .env переменные:
    `VKONTAKTE_GROUP_TOKEN=ваш_токен_группы вконтакте`<br>
    `TELEGRAM_TOKEN=ваш_токен_телеграм_бота`<br>
    `TELEGRAM_CHAT_ID=ваш_телеграм_айди`<br>
    `REDIS_PASSWORD=пароль_от_бд_redis`<br>
    `REDIS_ENDPOINT=ссылка_до_бд_redis`<br>
    `REDIS_PORT=порт_до_бд_redis`<br>
6. Запустите бота<br>
   Возможные команды для запуска(из консоли, из папки с ботом):<br>
   ```
   python3 vk_bot.py
   python3 telegram_bot.py
   ```
   или
   ```
   python vk_bot.py
   python telegram_bot.py
   ```
   или
   ```
   python3.6 main.py
   python3.6 telegram_bot.py
   ```
   
## Настройка для деплоя в облако Heroku
Если не знаем что такое Heroku - гуглим мануал или используем настройку бота из предыдущего туториала
1. Создайте `app` на Heroku 
2. Перейдите в созданный `app` и выберите GitHub в качестве `Deployment method`
3. Укажите адрес до **вашего!!!** проекта на гитхабе
4. Зайдите в раздел `Settings`
5. Запишите в раздел `Config Vars` переменные `KEY` и `VALUE`:
    `VKONTAKTE_GROUP_TOKEN=ваш_токен_группы вконтакте`<br>
    `TELEGRAM_TOKEN=ваш_токен_телеграм_бота`<br>
    `TELEGRAM_CHAT_ID=ваш_телеграм_айди`<br>
    `REDIS_PASSWORD=пароль_от_бд_redis`<br>
    `REDIS_ENDPOINT=ссылка_до_бд_redis`<br>
    `REDIS_PORT=порт_до_бд_redis`<br>
6. Зайдите в раздел `Deploy`, выберите ветку main в разделе `Manual deploy` и нажмите на кнопку `Deploy Branch`<br>
7. Перейдите в раздел `Resources` и включите бота<br> 
   Логи можно посмотреть в `More` -> `View logs`
  