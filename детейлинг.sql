-- Удаляем старые таблицы, если они забаговались, чтобы создать чистые
DROP TABLE IF EXISTS enrollments;
DROP TABLE IF EXISTS courses;
DROP TABLE IF EXISTS students;

-- 1. Создаем таблицу курсов
CREATE TABLE courses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    duration_hours INTEGER
);

-- 2. Создаем таблицу студентов
CREATE TABLE students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    phone TEXT,
    email TEXT,
    registration_date TEXT
);

-- 3. Создаем таблицу записей на курсы
CREATE TABLE enrollments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER,
    course_id INTEGER,
    enrollment_date TEXT,
    status TEXT DEFAULT 'Новый',
    certificate_number TEXT,
    FOREIGN KEY (student_id) REFERENCES students(id),
    FOREIGN KEY (course_id) REFERENCES courses(id)
);

-- 4. Сразу наполняем наши три курса данными
INSERT INTO courses (title, duration_hours) VALUES 
('Новичок', 20),
('Нормис', 50),
('Шиз', 120);
SELECT * FROM courses;   
INSERT INTO students (name, phone, email, registration_date) VALUES 
('Алексей Петров', '+79991112233', 'alex@mail.ru', '2026-05-20'),
('Дмитрий Иванов', '+79994445566', 'dima@yandex.ru', '2026-05-21'),
('Екатерина Смирнова', '+79001234567', 'katya@gmail.com', '2026-05-22'),
('Артем Соколов', '+79557778899', 'artem@detailing.ru', '2026-05-22'),
('Игорь Федоров', '+79119990011', 'igor@mail.ru', '2026-05-22');
INSERT INTO enrollments (student_id, course_id, enrollment_date, status, certificate_number) VALUES 
(1, 1, '2026-05-20', 'Завершен', 'CERT-NOV-001'), -- Алексей успешно закончил "Новичок"
(2, 2, '2026-05-21', 'Активен', NULL),           -- Дмитрий сейчас учится на "Нормисе"
(3, 3, '2026-05-22', 'Активен', NULL),           -- Екатерина пошла на "Шиза"
(4, 3, '2026-05-22', 'Новый', NULL),             -- Артем оставил заявку на "Шиза" (еще не подтвержден)
(5, 2, '2026-05-22', 'Отменен', NULL);           -- Игорь записался на "Нормиса", но отменил запись
SELECT s.name, c.title AS course_title, e.status 
FROM enrollments e
JOIN students s ON e.student_id = s.id
JOIN courses c ON e.course_id = c.id
WHERE s.id = 3;
SELECT s.name, c.title AS requested_course 
FROM enrollments e
JOIN students s ON e.student_id = s.id
JOIN courses c ON e.course_id = c.id
WHERE e.status = 'Новый';
SELECT c.title, COUNT(e.id) AS active_students_count
FROM enrollments e
JOIN courses c ON e.course_id = c.id
WHERE e.status = 'Активен'
GROUP BY c.id;
