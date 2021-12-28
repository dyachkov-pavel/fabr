# Тестовое задание для Фабрики Решений
## Приложение для опроса пользователей
**Задача:** спроектировать и разработать API для системы опросов пользователей.
## Функционал для администратора системы:

- авторизация в системе (регистрация не нужна)
- добавление/изменение/удаление опросов. Атрибуты опроса: название, дата старта, дата окончания, описание. После создания поле "дата старта" у опроса менять нельзя
- добавление/изменение/удаление вопросов в опросе.

## Функционал для пользователей системы:

- получение списка активных опросов
- прохождение опроса: опросы можно проходить анонимно, в качестве идентификатора пользователя в API передаётся числовой ID, по которому сохраняются ответы пользователя на вопросы; один пользователь может участвовать в любом количестве опросов
- получение пройденных пользователем опросов с детализацией по ответам (что выбрано) по ID уникальному пользователя

## Использованы следующие технологии: 
Django 2.2.10, Django REST framework

## Инструкция по разворачиванию приложения
1. **Склонируйте репозиторий**

```
git clone https://github.com/dyachkov-pavel/fabr.git
```

2. **Перейдите в директорию fabr**

```
cd fabr
```

3. **Создайте и активируйте виртуальное окружение**

```
python -m venv venv
```

```
source venv/Scripts/activate
```

4. **Установите зависимости**

```
pip install -r requirements.txt
```

5. **Примените миграции**

```
python manage.py makemigrations
```

```
python manage.py makemigrations polls
```

```
python manage.py migrate
```

6. **По желанию, можете заполнить базу начальными данными**

```
python manage.py loaddata fixtures.json
```

7. **Создайте супер юзера**

```
winpty python manage.py createsuperuser
```

8. **Запустите тесты**

```
python manage.py test tests
```

9. **Запустите сервер**

```
python manage.py runserver
```

# API для опроса пользователей
## Эндпоинты для админа
Разрешение: IsAdminUser
### POST /api/v1/admin/polls
**Создать опрос**

***Пример запроса***
```
{
    "title": "Название", # string
    "description": "Описание", # string
    "start_date": "2021-12-21", # "YYYY-MM-DD"
    "end_date": "2021-12-31"  # "YYYY-MM-DD"
}
```

***Тело ответа***\
HTTP 201 Created\
Allow: POST, OPTIONS\
Content-Type: application/json\
Vary: Accept

```
{
    "poll_id": 1,
    "title": "Название",
    "description": "Описание",
    "start_date": "2021-12-21",
    "end_date": "2021-12-31"
}
```
### PATCH /api/v1/admin/polls/{pk}
**Обновить опрос**

Начальную дату изменить нельзя

***Пример запроса***
```
{
    "title": "Измененное название", # string
    "description": "Измененное описание", # string
    "end_date": "2021-12-30"  # "YYYY-MM-DD"
}
```
***Тело ответа***\
HTTP 200 OK\
Allow: PUT, PATCH, DELETE, OPTIONS\
Content-Type: application/json\
Vary: Accept
```
{
    "poll_id": 1,
    "title": "Измененное название",
    "description": "Измененное описание",
    "start_date": "2021-12-21",
    "end_date": "2021-12-30"
}
```
### DELETE /api/v1/admin/polls/{pk}
**Удалить опрос**

***Тело ответа***\
HTTP 204 No Content\
Allow: PUT, PATCH, DELETE, OPTIONS\
Content-Type: application/json\
Vary: Accept

### POST /api/v1/admin/polls/{poll_id}/questions/

**Создать вопрос**\
***Пример запроса для вопроса с типом TEXT***
```
{
    "question_text": "Сколько Вам лет?", # string
    "question_type": "TEXT", # string
    "question_choice": [] # Оставьте поле пустым, если тип вопроса текст
}
```
***Тело ответа***\
HTTP 201 Created\
Allow: POST, OPTIONS\
Content-Type: application/json\
Vary: Accept
```
{
    "question_id": 1,
    "question_text": "Сколько вам лет",
    "question_type": "TEXT",
    "question_choice": []
}
```
***Пример запроса для вопроса с типом CHOICE, MULTICHOICE***
```
{
    "question_text": "Выберите ответ", # string
    "question_type": "CHOICE", # string
    "question_choice": [
      {"choice_text": "Первый ответ"}, # string
      {"choice_text": "Второй ответ"} # string
    ]
}
```
***Тело ответа***\
HTTP 201 Created\
Allow: POST, OPTIONS\
Content-Type: application/json\
Vary: Accept
```
{
    "question_id": 1,
    "question_text": "Выберите ответ",
    "question_type": "CHOICE",
    "question_choice": [
        {
            "choice_id": 1,
            "choice_text": "Первый ответ"
        },
        {
            "choice_id": 2,
            "choice_text": "Второй ответ"
        }
    ]
}
```
### PUT /api/v1/admin/polls/{poll_id}/questions/{pk}
**Изменить вопрос**

***Пример запроса***
```
{
    "question_text": "Выберите сколько вам лет", # string
    "question_type": "CHOICE", # string
    "question_choice": [
      {"choice_text": "Меньше 18"}, # string
      {"choice_text": "Больше 18"} # string
    ]
}
```
***Тело ответа***\
HTTP 200 OK\
Allow: PUT, PATCH, DELETE, OPTIONS\
Content-Type: application/json\
Vary: Accept

```
{
    "question_id": 1,
    "question_text": "Выберите сколько вам лет",
    "question_type": "CHOICE",
    "question_choice": [
        {
            "choice_id": 1,
            "choice_text": "Меньше 18"
        },
        {
            "choice_id": 2,
            "choice_text": "Больше 18"
        }
    ]
}
```
### PATCH /api/v1/admin/polls/{poll_id}/questions/{pk}
**Частично изменить вопрос**

***Пример запроса***
```
{
    "question_text": "Как у Вас дела?", # string
}
```
***Тело ответа***\
HTTP 200 OK\
Allow: PUT, PATCH, DELETE, OPTIONS\
Content-Type: application/json\
Vary: Accept
```
{
    "question_id": 1,
    "question_text": "Как у Вас дела?",
    "question_type": "TEXT",
    "question_choice": []
}
```
### DELETE /api/v1/admin/polls/{poll_id}/questions/{pk}
**Удалить вопрос**

***Тело ответа***\
HTTP 204 No Content\
Allow: PUT, PATCH, DELETE, OPTIONS\
Content-Type: application/json\
Vary: Accept

## Эндпоинты для пользователя
Разрешение: AllowAny

### GET /api/v1/polls
**Получение списка активных опросов**

***Тело ответа***\
HTTP 200 OK\
Allow: GET, HEAD, OPTIONS\
Content-Type: application/json\
Vary: Accept
```
[
    {
        "poll_id": 1,
        "title": "Первый опрос",
        "description": "Первое описание",
        "start_date": "2021-12-20",
        "end_date": "2022-12-30"
    },
    {
        "poll_id": 2,
        "title": "Второй опрос",
        "description": "Второе описание",
        "start_date": "2021-12-20",
        "end_date": "2022-12-30"
    }
]
```

### POST /api/v1/polls/{poll_id}/answer/
**Создать ответ на вопрос**
***Пример запроса если вопрос типа текст***
```

{
    "user_id": 1, # integer
    "question": 1, # integer
    "answer_text": "текст" # string
}
```
***Тело ответа***\
HTTP 201 Created\
Allow: POST, OPTIONS\
Content-Type: application/json\
Vary: Accept
```
{
    "answer_id": 1,
    "user_id": 1,
    "question": 1,
    "choice": null,
    "answer_text": "текст"
}
```
***Пример запроса если вопрос типа CHOICE, MULTICHOICE***
```
{
    "user_id": 1,
    "question": 2,
    "choice": 1
}
```
***Тело ответа***\
HTTP 201 Created\
Allow: POST, OPTIONS\
Content-Type: application/json\
Vary: Accept
```
{
    "answer_id": 2,
    "user_id": 1,
    "question": 2,
    "choice": 1,
    "answer_text": ""
}
```
### GET /api/v1/users/{user_id}/answers/
**Получение пройденных пользователем опросов с детализацией по ответам**

```
[
    {
        "poll_id": 1,
        "poll_title": "Первый опрос",
        "poll_description": "Описание первого опроса",
        "user_answers": [
            {
                "question_id": 1,
                "question_type": "TEXT",
                "question_text": "Сколько вам лет",
                "answer_text": "20",
                "choice": ""
            }
        ]
    },
    {
        "poll_id": 2,
        "poll_title": "Второй опрос",
        "poll_description": "Описание второго опроса",
        "user_answers": [
            {
                "question_id": 3,
                "question_type": "CHOICE",
                "question_text": "Укажите ваш пол?",
                "answer_text": "",
                "choice": "Больше 18"
            },
            {
                "question_id": 4,
                "question_type": "TEXT",
                "question_text": "Напишите ваше имя",
                "answer_text": "Паша",
                "choice": ""
            }
        ]
    }
]
```
