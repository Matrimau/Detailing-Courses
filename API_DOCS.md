# Документация API

## Как запустить

### Core сервис (Flask)
```
pip install -r requirements.txt
python app.py
```
Работает на `http://localhost:5000`

### Supporting сервис (FastAPI)
```
python supporting.py
```
Работает на `http://localhost:5001`

---

## Core сервис (Flask) — порт 5000

### Авторизация

#### POST /registration
Регистрация нового пользователя
- Body: `{"username": "nick", "password": "pass123"}`
- Успех: `{"status": "ok", "token": "jwt_token..."}`
- Ошибка: `{"error": "ты уже существуешь"}`

#### POST /login
Вход в аккаунт
- Body: `{"username": "nick", "password": "pass123"}`
- Успех: `{"status": "ok", "token": "jwt_token..."}`
- Ошибка: `{"error": "ты не родился ещё", "id": "log-nick"}`

#### GET /protected
Проверка что токен рабочий
- Headers: `Authorization: Bearer <token>`
- Ответ: `{"logged_in_as": "nick"}`

#### POST /refresh-token
Обновление токена
- Headers: `Authorization: Bearer <token>`
- Ответ: `{"token": "new_token...", "tolen": "new_token..."}`

### Профиль

#### GET /user
Профиль текущего пользователя (для фронтенда)
- Headers: `Authorization: Bearer <token>`
- Ответ:
```json
{
  "username": "nick",
  "data": {"created_at": "2026-05-25 12:00:00"},
  "course": "Новичок"
}
```

#### GET /\<username\>
Профиль по имени пользователя (для препода)
- Headers: `Authorization: Bearer <token>`
- Ответ: `{"username": "nick", "created_at": "2026-05-25 12:00:00"}`

### Утилиты

#### GET /api/about
Информация о проекте из about.json
- Без авторизации
- Ответ: содержимое about.json

#### GET /api/hash/\<text\>
Хеширование строки через SHA-256
- Без авторизации
- Пример: `GET /api/hash/hello`
- Ответ:
```json
{
  "request": "hello",
  "result": "2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824"
}
```

### Дашборд

#### GET /dashboard
Статистика для графиков
- Headers: `Authorization: Bearer <token>`
- Ответ:
```json
{
  "totalUsers": 5,
  "hardcore": 2,
  "normal": 2,
  "chill": 1,
  "monthlyLabels": ["Май"],
  "monthlyValues": [5]
}
```

### CRUD Курсы

Все CRUD роуты защищены токеном (`Authorization: Bearer <token>`)

#### GET /api/courses
Список курсов с поиском, сортировкой и пагинацией
- Query параметры:
  - `search` — поиск по названию
  - `sort` — поле сортировки (id, title, duration_hours)
  - `order` — направление (asc, desc)
  - `page` — номер страницы (по умолчанию 1)
  - `per_page` — элементов на странице (по умолчанию 10)
- Пример: `GET /api/courses?search=Нов&sort=title&order=asc&page=1&per_page=5`
- Ответ:
```json
{
  "data": [{"id": 1, "title": "Новичок", "duration_hours": 20}],
  "total": 1,
  "page": 1,
  "per_page": 5
}
```

#### GET /api/courses/\<id\>
Один курс по id

#### POST /api/courses
Создать курс
- Body: `{"title": "Мастер", "duration_hours": 200}`

#### PUT /api/courses/\<id\>
Обновить курс
- Body: `{"title": "Мастер+", "duration_hours": 250}`

#### DELETE /api/courses/\<id\>
Удалить курс

### CRUD Студенты

#### GET /api/students
Список с поиском по имени/email, сортировка и пагинация (аналогично курсам)

#### GET /api/students/\<id\>
#### POST /api/students
- Body: `{"name": "Иван", "phone": "+79991234567", "email": "ivan@mail.ru"}`

#### PUT /api/students/\<id\>
#### DELETE /api/students/\<id\>

### CRUD Записи на курсы

#### GET /api/enrollments
Список с поиском по статусу, сортировка и пагинация. В ответе также имя студента и название курса (JOIN)

#### GET /api/enrollments/\<id\>
#### POST /api/enrollments
- Body: `{"student_id": 1, "course_id": 2}`

#### PUT /api/enrollments/\<id\>
- Body: `{"status": "Завершен", "certificate_number": "CERT-001"}`

#### DELETE /api/enrollments/\<id\>

### Прокси к Supporting сервису

#### GET /api/analytics
Проксирует запрос к Supporting сервису. Если сервис недоступен — возвращает резервные данные

#### GET /api/notifications
Проксирует уведомления. При недоступности возвращает пустой список

---

## Supporting сервис (FastAPI) — порт 5001

Внутренний сервис, без авторизации (вызывается только из Core)

#### GET /api/analytics
Расширенная аналитика
```json
{
  "avg_duration": 63,
  "total_enrollments": 5,
  "completed": 1,
  "completion_rate": 20,
  "popular_course": "Нормис",
  "courses": [
    {"title": "Новичок", "duration_hours": 20, "students_count": 1},
    {"title": "Нормис", "duration_hours": 50, "students_count": 2},
    {"title": "Шиз", "duration_hours": 120, "students_count": 2}
  ]
}
```

#### GET /api/notifications
Последние записи на курсы
```json
{
  "notifications": [
    {
      "text": "Алексей Петров записался на курс \"Новичок\"",
      "date": "2026-05-20",
      "status": "Завершен"
    }
  ]
}
```

#### GET /api/report
Сводный отчет
```json
{
  "total_students": 5,
  "total_courses": 3,
  "total_enrollments": 5,
  "enrollments_by_status": {
    "Завершен": 1,
    "Активен": 2,
    "Новый": 1,
    "Отменен": 1
  }
}
```
