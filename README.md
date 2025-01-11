# Телеграм-бот трекер задач
Бот умеет:

    - создавать список задач;
    - задавать расписание для отправки напоминаний;


# Бот понимает следующие команды:


   - /start или /help - приветственное сообщение и список доступных команд
   - /subscribe тема <тема> рейтинг <рейтинг> уровень <уровень> - подписаться на рассылку
   - /unsubscribe - отписаться
   - /status - статус подписки
   - /tags - выводит список тем
   - /level - выводит значения уровней
   - /rating - выводит значения рейтинга
   - /sample - выводит шаблон для подписки

## Для локального запуска проекта необходимо выполнить следующие команды:
   - при работе на Linux запустить сервисы postgresql и redis:

    sudo service postgresql start

    sudo service redis-server start

   - создать базу данных и записать ее название в переменную POSTGRES_DB в .env-файл

   - установить виртуальное окружение:

    python -m venv venv

    python3 -m venv venv

   - активировать виртуальное окружение:

    venv/Scripts/activate

    source venv/bin/activate

   - установить зависимости:

    python -m pip install -r requirements-win.txt

    python3 -m pip install -r requirments.txt

   - применить миграции:

    python manage.py migrate

   - загрузить данные из дампа:

    python manage.py loaddata data.json

   - либо работать с пустой базой, тогда нужно создать пользователей:

    python manage.py csu

   - запустить проект:

    python manage.py runserver

   - в отдельном терминале запустить celery:

    celery -A config worker -l INFO -P eventlet celery -A config worker -l INFO

   - и beat:

    celery -A config beat -l INFO

   - либо одной командой:

    celery -A config.celery worker --beat --loglevel=info -D

   ## В проекте реализованы следующие команды:



      - python manage.py start_bot- запуск бота
      - python manage.py csu - создание пользователя с правами админа (логин - id 1, и пароль- 123abc123)