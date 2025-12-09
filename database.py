import sqlite3
from datetime import datetime
import hashlib

class Database:
    def __init__(self, db_name='uchet.db'):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.create_tables()
    
    def create_tables(self):
        """Создание всех необходимых таблиц"""
        
        # Таблица пользователей
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL CHECK(role IN ('admin', 'director', 'manager', 'worker', 'organizer')),
            full_name TEXT NOT NULL,
            email TEXT,
            phone TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_active INTEGER DEFAULT 1
        )
        ''')
        
        # Таблица отделов
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS departments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            director_id INTEGER,
            FOREIGN KEY (director_id) REFERENCES users (id)
        )
        ''')
        
        # Таблица проектов
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            start_date DATE,
            end_date DATE,
            budget REAL,
            status TEXT DEFAULT 'active',
            organizer_id INTEGER,
            FOREIGN KEY (organizer_id) REFERENCES users (id)
        )
        ''')
        
        # Таблица задач
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            project_id INTEGER,
            assigned_to INTEGER,
            priority TEXT CHECK(priority IN ('low', 'medium', 'high', 'critical')),
            status TEXT DEFAULT 'pending',
            deadline DATE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (project_id) REFERENCES projects (id),
            FOREIGN KEY (assigned_to) REFERENCES users (id)
        )
        ''')
        
        self.conn.commit()
    
    def hash_password(self, password):
        """Хеширование пароля"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def create_user(self, username, password, role, full_name, email=None, phone=None):
        """Создание нового пользователя"""
        password_hash = self.hash_password(password)
        try:
            self.cursor.execute('''
            INSERT INTO users (username, password_hash, role, full_name, email, phone)
            VALUES (?, ?, ?, ?, ?, ?)
            ''', (username, password_hash, role, full_name, email, phone))
            self.conn.commit()
            return self.cursor.lastrowid
        except sqlite3.IntegrityError:
            return None
    
    def authenticate_user(self, username, password):
        """Аутентификация пользователя"""
        password_hash = self.hash_password(password)
        self.cursor.execute('''
        SELECT id, username, role, full_name FROM users 
        WHERE username = ? AND password_hash = ? AND is_active = 1
        ''', (username, password_hash))
        return self.cursor.fetchone()
    
    def get_user_by_id(self, user_id):
        """Получение информации о пользователе по ID"""
        self.cursor.execute('''
        SELECT id, username, role, full_name, email, phone, created_at 
        FROM users WHERE id = ?
        ''', (user_id,))
        return self.cursor.fetchone()
    
    def get_all_users(self):
        """Получение всех пользователей"""
        self.cursor.execute('''
        SELECT id, username, role, full_name, email, phone, created_at, is_active 
        FROM users ORDER BY role, full_name
        ''')
        return self.cursor.fetchall()
    
    def create_department(self, name, director_id=None):
        """Создание отдела"""
        self.cursor.execute('''
        INSERT INTO departments (name, director_id) VALUES (?, ?)
        ''', (name, director_id))
        self.conn.commit()
        return self.cursor.lastrowid
    
    def create_project(self, name, description, start_date, end_date, budget, organizer_id):
        """Создание проекта"""
        self.cursor.execute('''
        INSERT INTO projects (name, description, start_date, end_date, budget, organizer_id)
        VALUES (?, ?, ?, ?, ?, ?)
        ''', (name, description, start_date, end_date, budget, organizer_id))
        self.conn.commit()
        return self.cursor.lastrowid
    
    def create_task(self, title, description, project_id, assigned_to, priority, deadline):
        """Создание задачи"""
        self.cursor.execute('''
        INSERT INTO tasks (title, description, project_id, assigned_to, priority, deadline)
        VALUES (?, ?, ?, ?, ?, ?)
        ''', (title, description, project_id, assigned_to, priority, deadline))
        self.conn.commit()
        return self.cursor.lastrowid
    
    def get_projects(self):
        """Получение всех проектов"""
        self.cursor.execute('''
        SELECT p.*, u.full_name as organizer_name 
        FROM projects p 
        LEFT JOIN users u ON p.organizer_id = u.id 
        ORDER BY p.status, p.end_date
        ''')
        return self.cursor.fetchall()
    
    def get_tasks_by_user(self, user_id):
        """Получение задач для конкретного пользователя"""
        self.cursor.execute('''
        SELECT t.*, p.name as project_name 
        FROM tasks t 
        LEFT JOIN projects p ON t.project_id = p.id 
        WHERE t.assigned_to = ? 
        ORDER BY t.priority DESC, t.deadline
        ''', (user_id,))
        return self.cursor.fetchall()
    
    def update_task_status(self, task_id, status):
        """Обновление статуса задачи"""
        self.cursor.execute('''
        UPDATE tasks SET status = ? WHERE id = ?
        ''', (status, task_id))
        self.conn.commit()
    
    def close(self):
        """Закрытие соединения с БД"""
        self.conn.close()

def init_database():
    """Инициализация базы данных с тестовыми данными"""
    db = Database()
    
    # Создание тестовых пользователей, если их нет
    db.create_user('admin', 'admin123', 'admin', 'Администратор Системы', 'admin@company.com')
    db.create_user('director', 'dir123', 'director', 'Иванов Иван Иванович', 'director@company.com')
    db.create_user('manager1', 'mgr123', 'manager', 'Петров Петр Петрович', 'manager1@company.com')
    db.create_user('worker1', 'wrk123', 'worker', 'Сидоров Алексей', 'worker1@company.com')
    db.create_user('organizer1', 'org123', 'organizer', 'Козлова Мария', 'organizer1@company.com')
    
    # Создание отделов
    db.create_department('Отдел разработки', 2)
    db.create_department('Отдел маркетинга', 3)
    
    # Создание проектов
    db.create_project(
        'Разработка новой системы',
        'Создание системы управления проектами',
        '2024-01-01',
        '2024-06-30',
        500000,
        5
    )
    
    db.close()
    print("База данных инициализирована!")

if __name__ == "__main__":
    init_database()