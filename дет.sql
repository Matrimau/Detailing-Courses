-- ==========================================
-- 1. структура бд 
-- ==========================================

DROP TABLE IF EXISTS course_views;
DROP TABLE IF EXISTS courses;
DROP TABLE IF EXISTS students;

CREATE TABLE courses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    content TEXT NOT NULL
);

CREATE TABLE students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    phone TEXT,
    email TEXT NOT NULL UNIQUE,
    registration_date DATE
);

CREATE TABLE course_views (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    course_id INTEGER NOT NULL,
    view_date DATETIME,
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
    FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE CASCADE
);

-- ==========================================
-- 2. демо данные 
-- ==========================================

INSERT INTO courses (title, content) VALUES 
('Новичок', 'Текст курса Новичок: Двухфазная мойка, глина, базовый уход...'), 
('Нормис', 'Текст курса Нормис: Химчистка, полировка в 2 шага, защитные составы...'), 
('Шиз', 'Текст курса Шиз: Реставрация кожи, оклейка полиуретаном, сложные работы...');

INSERT INTO students (name, phone, email, registration_date) VALUES 
('Алексей Петров', '+79991112233', 'alex@mail.ru', '2026-05-20'),
('Дмитрий Иванов', '+79994445566', 'dima@yandex.ru', '2026-05-21'),
('Екатерина Смирнова', '+79001234567', 'katya@gmail.com', '2026-05-22');

INSERT INTO course_views (student_id, course_id, view_date) VALUES 
(1, 1, '2026-05-20 14:00:00'),
(2, 2, '2026-05-21 15:30:00'),
(2, 3, '2026-05-22 10:00:00'),
(2, 3, '2026-05-22 18:00:00'),
(3, 3, '2026-05-22 11:15:00');

-- ==========================================
-- 3. пул из 26 запросов погнали еееее
-- ==========================================

-- Запрос 1: Проверка учетных данных при авторизации юзера
SELECT id, name, email FROM students WHERE email = 'dima@yandex.ru';

-- Запрос 2: Список всех курсов для вывода на главной странице
SELECT id, title FROM courses;

-- Запрос 3: Получение контента выбранного курса по его ID
SELECT title, content FROM courses WHERE id = 3;

-- Запрос 4: Список уникальных курсов, которые пользователь уже открывал
SELECT DISTINCT c.title FROM course_views cv
JOIN courses c ON cv.course_id = c.id
WHERE cv.student_id = 2;

-- Запрос 5: Поиск курса, который пользователь открывал последним
SELECT c.title FROM course_views cv
JOIN courses c ON cv.course_id = c.id
WHERE cv.student_id = 2
ORDER BY cv.view_date DESC LIMIT 1;

-- Запрос 6: Общее количество просмотров материалов конкретным студентом
SELECT COUNT(*) AS total_views FROM course_views WHERE student_id = 2;

-- Запрос 7: Регистрация нового пользователя на сайте
INSERT INTO students (name, phone, email, registration_date) 
VALUES ('Сергей Полиш', '+79110001122', 'sergey@detailing.ru', '2026-05-28');

-- Запрос 8: Фиксация перехода пользователя на страницу курса
INSERT INTO course_views (student_id, course_id, view_date) 
VALUES (2, 3, '2026-05-28 19:40:00');

-- Запрос 9: Обновление контактных данных в профиле пользователя
UPDATE students SET phone = '+79990000000' WHERE id = 2;

-- Запрос 10: Редактирование лекционного материала (обновление контента)
UPDATE courses SET content = 'Обновленный текст курса Нормис с новыми лайфхаками...' WHERE title = 'Нормис';

-- Запрос 11: Сброс истории просмотров в личном кабинете юзера
DELETE FROM course_views WHERE student_id = 2;

-- Запрос 12: Полное удаление аккаунта пользователя из системы
DELETE FROM students WHERE id = 1;

-- Запрос 13: Общее число зарегистрированных пользователей в базе
SELECT COUNT(*) AS total_users FROM students;

-- Запрос 14: Общее количество кликов по курсам за все время
SELECT COUNT(*) AS total_clicks FROM course_views;

-- Запрос 15: Список пользователей, отсортированный по дате регистрации (сначала новые)
SELECT * FROM students ORDER BY registration_date DESC;

-- Запрос 16: Лента активности пользователей для панели модератора
SELECT s.name, c.title, cv.view_date FROM course_views cv
JOIN students s ON cv.student_id = s.id
JOIN courses c ON cv.course_id = c.id
ORDER BY cv.view_date DESC;

-- Запрос 17: Самый популярный курс на платформе
SELECT c.title, COUNT(cv.id) AS click_count FROM courses c
LEFT JOIN course_views cv ON c.id = cv.course_id
GROUP BY c.id, c.title ORDER BY click_count DESC LIMIT 1;

-- Запрос 18: Статистика просмотров по каждому направлению отдельно
SELECT c.title, COUNT(cv.id) AS total_views FROM courses c
LEFT JOIN course_views cv ON c.id = cv.course_id
GROUP BY c.id, c.title;

-- Запрос 19: Список пользователей, которые ни разу не открывали курсы после регистрации
SELECT s.name, s.email FROM students s
LEFT JOIN course_views cv ON s.id = cv.student_id WHERE cv.id IS NULL;

-- Запрос 20: Поиск пользователей, изучавших один и тот же курс повторно
SELECT s.name, c.title, COUNT(cv.id) AS view_count FROM course_views cv
JOIN students s ON cv.student_id = s.id
JOIN courses c ON cv.course_id = c.id
GROUP BY cv.student_id, cv.course_id
HAVING view_count > 1;

-- Запрос 21: Статистика кликов по датам (активность по дням)
SELECT DATE(view_date) AS day, COUNT(*) AS clicks FROM course_views GROUP BY day;

-- Запрос 22: Количество новых регистраций в разрезе дней
SELECT registration_date, COUNT(*) AS new_users FROM students GROUP BY registration_date;

-- Запрос 23: Топ-3 самых активных пользователей по числу переходов
SELECT s.name, COUNT(cv.id) AS activity_score FROM students s
JOIN course_views cv ON s.id = cv.student_id
GROUP BY s.id, s.name ORDER BY activity_score DESC LIMIT 3;

-- Запрос 24: Поиск профиля студента по совпадению в имени
SELECT * FROM students WHERE name LIKE '%Петров%';

-- Запрос 25: Фильтрация базы пользователей по доменной зоне почты
SELECT * FROM students WHERE email LIKE '%@yandex.ru';

-- Запрос 26: Среднее количество уникальных курсов, просмотренных одним юзером
SELECT AVG(unique_courses) FROM (
    SELECT COUNT(DISTINCT course_id) AS unique_courses FROM course_views GROUP BY student_id
);