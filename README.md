# WeatherProject

Сервис для получения погоды на ближайшее время

## Описание

Веб-приложение для получения прогноза погоды по названию города, разработанное на фреймворке `Django 5.0.7`. Приложение сохраняет предыдущие запросы пользователя, запоминая его ip-адрес, и при повторном посещение показывает последние 5 вариантов. В приложение создана модель `City`, которая обеспечивает хранение городов и их координат в базе данных. Доступна форма, которая предлагает варианты на основе введенного пользователем текста. Написаны тесты на библиотеке Unittest. Настроено кеширование, обновляемое каждые 15 минут. При желание проект можно запустить в Docker-контейнере.

## Стек

- Python 3.10.12
- Django 5.0.7
- requests
- Unittest
- SQLite

## Как запустить проект:

Клонировать репозиторий:

```bash
git clone git@github.com:bissaliev/WeatherProject.git
```

Перейти в директорию:

```bash
cd WeatherProject
```

Установить виртуальное окружение:

```bash
python3 -m venv venv
```

Активировать виртуальное окружение:

```bash
. venv/bin/activate
```

Установить зависимости:

```bash
pip install -r requirements.txt
```

Перейти в директорию `weather_app`:

```bash
cd weather_app/
```

Сделать миграции:

```bash
python3 manage.py migrate
```

Загрузить фикстуры для модели `City`:

```bash
python3 manage.py loaddata fixtures/cities.json
```

Запустить проект в виртуальном окружение:

```bash
python3 manage.py runserver
```

### Также проект можно запустить в Docker-контейнере

Из директории `WeatherProject` выполните команду для сборки образа:

```bash
docker build -t weather_app .
```

Запустите контейнер:

```bash
docker run --name weather_app -p 8000:8000 weather_app
```

Сделать миграции:

```bash
docker exec weather_app python3 manage.py migrate
```

Загрузить фикстуры для модели `City`:

```bash
docker exec python3 manage.py loaddata fixtures/cities.json
```

## Автор

[Олег Биссалиев](https://github.com/bissaliev)
