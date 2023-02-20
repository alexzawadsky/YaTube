### Информация об авторе:

Меня зовут Алексей и мне 16 лет) Сейчас учусь в Яндекс.Практикуме по специальности Python-разработчик. В будущем думаю пробовать развиваться на фриланс площадках.

### Инфомация о проекте:

Это учебный проект Yatube API - социальная сеть.
Здесь вы сможете выкладывать посты, оставлять комментарии и подписываться на людей через API.

### Как запустить проект:

Клонировать репозиторий и перейти в него в командной строке:

```
git@github.com:alexzawadsky/api_yatube.git
```

```
cd api_yatube
```

Cоздать и активировать виртуальное окружение:

```
python -m venv env
```

```
source venv/Scripts/activate
```

Установить зависимости из файла requirements.txt:

```
pip install -r requirements.txt
```

Выполнить миграции:

```
python manage.py migrate
```

Запустить проект:

```
python manage.py runserver
```

### API документация:

Основные ресурсы:
```
/posts
/posts/<post_id>comments
/groups
/follows
```
```
/posts/<post_id>
/posts/<post_id>/comments/<comment_id>
/groups/<group_id>
```
Примеры запросов:
```
POST .../api/v1/jwt/create/
{
    "username": "<your username>",
    "password": "<your password>"
}
ОТВЕТ:
{
    "refresh": "<your refresh token>",
    "access": "<your access token>"
}
```
```
POST .../api/v1/posts/
{
    "text": "Вечером собрались в редакции «Русской мысли», чтобы поговорить о народном театре. Проект Шехтеля всем нравится.",
    "group": 1
}
ОТВЕТ:
{
    "id": 14,
    "text": "Вечером собрались в редакции «Русской мысли», чтобы поговорить о народном театре. Проект Шехтеля всем нравится.",
    "author": "anton",
    "image": null,
    "group": 1,
    "pub_date": "2021-06-01T08:47:11.084589Z"
} 
```
```
POST .../api/v1/posts/14/comments/
{
    "text": "тест тест"
}
ОТВЕТ:
{
    "id": 4,
    "author": "anton",
    "post": 14,
    "text": "тест тест",
    "created": "2021-06-01T10:14:51.388932Z"
}
```
```
GET .../api/v1/groups/2/
ОТВЕТ:
{
    "id": 2,
    "title": "Математика",
    "slug": "math",
    "description": "Посты на тему математики"
} 
```
```
POST .../api/v1/follow/
{
    "following": "vika223"
}
ОТВЕТ:
{
    "user": "alex",
    "following": "vika223"
}
```
```
GET .../api/v1/follow/
ОТВЕТ:
{
    "user": "alex",
    "following": "vika223"
}
```
