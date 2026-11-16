**Проект "Блогикум" - социальная сеть для публикации постов.**

*Здесь Вы можете создавать свои посты, выбирать для них тему и геолокацию,*
*а также читать и комментировать посты других пользователей.*

Стек технологий: Python 3.12, Django, HTML, Bootstrap.

Запуск проекта:
1. Клонировать репозиторий и перейти в него в командной строке:
```
git clone git@github.com:AnnBogd/Final_Blogicum.git
```
```
cd Final_Blogicum
```

2. Создать и активировать виртуальное окружение (ОС Windows)
```
python -m vevn venv
source venv/Scripts/activate
```

3. Установить зависимости:
```
pip install -r requirements
```

4. Создать миграции
```
python manage.py makemigrations
```

5. Применить миграции
```
python manage.py migrate
```

6. Запуск проекта:
```
python manage.py runserver
```
