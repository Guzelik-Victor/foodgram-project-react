# praktikum_new_diplom


## Описание:

Проект foodgram  «Продуктовый помощник»: сайт,
на котором пользователи будут публиковать рецепты,
добавлять чужие рецепты в избранное и подписываться на публикации других авторов.
Сервис «Список покупок» позволит пользователям создавать список продуктов,
которые нужно купить для приготовления выбранных блюд. 



## Технологии:
- Python 3.11, Django 4.2, DRF, Djoser

<details>
<summary><h2>Как запустить проект:</h2></summary>

## *Клонируйте репозиторий:*

```
git clone git@github.com:Guzelik-Victor/foodgram-project-react.git
```

## *Перейдите в репозиторий, foodgram создайте файл .env и заполните его:*
```
cd backend/foodgram
touch .env
nano .env
```

### *Шаблон наполнения файла .env:*
```
DB_ENGINE=django.db.backends.postgresql
DB_NAME=postgres
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
DB_HOST=db
DB_PORT=5432
SERET_KEY=your_secret_key

## *Заполните базу данных ингредиентами:*
```
python manage.py ingredients_csv_for_db
```


### Cервис локально доступty по [адресу](http://127.0.0.1:8000)


</details>

## Разработчик:
[Гузелик Виктор](https://github.com/Guzelik-Victor)