# praktikum_new_diplom




Проект foodgram  «Продуктовый помощник»: сайт,
на котором пользователи будут публиковать рецепты,
добавлять чужие рецепты в избранное и подписываться на публикации других авторов.
Сервис «Список покупок» позволит пользователям создавать список продуктов,
которые нужно купить для приготовления выбранных блюд. 

## Сайт доступен по [адресу](http://158.160.19.86/recipes)

## Технологии:
Python 3.7, Django 2.2, DRF, Djoser, PostgreSQL, Docker

![Workflow stat](https://github.com/Guzelik-Victor/foodgram-project-react/actions/workflows/foodgram_workflow.yml/badge.svg)

<details>
<summary><h2>Как запустить проект:</h2></summary>

### *Клонируйте репозиторий:*
```
git@github.com:Guzelik-Victor/foodgram-project-react.git
```

### *Установите и активируйте виртуальное окружение:*
Win:
```
python -m venv venv
venv/Scripts/activate
```

Mac:
```
python3 -m venv venv
source venv/bin/activate
```

### *Установите зависимости из файла requirements.txt:*
```
pip install -r requirements.txt
```

### *Перейдите в директорию с файлом manage.py, создайте и примените миграции (python3 для Mac):*
```
cd backend/foodgram
python manage.py makemigrations
python manage.py migrate
```

### *Создайте суперпользователя (python3 для Mac):*
```
python manage.py createsuperuser
```

### *Запустите сервер (python3 для Mac):*
```
python manage.py runserver
```

### *Чтобы запустить проект через докер:*
В папке **frontend** соберите образ docker `build -t YourDockerNickname/foodgram_frontend .`

В папке **infra** создайте файл **.env** и заполните его данными. Пример:
```
SECRET_KEY=YourSecretKeyFromDjangoProjectSettings
DEBUG=True
ALLOWED_HOSTS='*'
DB_ENGINE=django.db.backends.postgresql
DB_NAME=postgres
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=db
DB_PORT=5432
```
Для работы с workflow и деплоем на сервер добавьте Github Secrets. Шаблон:
```
DB_ENGINE=django.db.backends.postgresql
DB_NAME=postgres
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=db
DB_PORT=5432
DEBUG=True
DOCKER_PASSWORD=YourPassword
DOCKER_USERNAME=YourUsername

USER=ServerUsername
HOST=ServerIP
PASSPHRASE=GitPassphrase
SSH_KEY=SSHKey (для получения команда: cat ~/.ssh/id_rsa)

TELEGRAM_TO=YourTelegramID
TELEGRAM_TOKEN=BotToken
```
Далее в папке **infra** запустите команду `docker-compose up --build`

После сборки запустите миграции, соберите статику, создайте суперпользователя, подгрузите данные из копии бд:
```
docker-compose exec backend python manage.py makemigrations
docker-compose exec backend python manage.py migrate
docker-compose exec backend python manage.py collectstatic --no-input
docker-compose exec backend python manage.py data_csv_for_db
docker-compose exec backend python manage.py createsuperuser
```
Для остановки контейнера `docker-compose down -v`
</details>


## Разработчик:
[Гузелик Виктор](https://github.com/Guzelik-Victor)
