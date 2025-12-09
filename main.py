import tkinter as tk
from tkinter import ttk, messagebox
from database import Database
import sys

class LoginWindow:
    """Окно авторизации"""
    def __init__(self, root, on_login_success):
        self.root = root
        self.root.title("Авторизация")
        self.root.geometry("400x300")
        self.on_login_success = on_login_success
        
        # Центрирование окна
        self.center_window()
        
        # Создание элементов интерфейса
        self.create_widgets()
        
    def center_window(self):
        """Центрирование окна на экране"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def create_widgets(self):
        """Создание элементов интерфейса авторизации"""
        # Фрейм для элементов
        frame = ttk.Frame(self.root, padding="20")
        frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Заголовок
        ttk.Label(frame, text="Система учета персонала", 
                 font=('Arial', 16, 'bold')).grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Поле логина
        ttk.Label(frame, text="Логин:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.username_entry = ttk.Entry(frame, width=30)
        self.username_entry.grid(row=1, column=1, pady=5, padx=(10, 0))
        
        # Поле пароля
        ttk.Label(frame, text="Пароль:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.password_entry = ttk.Entry(frame, width=30, show="*")
        self.password_entry.grid(row=2, column=1, pady=5, padx=(10, 0))
        
        # Кнопка входа
        login_btn = ttk.Button(frame, text="Войти", command=self.login)
        login_btn.grid(row=3, column=0, columnspan=2, pady=20)
        
        # Подсказка
        ttk.Label(frame, text="Тестовые данные:\nadmin / admin123", 
                 font=('Arial', 8), foreground="gray").grid(row=4, column=0, columnspan=2)
    
    def login(self):
        """Обработка попытки входа"""
        username = self.username_entry.get()
        password = self.password_entry.get()
        
        if not username or not password:
            messagebox.showerror("Ошибка", "Заполните все поля!")
            return
        
        db = Database()
        user_data = db.authenticate_user(username, password)
        db.close()
        
        if user_data:
            self.root.destroy()
            self.on_login_success(user_data)
        else:
            messagebox.showerror("Ошибка", "Неверный логин или пароль!")

class MainApplication:
    """Главное окно приложения"""
    def __init__(self, user_data):
        self.user_data = user_data
        self.user_id, self.username, self.role, self.full_name = user_data
        
        self.root = tk.Tk()
        self.root.title(f"Система учета - {self.full_name} ({self.role})")
        self.root.geometry("1200x700")
        
        self.db = Database()
        self.setup_ui()
        
    def setup_ui(self):
        """Настройка пользовательского интерфейса"""
        # Создание меню
        self.create_menu()
        
        # Панель статуса
        self.create_status_bar()
        
        # Основная область
        self.create_main_area()
        
        # Загрузка данных в зависимости от роли
        self.load_role_specific_data()
    
    def create_menu(self):
        """Создание меню приложения"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # Меню "Файл"
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Файл", menu=file_menu)
        file_menu.add_command(label="Выход", command=self.exit_app)
        
        # Меню "Справочники" (только для админов и директоров)
        if self.role in ['admin', 'director']:
            reference_menu = tk.Menu(menubar, tearoff=0)
            menubar.add_cascade(label="Справочники", menu=reference_menu)
            reference_menu.add_command(label="Пользователи", command=self.show_users)
            reference_menu.add_command(label="Отделы", command=self.show_departments)
        
        # Меню "Проекты"
        project_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Проекты", menu=project_menu)
        project_menu.add_command(label="Все проекты", command=self.show_projects)
        
        if self.role in ['admin', 'director', 'organizer']:
            project_menu.add_command(label="Новый проект", command=self.create_project)
        
        # Меню "Задачи"
        task_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Задачи", menu=task_menu)
        task_menu.add_command(label="Мои задачи", command=self.show_my_tasks)
        
        if self.role in ['admin', 'director', 'manager']:
            task_menu.add_command(label="Назначить задачу", command=self.assign_task)
        
        # Меню "Помощь"
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Помощь", menu=help_menu)
        help_menu.add_command(label="О программе", command=self.show_about)
    
    def create_status_bar(self):
        """Создание строки статуса"""
        status_frame = ttk.Frame(self.root)
        status_frame.pack(side=tk.BOTTOM, fill=tk.X)
        
        ttk.Label(status_frame, text=f"Пользователь: {self.full_name} | Роль: {self.role}",
                 relief=tk.SUNKEN, anchor=tk.W).pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        ttk.Button(status_frame, text="Выход", command=self.exit_app).pack(side=tk.RIGHT, padx=5)
    
    def create_main_area(self):
        """Создание основной области"""
        # Панель с вкладками
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Вкладка "Дашборд"
        self.dashboard_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.dashboard_tab, text="Дашборд")
        
        # Вкладка "Проекты"
        self.projects_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.projects_tab, text="Проекты")
        
        # Вкладка "Задачи"
        self.tasks_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.tasks_tab, text="Задачи")
    
    def load_role_specific_data(self):
        """Загрузка данных в зависимости от роли пользователя"""
        # Дашборд
        self.load_dashboard()
        
        # Проекты
        self.load_projects()
        
        # Задачи
        self.load_tasks()
    
    def load_dashboard(self):
        """Загрузка дашборда"""
        for widget in self.dashboard_tab.winfo_children():
            widget.destroy()
        
        frame = ttk.Frame(self.dashboard_tab, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Приветствие
        welcome_text = f"Добро пожаловать, {self.full_name}!\n\n"
        welcome_text += f"Ваша роль: {self.get_role_name()}\n"
        welcome_text += f"Дата входа: {self.get_current_date()}"
        
        ttk.Label(frame, text=welcome_text, font=('Arial', 12)).pack(anchor=tk.W, pady=(0, 20))
        
        # Статистика в зависимости от роли
        if self.role == 'worker':
            tasks = self.db.get_tasks_by_user(self.user_id)
            active_tasks = [t for t in tasks if t[6] == 'active']
            
            stats_text = f"Ваши задачи:\n"
            stats_text += f"Всего: {len(tasks)}\n"
            stats_text += f"Активные: {len(active_tasks)}\n"
            stats_text += f"Выполнено: {len(tasks) - len(active_tasks)}"
            
        elif self.role == 'manager':
            users = self.db.get_all_users()
            workers = [u for u in users if u[2] == 'worker']
            
            stats_text = f"Статистика:\n"
            stats_text += f"Всего сотрудников: {len(workers)}\n"
            stats_text += f"Всего пользователей: {len(users)}"
            
        else:
            stats_text = "Используйте меню для навигации по системе"
        
        ttk.Label(frame, text=stats_text, font=('Arial', 11)).pack(anchor=tk.W)
    
    def load_projects(self):
        """Загрузка списка проектов"""
        for widget in self.projects_tab.winfo_children():
            widget.destroy()
        
        frame = ttk.Frame(self.projects_tab)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Заголовок
        ttk.Label(frame, text="Список проектов", font=('Arial', 14, 'bold')).pack(anchor=tk.W, pady=(0, 10))
        
        # Таблица проектов
        columns = ("ID", "Название", "Организатор", "Дата начала", "Дата окончания", "Бюджет", "Статус")
        tree = ttk.Treeview(frame, columns=columns, show="headings", height=15)
        
        # Настройка колонок
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=100)
        
        tree.column("Название", width=200)
        tree.column("Организатор", width=150)
        
        # Добавление данных
        projects = self.db.get_projects()
        for project in projects:
            tree.insert("", tk.END, values=project)
        
        # Полоса прокрутки
        scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscroll=scrollbar.set)
        
        # Размещение
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def load_tasks(self):
        """Загрузка задач пользователя"""
        for widget in self.tasks_tab.winfo_children():
            widget.destroy()
        
        frame = ttk.Frame(self.tasks_tab)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Заголовок
        ttk.Label(frame, text="Мои задачи", font=('Arial', 14, 'bold')).pack(anchor=tk.W, pady=(0, 10))
        
        # Таблица задач
        columns = ("ID", "Задача", "Проект", "Приоритет", "Дедлайн", "Статус")
        tree = ttk.Treeview(frame, columns=columns, show="headings", height=15)
        
        # Настройка колонок
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=100)
        
        tree.column("Задача", width=250)
        tree.column("Проект", width=150)
        
        # Добавление данных
        tasks = self.db.get_tasks_by_user(self.user_id)
        for task in tasks:
            tree.insert("", tk.END, values=task[:6])
        
        # Полоса прокрутки
        scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscroll=scrollbar.set)
        
        # Размещение
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Кнопки для рабочих
        if self.role == 'worker':
            btn_frame = ttk.Frame(frame)
            btn_frame.pack(pady=10)
            
            ttk.Button(btn_frame, text="Отметить как выполненную", 
                      command=lambda: self.update_task_status(tree)).pack(side=tk.LEFT, padx=5)
    
    def show_users(self):
        """Показать список пользователей"""
        users_window = tk.Toplevel(self.root)
        users_window.title("Список пользователей")
        users_window.geometry("800x500")
        
        frame = ttk.Frame(users_window)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        columns = ("ID", "Логин", "Роль", "ФИО", "Email", "Телефон", "Дата регистрации")
        tree = ttk.Treeview(frame, columns=columns, show="headings", height=20)
        
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=100)
        
        users = self.db.get_all_users()
        for user in users:
            tree.insert("", tk.END, values=user[:7])
        
        scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscroll=scrollbar.set)
        
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def show_projects(self):
        """Показать окно проектов"""
        self.notebook.select(1)  # Переключиться на вкладку проектов
    
    def show_my_tasks(self):
        """Показать окно задач"""
        self.notebook.select(2)  # Переключиться на вкладку задач
    
    def create_project(self):
        """Создание нового проекта"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Новый проект")
        dialog.geometry("500x400")
        
        ttk.Label(dialog, text="Создание нового проекта", font=('Arial', 12, 'bold')).pack(pady=10)
        
        # Форма
        fields_frame = ttk.Frame(dialog, padding="20")
        fields_frame.pack()
        
        ttk.Label(fields_frame, text="Название:").grid(row=0, column=0, sticky=tk.W, pady=5)
        name_entry = ttk.Entry(fields_frame, width=40)
        name_entry.grid(row=0, column=1, pady=5)
        
        ttk.Label(fields_frame, text="Описание:").grid(row=1, column=0, sticky=tk.W, pady=5)
        desc_entry = tk.Text(fields_frame, width=40, height=5)
        desc_entry.grid(row=1, column=1, pady=5)
        
        ttk.Label(fields_frame, text="Бюджет:").grid(row=2, column=0, sticky=tk.W, pady=5)
        budget_entry = ttk.Entry(fields_frame, width=40)
        budget_entry.grid(row=2, column=1, pady=5)
        
        # Кнопки
        btn_frame = ttk.Frame(dialog)
        btn_frame.pack(pady=20)
        
        ttk.Button(btn_frame, text="Создать", command=lambda: self.save_project(
            name_entry.get(), desc_entry.get("1.0", tk.END), budget_entry.get(), dialog
        )).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(btn_frame, text="Отмена", command=dialog.destroy).pack(side=tk.LEFT, padx=5)
    
    def save_project(self, name, description, budget, dialog):
        """Сохранение проекта"""
        if not name:
            messagebox.showerror("Ошибка", "Введите название проекта!")
            return
        
        try:
            budget = float(budget) if budget else 0
        except ValueError:
            messagebox.showerror("Ошибка", "Бюджет должен быть числом!")
            return
        
        project_id = self.db.create_project(
            name=name,
            description=description,
            start_date="2024-01-01",
            end_date="2024-12-31",
            budget=budget,
            organizer_id=self.user_id
        )
        
        if project_id:
            messagebox.showinfo("Успех", "Проект успешно создан!")
            dialog.destroy()
            self.load_projects()
    
    def assign_task(self):
        """Назначение задачи"""
        messagebox.showinfo("Информация", "Функция назначения задач будет реализована в следующей версии")
    
    def update_task_status(self, tree):
        """Обновление статуса задачи"""
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("Внимание", "Выберите задачу!")
            return
        
        task_id = tree.item(selected[0])['values'][0]
        self.db.update_task_status(task_id, 'completed')
        messagebox.showinfo("Успех", "Статус задачи обновлен!")
        self.load_tasks()
    
    def get_role_name(self):
        """Получение названия роли на русском"""
        role_names = {
            'admin': 'Администратор',
            'director': 'Директор',
            'manager': 'Менеджер',
            'worker': 'Работник',
            'organizer': 'Организатор'
        }
        return role_names.get(self.role, self.role)
    
    def get_current_date(self):
        """Получение текущей даты"""
        from datetime import datetime
        return datetime.now().strftime("%d.%m.%Y %H:%M")
    
    def show_about(self):
        """Показать информацию о программе"""
        about_text = """Система учета персонала и проектов
        
Версия 1.0
        
Разработано для демонстрационного экзамена
Роли пользователей:
- Администратор: полный доступ
- Директор: управление отделами
- Менеджер: управление задачами
- Работник: выполнение задач
- Организатор: управление проектами"""
        
        messagebox.showinfo("О программе", about_text)
    
    def show_departments(self):
        """Показать отделы"""
        messagebox.showinfo("Информация", "Функция просмотра отделов будет реализована в следующей версии")
    
    def exit_app(self):
        """Выход из приложения"""
        if messagebox.askyesno("Выход", "Вы уверены, что хотите выйти?"):
            self.db.close()
            self.root.quit()
    
    def run(self):
        """Запуск приложения"""
        self.root.mainloop()

def main():
    """Главная функция"""
    # Инициализация базы данных
    from database import init_database
    init_database()
    
    # Создание корневого окна для авторизации
    login_root = tk.Tk()
    
    def on_login_success(user_data):
        """Обработчик успешного входа"""
        app = MainApplication(user_data)
        app.run()
    
    login_app = LoginWindow(login_root, on_login_success)
    login_root.mainloop()

if __name__ == "__main__":
    main()