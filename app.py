# furniture_shop_with_orders.py
import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime

class FurnitureShop:
    def __init__(self, root):
        self.root = root
        self.root.title("🏠 Мебельный магазин - Полная версия")
        self.root.geometry("1300x750")
        
        # Настройка цветовой схемы
        self.colors = {
            'bg': '#f5f5f5',
            'primary': '#2c3e50',
            'secondary': '#3498db',
            'success': '#27ae60',
            'warning': '#e74c3c',
            'light': '#ecf0f1',
            'white': '#ffffff',
            'text': '#34495e',
            'border': '#bdc3c7',
            'gold': '#f1c40f'
        }
        
        # Настройка стилей
        self.setup_styles()
        
        # База данных
        self.conn = sqlite3.connect('furniture_shop.db')
        self.cursor = self.conn.cursor()
        self.create_db()
        self.add_test_data()
        
        # Текущий заказ
        self.current_order = {
            'customer_id': None,
            'customer_name': None,
            'items': [],
            'total': 0
        }
        
        # Создание интерфейса
        self.create_widgets()
        self.load_data()
    
    def setup_styles(self):
        """Настройка стилей"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Настройка цветов
        self.root.configure(bg=self.colors['bg'])
        
        # Стиль для кнопок
        style.configure('Primary.TButton', 
                       background=self.colors['secondary'],
                       foreground='white',
                       borderwidth=0,
                       focusthickness=0,
                       font=('Segoe UI', 10))
        style.map('Primary.TButton',
                 background=[('active', '#2980b9')])
        
        # Стиль для успешных действий
        style.configure('Success.TButton',
                       background=self.colors['success'],
                       foreground='white',
                       borderwidth=0,
                       font=('Segoe UI', 10, 'bold'))
        style.map('Success.TButton',
                 background=[('active', '#219a52')])
        
        # Стиль для заголовков
        style.configure('Heading.TLabel',
                       font=('Segoe UI', 16, 'bold'),
                       foreground=self.colors['primary'],
                       background=self.colors['bg'])
        
        # Стиль для таблиц
        style.configure('Treeview',
                       background=self.colors['white'],
                       foreground=self.colors['text'],
                       rowheight=30,
                       fieldbackground=self.colors['white'],
                       font=('Segoe UI', 10))
        style.configure('Treeview.Heading',
                       background=self.colors['primary'],
                       foreground='white',
                       font=('Segoe UI', 10, 'bold'),
                       borderwidth=1)
        style.map('Treeview.Heading',
                 background=[('active', self.colors['secondary'])])
        
        # Стиль для вкладок
        style.configure('TNotebook',
                       background=self.colors['bg'],
                       borderwidth=0)
        style.configure('TNotebook.Tab',
                       background=self.colors['light'],
                       foreground=self.colors['text'],
                       padding=[20, 8],
                       font=('Segoe UI', 10))
        style.map('TNotebook.Tab',
                 background=[('selected', self.colors['white'])],
                 foreground=[('selected', self.colors['primary'])])
    
    def create_db(self):
        """Создание таблиц"""
        self.cursor.executescript('''
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL
            );
            
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                price REAL NOT NULL,
                stock INTEGER DEFAULT 0,
                category_id INTEGER,
                material TEXT,
                color TEXT,
                description TEXT,
                FOREIGN KEY (category_id) REFERENCES categories (id)
            );
            
            CREATE TABLE IF NOT EXISTS customers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                phone TEXT,
                email TEXT UNIQUE
            );
            
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_id INTEGER,
                order_date TEXT,
                total_amount REAL,
                status TEXT DEFAULT 'Новый',
                payment_method TEXT,
                FOREIGN KEY (customer_id) REFERENCES customers (id)
            );
            
            CREATE TABLE IF NOT EXISTS order_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_id INTEGER,
                product_id INTEGER,
                quantity INTEGER,
                price_per_unit REAL,
                subtotal REAL,
                FOREIGN KEY (order_id) REFERENCES orders (id),
                FOREIGN KEY (product_id) REFERENCES products (id)
            );
        ''')
        self.conn.commit()
    
    def add_test_data(self):
        """Добавление тестовых данных"""
        # Категории
        self.cursor.execute("SELECT COUNT(*) FROM categories")
        if self.cursor.fetchone()[0] == 0:
            categories = ['Диваны', 'Кресла', 'Столы', 'Стулья', 'Шкафы', 'Кровати', 'Матрасы', 'Комоды']
            for cat in categories:
                self.cursor.execute("INSERT INTO categories (name) VALUES (?)", (cat,))
        
        # Товары
        self.cursor.execute("SELECT COUNT(*) FROM products")
        if self.cursor.fetchone()[0] == 0:
            products = [
                ('Диван "Комфорт"', 45000, 5, 1, 'Ткань, дерево', 'Бежевый', 'Мягкий удобный диван'),
                ('Диван "Престиж"', 65000, 3, 1, 'Кожа, дерево', 'Коричневый', 'Кожаный диван'),
                ('Диван "Маленький"', 25000, 7, 1, 'Ткань', 'Серый', 'Компактный диван'),
                ('Кресло "Релакс"', 15000, 8, 2, 'Ткань, металл', 'Серый', 'Удобное кресло'),
                ('Кресло-качалка', 18000, 4, 2, 'Дерево', 'Натуральный', 'Для уюта'),
                ('Стол обеденный', 25000, 4, 3, 'Дерево', 'Дуб', 'Большой стол'),
                ('Стол компьютерный', 12000, 6, 3, 'ЛДСП', 'Белый', 'С полками'),
                ('Стул деревянный', 5000, 15, 4, 'Дерево', 'Натуральный', 'Удобный стул'),
                ('Стул мягкий', 7000, 10, 4, 'Ткань, металл', 'Синий', 'С подлокотниками'),
                ('Шкаф-купе', 55000, 2, 5, 'ЛДСП', 'Белый', 'Вместительный шкаф'),
                ('Шкаф для одежды', 35000, 3, 5, 'Дерево', 'Венге', 'С зеркалом'),
                ('Кровать двуспальная', 35000, 3, 6, 'Дерево', 'Венге', 'Спальная кровать'),
                ('Кровать односпальная', 18000, 5, 6, 'Металл', 'Белый', 'Для подростка'),
                ('Матрас ортопедический', 15000, 8, 7, 'Пена', 'Белый', 'Жесткий'),
                ('Матрас мягкий', 10000, 6, 7, 'Пружины', 'Бежевый', 'Мягкий'),
                ('Комод', 22000, 4, 8, 'Дерево', 'Дуб', '6 ящиков')
            ]
            for p in products:
                self.cursor.execute('''
                    INSERT INTO products (name, price, stock, category_id, material, color, description)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', p)
        
        # Клиенты
        self.cursor.execute("SELECT COUNT(*) FROM customers")
        if self.cursor.fetchone()[0] == 0:
            customers = [
                ('Иван', 'Петров', '+7 (999) 123-45-67', 'ivan@mail.com'),
                ('Мария', 'Иванова', '+7 (999) 765-43-21', 'maria@mail.com'),
                ('Петр', 'Сидоров', '+7 (999) 555-55-55', 'petr@mail.com'),
                ('Анна', 'Козлова', '+7 (999) 111-22-33', 'anna@mail.com'),
                ('Сергей', 'Смирнов', '+7 (999) 444-55-66', 'sergey@mail.com'),
                ('Елена', 'Попова', '+7 (999) 777-88-99', 'elena@mail.com')
            ]
            for c in customers:
                self.cursor.execute('''
                    INSERT INTO customers (first_name, last_name, phone, email)
                    VALUES (?, ?, ?, ?)
                ''', c)
        
        self.conn.commit()
    
    def create_widgets(self):
        """Создание интерфейса"""
        # Заголовок
        title_frame = tk.Frame(self.root, bg=self.colors['primary'], height=70)
        title_frame.pack(fill='x')
        title_frame.pack_propagate(False)
        
        title_label = tk.Label(title_frame, 
                              text="🏠 МЕБЕЛЬНЫЙ МАГАЗИН - СИСТЕМА УПРАВЛЕНИЯ",
                              font=('Segoe UI', 18, 'bold'),
                              bg=self.colors['primary'],
                              fg='white')
        title_label.pack(expand=True)
        
        # Вкладки
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Создание вкладок
        self.create_products_tab()
        self.create_customers_tab()
        self.create_categories_tab()
        self.create_orders_tab()
        self.create_new_order_tab()
    
    def create_products_tab(self):
        """Вкладка товаров"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text='📦 Товары')
        
        # Верхняя панель
        top_frame = tk.Frame(frame, bg=self.colors['white'], height=90)
        top_frame.pack(fill='x', padx=10, pady=10)
        top_frame.pack_propagate(False)
        
        # Кнопки действий
        btn_frame = tk.Frame(top_frame, bg=self.colors['white'])
        btn_frame.pack(side='left', padx=10)
        
        buttons = [
            ('➕ Добавить', self.add_product, self.colors['success']),
            ('✏️ Редактировать', self.edit_product, self.colors['secondary']),
            ('🗑️ Удалить', self.delete_product, self.colors['warning']),
            ('🔄 Обновить', self.load_products, self.colors['primary']),
            ('🛒 В заказ', self.add_to_order_from_products, self.colors['gold'])
        ]
        
        for text, command, color in buttons:
            btn = tk.Button(btn_frame, text=text, command=command,
                          bg=color, fg='white' if color != self.colors['gold'] else 'black',
                          font=('Segoe UI', 10, 'bold' if color == self.colors['gold'] else 'normal'),
                          padx=15, pady=5, borderwidth=0, cursor='hand2')
            btn.pack(side='left', padx=2)
            
            # Эффект при наведении
            btn.bind('<Enter>', lambda e, b=btn: b.configure(bg='#34495e' if b['bg'] != self.colors['gold'] else '#d4ac0d'))
            btn.bind('<Leave>', lambda e, b=btn, c=color: b.configure(bg=c))
        
        # Поиск
        search_frame = tk.Frame(top_frame, bg=self.colors['white'])
        search_frame.pack(side='right', padx=10)
        
        tk.Label(search_frame, text="🔍 Поиск:", 
                bg=self.colors['white'], font=('Segoe UI', 10)).pack(side='left')
        
        self.search_entry = tk.Entry(search_frame, font=('Segoe UI', 10),
                                    width=20, bd=1, relief='solid')
        self.search_entry.pack(side='left', padx=5)
        
        tk.Button(search_frame, text="Найти", command=self.search_products,
                 bg=self.colors['secondary'], fg='white', font=('Segoe UI', 10),
                 padx=10, borderwidth=0, cursor='hand2').pack(side='left')
        
        # Фильтр по категории
        tk.Label(search_frame, text="📋 Категория:", 
                bg=self.colors['white'], font=('Segoe UI', 10)).pack(side='left', padx=(20,5))
        
        self.category_filter = ttk.Combobox(search_frame, width=15, font=('Segoe UI', 10))
        self.category_filter.pack(side='left')
        self.category_filter.bind('<<ComboboxSelected>>', self.filter_by_category)
        self.load_categories_filter()
        
        # Таблица товаров
        table_frame = tk.Frame(frame, bg=self.colors['white'], bd=1, relief='solid')
        table_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        columns = ('ID', '📦 Название', '💰 Цена', '📊 В наличии', '📋 Категория', '🔨 Материал', '🎨 Цвет')
        self.products_tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=15)
        
        # Заголовки
        for col in columns:
            self.products_tree.heading(col, text=col)
        
        # Ширина колонок
        self.products_tree.column('ID', width=50, anchor='center')
        self.products_tree.column('📦 Название', width=250)
        self.products_tree.column('💰 Цена', width=120, anchor='e')
        self.products_tree.column('📊 В наличии', width=100, anchor='center')
        self.products_tree.column('📋 Категория', width=150)
        self.products_tree.column('🔨 Материал', width=150)
        self.products_tree.column('🎨 Цвет', width=120)
        
        # Двойной клик для добавления в заказ
        self.products_tree.bind('<Double-1>', lambda e: self.add_to_order_from_products())
        
        # Скролл
        scroll = ttk.Scrollbar(table_frame, orient='vertical', command=self.products_tree.yview)
        self.products_tree.configure(yscrollcommand=scroll.set)
        
        self.products_tree.pack(side='left', fill='both', expand=True)
        scroll.pack(side='right', fill='y')
    
    def create_customers_tab(self):
        """Вкладка клиентов"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text='👥 Клиенты')
        
        # Верхняя панель
        top_frame = tk.Frame(frame, bg=self.colors['white'], height=60)
        top_frame.pack(fill='x', padx=10, pady=10)
        top_frame.pack_propagate(False)
        
        # Кнопки
        btn_frame = tk.Frame(top_frame, bg=self.colors['white'])
        btn_frame.pack(side='left', padx=10)
        
        buttons = [
            ('➕ Добавить', self.add_customer, self.colors['success']),
            ('✏️ Редактировать', self.edit_customer, self.colors['secondary']),
            ('🗑️ Удалить', self.delete_customer, self.colors['warning']),
            ('🔄 Обновить', self.load_customers, self.colors['primary']),
            ('📝 Новый заказ', self.create_order_for_customer, self.colors['gold'])
        ]
        
        for text, command, color in buttons:
            btn = tk.Button(btn_frame, text=text, command=command,
                          bg=color, fg='white' if color != self.colors['gold'] else 'black',
                          font=('Segoe UI', 10, 'bold' if color == self.colors['gold'] else 'normal'),
                          padx=15, pady=5, borderwidth=0, cursor='hand2')
            btn.pack(side='left', padx=2)
            
            btn.bind('<Enter>', lambda e, b=btn: b.configure(bg='#34495e' if b['bg'] != self.colors['gold'] else '#d4ac0d'))
            btn.bind('<Leave>', lambda e, b=btn, c=color: b.configure(bg=c))
        
        # Поиск
        search_frame = tk.Frame(top_frame, bg=self.colors['white'])
        search_frame.pack(side='right', padx=10)
        
        tk.Label(search_frame, text="🔍 Поиск:", 
                bg=self.colors['white'], font=('Segoe UI', 10)).pack(side='left')
        
        self.customer_search = tk.Entry(search_frame, font=('Segoe UI', 10),
                                       width=20, bd=1, relief='solid')
        self.customer_search.pack(side='left', padx=5)
        
        tk.Button(search_frame, text="Найти", command=self.search_customers,
                 bg=self.colors['secondary'], fg='white', font=('Segoe UI', 10),
                 padx=10, borderwidth=0, cursor='hand2').pack(side='left')
        
        # Таблица клиентов
        table_frame = tk.Frame(frame, bg=self.colors['white'], bd=1, relief='solid')
        table_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        columns = ('ID', '👤 Имя', '👤 Фамилия', '📞 Телефон', '✉️ Email')
        self.customers_tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=15)
        
        # Заголовки
        for col in columns:
            self.customers_tree.heading(col, text=col)
        
        # Ширина колонок
        self.customers_tree.column('ID', width=50, anchor='center')
        self.customers_tree.column('👤 Имя', width=150)
        self.customers_tree.column('👤 Фамилия', width=150)
        self.customers_tree.column('📞 Телефон', width=150)
        self.customers_tree.column('✉️ Email', width=250)
        
        # Двойной клик для создания заказа
        self.customers_tree.bind('<Double-1>', lambda e: self.create_order_for_customer())
        
        # Скролл
        scroll = ttk.Scrollbar(table_frame, orient='vertical', command=self.customers_tree.yview)
        self.customers_tree.configure(yscrollcommand=scroll.set)
        
        self.customers_tree.pack(side='left', fill='both', expand=True)
        scroll.pack(side='right', fill='y')
    
    def create_categories_tab(self):
        """Вкладка категорий"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text='🏷️ Категории')
        
        # Верхняя панель
        top_frame = tk.Frame(frame, bg=self.colors['white'], height=60)
        top_frame.pack(fill='x', padx=10, pady=10)
        top_frame.pack_propagate(False)
        
        # Кнопки
        btn_frame = tk.Frame(top_frame, bg=self.colors['white'])
        btn_frame.pack(side='left', padx=10)
        
        buttons = [
            ('➕ Добавить', self.add_category, self.colors['success']),
            ('🗑️ Удалить', self.delete_category, self.colors['warning']),
            ('🔄 Обновить', self.load_categories, self.colors['primary'])
        ]
        
        for text, command, color in buttons:
            btn = tk.Button(btn_frame, text=text, command=command,
                          bg=color, fg='white', font=('Segoe UI', 10),
                          padx=15, pady=5, borderwidth=0, cursor='hand2')
            btn.pack(side='left', padx=2)
            
            btn.bind('<Enter>', lambda e, b=btn: b.configure(bg='#34495e'))
            btn.bind('<Leave>', lambda e, b=btn, c=color: b.configure(bg=c))
        
        # Таблица категорий
        table_frame = tk.Frame(frame, bg=self.colors['white'], bd=1, relief='solid')
        table_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        columns = ('ID', '🏷️ Категория', '📦 Товаров')
        self.categories_tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=15)
        
        # Заголовки
        self.categories_tree.heading('ID', text='ID')
        self.categories_tree.heading('🏷️ Категория', text='Категория')
        self.categories_tree.heading('📦 Товаров', text='Кол-во товаров')
        
        # Ширина колонок
        self.categories_tree.column('ID', width=100, anchor='center')
        self.categories_tree.column('🏷️ Категория', width=300)
        self.categories_tree.column('📦 Товаров', width=200, anchor='center')
        
        # Скролл
        scroll = ttk.Scrollbar(table_frame, orient='vertical', command=self.categories_tree.yview)
        self.categories_tree.configure(yscrollcommand=scroll.set)
        
        self.categories_tree.pack(side='left', fill='both', expand=True)
        scroll.pack(side='right', fill='y')
    
    def create_orders_tab(self):
        """Вкладка заказов"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text='📋 Заказы')
        
        # Верхняя панель
        top_frame = tk.Frame(frame, bg=self.colors['white'], height=60)
        top_frame.pack(fill='x', padx=10, pady=10)
        top_frame.pack_propagate(False)
        
        # Кнопки
        btn_frame = tk.Frame(top_frame, bg=self.colors['white'])
        btn_frame.pack(side='left', padx=10)
        
        buttons = [
            ('🔄 Обновить', self.load_orders, self.colors['primary']),
            ('📊 Статус', self.change_order_status, self.colors['secondary']),
            ('🔍 Детали', self.view_order_details, self.colors['gold'])
        ]
        
        for text, command, color in buttons:
            btn = tk.Button(btn_frame, text=text, command=command,
                          bg=color, fg='white' if color != self.colors['gold'] else 'black',
                          font=('Segoe UI', 10),
                          padx=15, pady=5, borderwidth=0, cursor='hand2')
            btn.pack(side='left', padx=2)
            
            btn.bind('<Enter>', lambda e, b=btn: b.configure(bg='#34495e' if b['bg'] != self.colors['gold'] else '#d4ac0d'))
            btn.bind('<Leave>', lambda e, b=btn, c=color: b.configure(bg=c))
        
        # Фильтр по статусу
        filter_frame = tk.Frame(top_frame, bg=self.colors['white'])
        filter_frame.pack(side='right', padx=10)
        
        tk.Label(filter_frame, text="Статус:", 
                bg=self.colors['white'], font=('Segoe UI', 10)).pack(side='left')
        
        self.status_filter = ttk.Combobox(filter_frame, values=['Все', 'Новый', 'В обработке', 'Доставлен', 'Отменен'], 
                                         width=12, font=('Segoe UI', 10))
        self.status_filter.set('Все')
        self.status_filter.pack(side='left', padx=5)
        self.status_filter.bind('<<ComboboxSelected>>', self.filter_orders_by_status)
        
        # Таблица заказов
        table_frame = tk.Frame(frame, bg=self.colors['white'], bd=1, relief='solid')
        table_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        columns = ('№', '📅 Дата', '👤 Клиент', '💰 Сумма', '📊 Статус', '💳 Оплата')
        self.orders_tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=15)
        
        # Заголовки
        self.orders_tree.heading('№', text='№ заказа')
        self.orders_tree.heading('📅 Дата', text='Дата')
        self.orders_tree.heading('👤 Клиент', text='Клиент')
        self.orders_tree.heading('💰 Сумма', text='Сумма')
        self.orders_tree.heading('📊 Статус', text='Статус')
        self.orders_tree.heading('💳 Оплата', text='Оплата')
        
        # Ширина колонок
        self.orders_tree.column('№', width=80, anchor='center')
        self.orders_tree.column('📅 Дата', width=150)
        self.orders_tree.column('👤 Клиент', width=250)
        self.orders_tree.column('💰 Сумма', width=120, anchor='e')
        self.orders_tree.column('📊 Статус', width=120, anchor='center')
        self.orders_tree.column('💳 Оплата', width=120, anchor='center')
        
        # Двойной клик для просмотра деталей
        self.orders_tree.bind('<Double-1>', lambda e: self.view_order_details())
        
        # Скролл
        scroll = ttk.Scrollbar(table_frame, orient='vertical', command=self.orders_tree.yview)
        self.orders_tree.configure(yscrollcommand=scroll.set)
        
        self.orders_tree.pack(side='left', fill='both', expand=True)
        scroll.pack(side='right', fill='y')
    
    def create_new_order_tab(self):
        """Вкладка создания нового заказа"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text='🛒 Новый заказ')
        
        # Информация о клиенте
        customer_frame = tk.Frame(frame, bg=self.colors['white'], bd=1, relief='solid')
        customer_frame.pack(fill='x', padx=10, pady=10)
        
        tk.Label(customer_frame, text="👤 КЛИЕНТ", 
                font=('Segoe UI', 12, 'bold'),
                bg=self.colors['white'],
                fg=self.colors['primary']).pack(anchor='w', padx=10, pady=5)
        
        customer_info_frame = tk.Frame(customer_frame, bg=self.colors['white'])
        customer_info_frame.pack(fill='x', padx=10, pady=5)
        
        self.customer_label = tk.Label(customer_info_frame, 
                                      text="Клиент не выбран",
                                      font=('Segoe UI', 11),
                                      bg=self.colors['white'],
                                      fg=self.colors['warning'])
        self.customer_label.pack(side='left')
        
        tk.Button(customer_info_frame, text="Выбрать клиента", 
                 command=self.choose_customer,
                 bg=self.colors['secondary'], fg='white',
                 font=('Segoe UI', 10), padx=15, pady=3,
                 borderwidth=0, cursor='hand2').pack(side='right', padx=5)
        
        tk.Button(customer_info_frame, text="➕ Новый клиент", 
                 command=self.add_customer_and_order,
                 bg=self.colors['success'], fg='white',
                 font=('Segoe UI', 10), padx=15, pady=3,
                 borderwidth=0, cursor='hand2').pack(side='right', padx=5)
        
        # Товары в заказе
        items_frame = tk.Frame(frame, bg=self.colors['white'], bd=1, relief='solid')
        items_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        tk.Label(items_frame, text="🛍️ ТОВАРЫ В ЗАКАЗЕ", 
                font=('Segoe UI', 12, 'bold'),
                bg=self.colors['white'],
                fg=self.colors['primary']).pack(anchor='w', padx=10, pady=5)
        
        # Таблица товаров в заказе
        table_frame = tk.Frame(items_frame, bg=self.colors['white'])
        table_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        columns = ('ID', '📦 Товар', '💰 Цена', '🔢 Количество', '💵 Сумма')
        self.order_items_tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=8)
        
        self.order_items_tree.heading('ID', text='ID')
        self.order_items_tree.heading('📦 Товар', text='Товар')
        self.order_items_tree.heading('💰 Цена', text='Цена')
        self.order_items_tree.heading('🔢 Количество', text='Количество')
        self.order_items_tree.heading('💵 Сумма', text='Сумма')
        
        self.order_items_tree.column('ID', width=50, anchor='center')
        self.order_items_tree.column('📦 Товар', width=400)
        self.order_items_tree.column('💰 Цена', width=120, anchor='e')
        self.order_items_tree.column('🔢 Количество', width=100, anchor='center')
        self.order_items_tree.column('💵 Сумма', width=120, anchor='e')
        
        self.order_items_tree.pack(fill='both', expand=True)
        
        # Кнопки управления товарами
        control_frame = tk.Frame(items_frame, bg=self.colors['white'])
        control_frame.pack(fill='x', padx=10, pady=10)
        
        tk.Button(control_frame, text="➕ Добавить товар", 
                 command=self.add_product_from_catalog,
                 bg=self.colors['secondary'], fg='white',
                 font=('Segoe UI', 10), padx=15, pady=5,
                 borderwidth=0, cursor='hand2').pack(side='left', padx=2)
        
        tk.Button(control_frame, text="🗑️ Удалить", 
                 command=self.remove_from_order,
                 bg=self.colors['warning'], fg='white',
                 font=('Segoe UI', 10), padx=15, pady=5,
                 borderwidth=0, cursor='hand2').pack(side='left', padx=2)
        
        tk.Button(control_frame, text="🔄 Очистить", 
                 command=self.clear_order,
                 bg=self.colors['primary'], fg='white',
                 font=('Segoe UI', 10), padx=15, pady=5,
                 borderwidth=0, cursor='hand2').pack(side='left', padx=2)
        
        # Итого
        total_frame = tk.Frame(frame, bg=self.colors['white'], bd=1, relief='solid')
        total_frame.pack(fill='x', padx=10, pady=5)
        
        self.total_label = tk.Label(total_frame, 
                                   text="ИТОГО: 0 ₽",
                                   font=('Segoe UI', 16, 'bold'),
                                   bg=self.colors['white'],
                                   fg=self.colors['success'])
        self.total_label.pack(side='left', padx=20, pady=10)
        
        tk.Button(total_frame, text="✅ Оформить заказ", 
                 command=self.complete_order,
                 bg=self.colors['success'], fg='white',
                 font=('Segoe UI', 12, 'bold'), padx=30, pady=8,
                 borderwidth=0, cursor='hand2').pack(side='right', padx=20, pady=10)
    
    # ========== МЕТОДЫ ЗАГРУЗКИ ДАННЫХ ==========
    
    def load_data(self):
        """Загрузка всех данных"""
        self.load_products()
        self.load_customers()
        self.load_categories()
        self.load_orders()
    
    def load_products(self):
        """Загрузка товаров"""
        for row in self.products_tree.get_children():
            self.products_tree.delete(row)
        
        self.cursor.execute('''
            SELECT p.id, p.name, p.price, p.stock, c.name, p.material, p.color
            FROM products p
            LEFT JOIN categories c ON p.category_id = c.id
            ORDER BY p.name
        ''')
        for row in self.cursor.fetchall():
            formatted_row = (
                row[0],
                row[1],
                f"{row[2]:,.0f} ₽",
                f"{row[3]} шт.",
                row[4],
                row[5],
                row[6]
            )
            self.products_tree.insert('', 'end', values=formatted_row)
    
    def load_customers(self):
        """Загрузка клиентов"""
        for row in self.customers_tree.get_children():
            self.customers_tree.delete(row)
        
        self.cursor.execute("SELECT id, first_name, last_name, phone, email FROM customers ORDER BY last_name")
        for row in self.cursor.fetchall():
            self.customers_tree.insert('', 'end', values=row)
    
    def load_categories(self):
        """Загрузка категорий"""
        for row in self.categories_tree.get_children():
            self.categories_tree.delete(row)
        
        self.cursor.execute('''
            SELECT c.id, c.name, COUNT(p.id)
            FROM categories c
            LEFT JOIN products p ON c.id = p.category_id
            GROUP BY c.id
            ORDER BY c.name
        ''')
        for row in self.cursor.fetchall():
            # Добавляем иконку эмодзи в название категории для красоты
            icon = ''
            if 'Диван' in row[1]:
                icon = '🛋️ '
            elif 'Кресл' in row[1]:
                icon = '💺 '
            elif 'Стол' in row[1]:
                icon = '🪑 '
            elif 'Стул' in row[1]:
                icon = '🪑 '
            elif 'Шкаф' in row[1]:
                icon = '🗄️ '
            elif 'Кроват' in row[1]:
                icon = '🛏️ '
            elif 'Матрас' in row[1]:
                icon = '🛏️ '
            elif 'Комод' in row[1]:
                icon = '🗄️ '
            
            self.categories_tree.insert('', 'end', values=(row[0], f"{icon}{row[1]}", row[2]))
    
    def load_orders(self):
        """Загрузка заказов"""
        for row in self.orders_tree.get_children():
            self.orders_tree.delete(row)
        
        self.cursor.execute('''
            SELECT o.id, o.order_date, c.first_name || ' ' || c.last_name,
                   o.total_amount, o.status, o.payment_method
            FROM orders o
            JOIN customers c ON o.customer_id = c.id
            ORDER BY o.id DESC
        ''')
        for row in self.cursor.fetchall():
            payment = row[5] if row[5] else 'Не указан'
            formatted_row = (
                row[0],
                row[1][:16] if row[1] else '',
                row[2],
                f"{row[3]:,.0f} ₽",
                row[4],
                payment
            )
            self.orders_tree.insert('', 'end', values=formatted_row)
    
    def load_categories_filter(self):
        """Загрузка категорий для фильтра"""
        self.cursor.execute("SELECT name FROM categories ORDER BY name")
        categories = [row[0] for row in self.cursor.fetchall()]
        self.category_filter['values'] = ['Все категории'] + categories
        self.category_filter.set('Все категории')
    
    # ========== МЕТОДЫ ПОИСКА И ФИЛЬТРАЦИИ ==========
    
    def search_products(self):
        """Поиск товаров"""
        search_term = self.search_entry.get()
        
        for row in self.products_tree.get_children():
            self.products_tree.delete(row)
        
        self.cursor.execute('''
            SELECT p.id, p.name, p.price, p.stock, c.name, p.material, p.color
            FROM products p
            LEFT JOIN categories c ON p.category_id = c.id
            WHERE p.name LIKE ? OR p.material LIKE ? OR p.color LIKE ? OR p.description LIKE ?
            ORDER BY p.name
        ''', (f'%{search_term}%', f'%{search_term}%', f'%{search_term}%', f'%{search_term}%'))
        
        for row in self.cursor.fetchall():
            formatted_row = (
                row[0],
                row[1],
                f"{row[2]:,.0f} ₽",
                f"{row[3]} шт.",
                row[4],
                row[5],
                row[6]
            )
            self.products_tree.insert('', 'end', values=formatted_row)
    
    def search_customers(self):
        """Поиск клиентов"""
        search_term = self.customer_search.get()
        
        for row in self.customers_tree.get_children():
            self.customers_tree.delete(row)
        
        self.cursor.execute('''
            SELECT id, first_name, last_name, phone, email
            FROM customers
            WHERE first_name LIKE ? OR last_name LIKE ? OR phone LIKE ? OR email LIKE ?
            ORDER BY last_name
        ''', (f'%{search_term}%', f'%{search_term}%', f'%{search_term}%', f'%{search_term}%'))
        
        for row in self.cursor.fetchall():
            self.customers_tree.insert('', 'end', values=row)
    
    def filter_by_category(self, event=None):
        """Фильтр по категории"""
        category = self.category_filter.get()
        
        for row in self.products_tree.get_children():
            self.products_tree.delete(row)
        
        if category == 'Все категории':
            self.load_products()
        else:
            self.cursor.execute('''
                SELECT p.id, p.name, p.price, p.stock, c.name, p.material, p.color
                FROM products p
                LEFT JOIN categories c ON p.category_id = c.id
                WHERE c.name = ?
                ORDER BY p.name
            ''', (category,))
            for row in self.cursor.fetchall():
                formatted_row = (
                    row[0],
                    row[1],
                    f"{row[2]:,.0f} ₽",
                    f"{row[3]} шт.",
                    row[4],
                    row[5],
                    row[6]
                )
                self.products_tree.insert('', 'end', values=formatted_row)
    
    def filter_orders_by_status(self, event=None):
        """Фильтр заказов по статусу"""
        status = self.status_filter.get()
        
        for row in self.orders_tree.get_children():
            self.orders_tree.delete(row)
        
        if status == 'Все':
            self.load_orders()
        else:
            self.cursor.execute('''
                SELECT o.id, o.order_date, c.first_name || ' ' || c.last_name,
                       o.total_amount, o.status, o.payment_method
                FROM orders o
                JOIN customers c ON o.customer_id = c.id
                WHERE o.status = ?
                ORDER BY o.id DESC
            ''', (status,))
            for row in self.cursor.fetchall():
                payment = row[5] if row[5] else 'Не указан'
                formatted_row = (
                    row[0],
                    row[1][:16] if row[1] else '',
                    row[2],
                    f"{row[3]:,.0f} ₽",
                    row[4],
                    payment
                )
                self.orders_tree.insert('', 'end', values=formatted_row)
    
    # ========== МЕТОДЫ УПРАВЛЕНИЯ ТОВАРАМИ ==========
    
    def add_product(self):
        """Диалог добавления товара"""
        dialog = tk.Toplevel(self.root)
        dialog.title("➕ Добавление товара")
        dialog.geometry("500x600")
        dialog.configure(bg=self.colors['white'])
        dialog.grab_set()
        
        # Заголовок
        tk.Label(dialog, text="Добавление нового товара", 
                font=('Segoe UI', 14, 'bold'),
                bg=self.colors['white'],
                fg=self.colors['primary']).pack(pady=15)
        
        # Поля ввода
        fields_frame = tk.Frame(dialog, bg=self.colors['white'])
        fields_frame.pack(padx=30, pady=10)
        
        fields = [
            ('Название товара:', 'entry'),
            ('Цена (₽):', 'entry'),
            ('Количество на складе:', 'entry'),
            ('Категория:', 'combo'),
            ('Материал:', 'entry'),
            ('Цвет:', 'entry'),
            ('Описание:', 'text')
        ]
        
        entries = {}
        row = 0
        
        for label, type_ in fields:
            tk.Label(fields_frame, text=label, 
                    bg=self.colors['white'],
                    font=('Segoe UI', 10)).grid(row=row, column=0, sticky='w', pady=8)
            
            if type_ == 'entry':
                entries[label] = tk.Entry(fields_frame, width=40, font=('Segoe UI', 10),
                                         bd=1, relief='solid')
                entries[label].grid(row=row, column=1, padx=10, pady=5)
            elif type_ == 'combo':
                self.cursor.execute("SELECT name FROM categories")
                categories = [cat[0] for cat in self.cursor.fetchall()]
                entries[label] = ttk.Combobox(fields_frame, values=categories, width=37, font=('Segoe UI', 10))
                entries[label].grid(row=row, column=1, padx=10, pady=5)
            elif type_ == 'text':
                entries[label] = tk.Text(fields_frame, height=4, width=30, font=('Segoe UI', 10),
                                        bd=1, relief='solid')
                entries[label].grid(row=row, column=1, padx=10, pady=5)
            
            row += 1
        
        # Кнопки
        btn_frame = tk.Frame(dialog, bg=self.colors['white'])
        btn_frame.pack(pady=20)
        
        def save():
            try:
                # Получаем ID категории
                self.cursor.execute("SELECT id FROM categories WHERE name=?", 
                                   (entries['Категория:'].get(),))
                category_id = self.cursor.fetchone()[0]
                
                self.cursor.execute('''
                    INSERT INTO products (name, price, stock, category_id, material, color, description)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    entries['Название товара:'].get(),
                    float(entries['Цена (₽):'].get()),
                    int(entries['Количество на складе:'].get()),
                    category_id,
                    entries['Материал:'].get(),
                    entries['Цвет:'].get(),
                    entries['Описание:'].get('1.0', tk.END).strip()
                ))
                
                self.conn.commit()
                self.load_products()
                dialog.destroy()
                messagebox.showinfo("✅ Успех", "Товар успешно добавлен!")
            except Exception as e:
                messagebox.showerror("❌ Ошибка", f"Не удалось добавить товар:\n{str(e)}")
        
        tk.Button(btn_frame, text="💾 Сохранить", command=save,
                 bg=self.colors['success'], fg='white', font=('Segoe UI', 11, 'bold'),
                 padx=30, pady=8, borderwidth=0, cursor='hand2').pack(side='left', padx=5)
        tk.Button(btn_frame, text="✖️ Отмена", command=dialog.destroy,
                 bg=self.colors['warning'], fg='white', font=('Segoe UI', 11, 'bold'),
                 padx=30, pady=8, borderwidth=0, cursor='hand2').pack(side='left', padx=5)
    
    def edit_product(self):
        """Редактирование товара"""
        selected = self.products_tree.selection()
        if not selected:
            messagebox.showwarning("⚠️ Внимание", "Выберите товар для редактирования")
            return
        
        product = self.products_tree.item(selected[0])['values']
        
        dialog = tk.Toplevel(self.root)
        dialog.title("✏️ Редактирование товара")
        dialog.geometry("500x500")
        dialog.configure(bg=self.colors['white'])
        dialog.grab_set()
        
        tk.Label(dialog, text="Редактирование товара", 
                font=('Segoe UI', 14, 'bold'),
                bg=self.colors['white'],
                fg=self.colors['primary']).pack(pady=15)
        
        fields_frame = tk.Frame(dialog, bg=self.colors['white'])
        fields_frame.pack(padx=30, pady=10)
        
        fields = [
            ('Название:', product[1]),
            ('Цена:', str(product[2]).replace(' ₽', '').replace(' ', '')),
            ('Количество:', str(product[3]).replace(' шт.', '')),
            ('Материал:', product[5]),
            ('Цвет:', product[6])
        ]
        
        entries = {}
        row = 0
        
        for label, value in fields:
            tk.Label(fields_frame, text=label, 
                    bg=self.colors['white'],
                    font=('Segoe UI', 10)).grid(row=row, column=0, sticky='w', pady=8)
            
            entries[label] = tk.Entry(fields_frame, width=40, font=('Segoe UI', 10),
                                     bd=1, relief='solid')
            entries[label].insert(0, value)
            entries[label].grid(row=row, column=1, padx=10, pady=5)
            row += 1
        
        def save():
            try:
                self.cursor.execute('''
                    UPDATE products 
                    SET name=?, price=?, stock=?, material=?, color=?
                    WHERE id=?
                ''', (
                    entries['Название:'].get(),
                    float(entries['Цена:'].get()),
                    int(entries['Количество:'].get()),
                    entries['Материал:'].get(),
                    entries['Цвет:'].get(),
                    product[0]
                ))
                
                self.conn.commit()
                self.load_products()
                dialog.destroy()
                messagebox.showinfo("✅ Успех", "Товар обновлен!")
            except Exception as e:
                messagebox.showerror("❌ Ошибка", f"Не удалось обновить товар:\n{str(e)}")
        
        btn_frame = tk.Frame(dialog, bg=self.colors['white'])
        btn_frame.pack(pady=20)
        
        tk.Button(btn_frame, text="💾 Сохранить", command=save,
                 bg=self.colors['success'], fg='white', font=('Segoe UI', 11, 'bold'),
                 padx=30, pady=8, borderwidth=0, cursor='hand2').pack(side='left', padx=5)
        tk.Button(btn_frame, text="✖️ Отмена", command=dialog.destroy,
                 bg=self.colors['warning'], fg='white', font=('Segoe UI', 11, 'bold'),
                 padx=30, pady=8, borderwidth=0, cursor='hand2').pack(side='left', padx=5)
    
    def delete_product(self):
        """Удаление товара"""
        selected = self.products_tree.selection()
        if not selected:
            messagebox.showwarning("⚠️ Внимание", "Выберите товар для удаления")
            return
        
        if messagebox.askyesno("⚠️ Подтверждение", "Вы уверены, что хотите удалить товар?"):
            product_id = self.products_tree.item(selected[0])['values'][0]
            self.cursor.execute("DELETE FROM products WHERE id=?", (product_id,))
            self.conn.commit()
            self.load_products()
            messagebox.showinfo("✅ Успех", "Товар удален")
    
    # ========== МЕТОДЫ УПРАВЛЕНИЯ КЛИЕНТАМИ ==========
    
    def add_customer(self):
        """Диалог добавления клиента"""
        dialog = tk.Toplevel(self.root)
        dialog.title("➕ Добавление клиента")
        dialog.geometry("450x350")
        dialog.configure(bg=self.colors['white'])
        dialog.grab_set()
        
        tk.Label(dialog, text="Добавление нового клиента", 
                font=('Segoe UI', 14, 'bold'),
                bg=self.colors['white'],
                fg=self.colors['primary']).pack(pady=15)
        
        fields_frame = tk.Frame(dialog, bg=self.colors['white'])
        fields_frame.pack(padx=30, pady=10)
        
        fields = ['Имя:', 'Фамилия:', 'Телефон:', 'Email:']
        entries = {}
        
        for i, field in enumerate(fields):
            tk.Label(fields_frame, text=field, 
                    bg=self.colors['white'],
                    font=('Segoe UI', 10)).grid(row=i, column=0, sticky='w', pady=8)
            
            entries[field] = tk.Entry(fields_frame, width=35, font=('Segoe UI', 10),
                                     bd=1, relief='solid')
            entries[field].grid(row=i, column=1, padx=10, pady=5)
        
        def save():
            try:
                self.cursor.execute('''
                    INSERT INTO customers (first_name, last_name, phone, email)
                    VALUES (?, ?, ?, ?)
                ''', (
                    entries['Имя:'].get(),
                    entries['Фамилия:'].get(),
                    entries['Телефон:'].get(),
                    entries['Email:'].get()
                ))
                self.conn.commit()
                self.load_customers()
                dialog.destroy()
                messagebox.showinfo("✅ Успех", "Клиент добавлен!")
            except Exception as e:
                messagebox.showerror("❌ Ошибка", f"Не удалось добавить клиента:\n{str(e)}")
        
        btn_frame = tk.Frame(dialog, bg=self.colors['white'])
        btn_frame.pack(pady=20)
        
        tk.Button(btn_frame, text="💾 Сохранить", command=save,
                 bg=self.colors['success'], fg='white', font=('Segoe UI', 11, 'bold'),
                 padx=30, pady=8, borderwidth=0, cursor='hand2').pack(side='left', padx=5)
        tk.Button(btn_frame, text="✖️ Отмена", command=dialog.destroy,
                 bg=self.colors['warning'], fg='white', font=('Segoe UI', 11, 'bold'),
                 padx=30, pady=8, borderwidth=0, cursor='hand2').pack(side='left', padx=5)
    
    def edit_customer(self):
        """Редактирование клиента"""
        selected = self.customers_tree.selection()
        if not selected:
            messagebox.showwarning("⚠️ Внимание", "Выберите клиента для редактирования")
            return
        
        customer = self.customers_tree.item(selected[0])['values']
        
        dialog = tk.Toplevel(self.root)
        dialog.title("✏️ Редактирование клиента")
        dialog.geometry("450x350")
        dialog.configure(bg=self.colors['white'])
        dialog.grab_set()
        
        tk.Label(dialog, text="Редактирование данных клиента", 
                font=('Segoe UI', 14, 'bold'),
                bg=self.colors['white'],
                fg=self.colors['primary']).pack(pady=15)
        
        fields_frame = tk.Frame(dialog, bg=self.colors['white'])
        fields_frame.pack(padx=30, pady=10)
        
        fields = ['Имя:', 'Фамилия:', 'Телефон:', 'Email:']
        entries = {}
        
        for i, field in enumerate(fields):
            tk.Label(fields_frame, text=field, 
                    bg=self.colors['white'],
                    font=('Segoe UI', 10)).grid(row=i, column=0, sticky='w', pady=8)
            
            entries[field] = tk.Entry(fields_frame, width=35, font=('Segoe UI', 10),
                                     bd=1, relief='solid')
            entries[field].insert(0, customer[i+1])
            entries[field].grid(row=i, column=1, padx=10, pady=5)
        
        def save():
            try:
                self.cursor.execute('''
                    UPDATE customers 
                    SET first_name=?, last_name=?, phone=?, email=?
                    WHERE id=?
                ''', (
                    entries['Имя:'].get(),
                    entries['Фамилия:'].get(),
                    entries['Телефон:'].get(),
                    entries['Email:'].get(),
                    customer[0]
                ))
                self.conn.commit()
                self.load_customers()
                dialog.destroy()
                messagebox.showinfo("✅ Успех", "Данные обновлены!")
            except Exception as e:
                messagebox.showerror("❌ Ошибка", f"Не удалось обновить данные:\n{str(e)}")
        
        btn_frame = tk.Frame(dialog, bg=self.colors['white'])
        btn_frame.pack(pady=20)
        
        tk.Button(btn_frame, text="💾 Сохранить", command=save,
                 bg=self.colors['success'], fg='white', font=('Segoe UI', 11, 'bold'),
                 padx=30, pady=8, borderwidth=0, cursor='hand2').pack(side='left', padx=5)
        tk.Button(btn_frame, text="✖️ Отмена", command=dialog.destroy,
                 bg=self.colors['warning'], fg='white', font=('Segoe UI', 11, 'bold'),
                 padx=30, pady=8, borderwidth=0, cursor='hand2').pack(side='left', padx=5)
    
    def delete_customer(self):
        """Удаление клиента"""
        selected = self.customers_tree.selection()
        if not selected:
            messagebox.showwarning("⚠️ Внимание", "Выберите клиента для удаления")
            return
        
        if messagebox.askyesno("⚠️ Подтверждение", "Вы уверены, что хотите удалить клиента?"):
            customer_id = self.customers_tree.item(selected[0])['values'][0]
            
            # Проверяем, есть ли заказы у клиента
            self.cursor.execute("SELECT COUNT(*) FROM orders WHERE customer_id=?", (customer_id,))
            if self.cursor.fetchone()[0] > 0:
                messagebox.showerror("❌ Ошибка", "Нельзя удалить клиента с заказами")
                return
            
            self.cursor.execute("DELETE FROM customers WHERE id=?", (customer_id,))
            self.conn.commit()
            self.load_customers()
            messagebox.showinfo("✅ Успех", "Клиент удален")
    
    # ========== МЕТОДЫ УПРАВЛЕНИЯ КАТЕГОРИЯМИ ==========
    
    def add_category(self):
        """Добавление категории"""
        dialog = tk.Toplevel(self.root)
        dialog.title("➕ Добавление категории")
        dialog.geometry("400x200")
        dialog.configure(bg=self.colors['white'])
        dialog.grab_set()
        
        tk.Label(dialog, text="Новая категория", 
                font=('Segoe UI', 14, 'bold'),
                bg=self.colors['white'],
                fg=self.colors['primary']).pack(pady=20)
        
        tk.Label(dialog, text="Название категории:", 
                bg=self.colors['white'],
                font=('Segoe UI', 10)).pack()
        
        name_entry = tk.Entry(dialog, width=30, font=('Segoe UI', 10),
                             bd=1, relief='solid')
        name_entry.pack(pady=10)
        
        def save():
            name = name_entry.get()
            if name:
                try:
                    self.cursor.execute("INSERT INTO categories (name) VALUES (?)", (name,))
                    self.conn.commit()
                    self.load_categories()
                    self.load_categories_filter()
                    dialog.destroy()
                    messagebox.showinfo("✅ Успех", "Категория добавлена!")
                except:
                    messagebox.showerror("❌ Ошибка", "Такая категория уже существует")
        
        btn_frame = tk.Frame(dialog, bg=self.colors['white'])
        btn_frame.pack(pady=20)
        
        tk.Button(btn_frame, text="💾 Сохранить", command=save,
                 bg=self.colors['success'], fg='white', font=('Segoe UI', 11, 'bold'),
                 padx=30, pady=8, borderwidth=0, cursor='hand2').pack(side='left', padx=5)
        tk.Button(btn_frame, text="✖️ Отмена", command=dialog.destroy,
                 bg=self.colors['warning'], fg='white', font=('Segoe UI', 11, 'bold'),
                 padx=30, pady=8, borderwidth=0, cursor='hand2').pack(side='left', padx=5)
    
    def delete_category(self):
        """Удаление категории"""
        selected = self.categories_tree.selection()
        if not selected:
            messagebox.showwarning("⚠️ Внимание", "Выберите категорию для удаления")
            return
        
        category_id = self.categories_tree.item(selected[0])['values'][0]
        
        # Проверяем, есть ли товары в категории
        self.cursor.execute("SELECT COUNT(*) FROM products WHERE category_id=?", (category_id,))
        if self.cursor.fetchone()[0] > 0:
            messagebox.showerror("❌ Ошибка", "Нельзя удалить категорию с товарами")
            return
        
        if messagebox.askyesno("⚠️ Подтверждение", "Удалить категорию?"):
            self.cursor.execute("DELETE FROM categories WHERE id=?", (category_id,))
            self.conn.commit()
            self.load_categories()
            self.load_categories_filter()
            messagebox.showinfo("✅ Успех", "Категория удалена")
    
    # ========== ИСПРАВЛЕННЫЕ МЕТОДЫ РАБОТЫ С ЗАКАЗАМИ ==========
    
    def add_to_order_from_products(self):
        """Добавить товар в заказ из каталога (ИСПРАВЛЕНО)"""
        # Проверяем, выбран ли клиент
        if not self.current_order['customer_id']:
            result = messagebox.askyesno("👤 Клиент не выбран", 
                                        "Сначала нужно выбрать клиента. Перейти к выбору клиента?")
            if result:
                self.notebook.select(1)  # Переключаемся на вкладку клиентов
            return
        
        # Получаем выбранный товар
        selected = self.products_tree.selection()
        if not selected:
            messagebox.showwarning("⚠️ Внимание", "Выберите товар из списка")
            return
        
        # Получаем данные товара
        product = self.products_tree.item(selected[0])['values']
        
        product_id = product[0]
        product_name = product[1]
        
        # ИСПРАВЛЕНО: правильное извлечение цены
        price_str = str(product[2])
        # Убираем все символы кроме цифр и точки
        price_str = ''.join(c for c in price_str if c.isdigit() or c == '.')
        try:
            product_price = float(price_str)
        except:
            product_price = 0
        
        # ИСПРАВЛЕНО: правильное извлечение количества
        stock_str = str(product[3])
        # Убираем все символы кроме цифр
        stock_str = ''.join(c for c in stock_str if c.isdigit())
        try:
            available = int(stock_str)
        except:
            available = 0
        
        # Проверяем, есть ли товар в наличии
        if available <= 0:
            messagebox.showerror("❌ Ошибка", f"Товар '{product_name}' отсутствует на складе")
            return
        
        # Проверяем, сколько уже добавлено
        current_qty = 0
        for item in self.current_order['items']:
            if item['id'] == product_id:
                current_qty = item['quantity']
                break
        
        if current_qty >= available:
            messagebox.showerror("❌ Ошибка", f"Товар '{product_name}' закончился на складе\n(все {available} шт. уже в заказе)")
            return
        
        # Диалог выбора количества
        dialog = tk.Toplevel(self.root)
        dialog.title("Количество товара")
        dialog.geometry("350x250")
        dialog.configure(bg=self.colors['white'])
        dialog.grab_set()
        
        tk.Label(dialog, text=f"Товар: {product_name}", 
                font=('Segoe UI', 11, 'bold'),
                bg=self.colors['white']).pack(pady=10)
        
        tk.Label(dialog, text=f"Цена: {product_price:,.0f} ₽", 
                bg=self.colors['white']).pack()
        
        tk.Label(dialog, text=f"Доступно: {available} шт.", 
                bg=self.colors['white']).pack()
        
        if current_qty > 0:
            tk.Label(dialog, text=f"Уже в заказе: {current_qty} шт.", 
                    fg=self.colors['secondary'],
                    bg=self.colors['white']).pack()
        
        frame = tk.Frame(dialog, bg=self.colors['white'])
        frame.pack(pady=10)
        
        tk.Label(frame, text="Количество:", bg=self.colors['white']).pack(side='left')
        
        max_qty = available - current_qty
        qty_var = tk.IntVar(value=1)
        spinbox = tk.Spinbox(frame, from_=1, to=max_qty, textvariable=qty_var,
                            width=10, font=('Segoe UI', 10))
        spinbox.pack(side='left', padx=5)
        
        def add_to_cart():
            qty = qty_var.get()
            
            # Добавляем или обновляем товар в заказе
            found = False
            for item in self.current_order['items']:
                if item['id'] == product_id:
                    item['quantity'] += qty
                    item['subtotal'] = item['price'] * item['quantity']
                    found = True
                    break
            
            if not found:
                self.current_order['items'].append({
                    'id': product_id,
                    'name': product_name,
                    'price': product_price,
                    'quantity': qty,
                    'subtotal': product_price * qty
                })
            
            # Пересчитываем итого
            self.current_order['total'] = sum(item['subtotal'] for item in self.current_order['items'])
            
            # Обновляем отображение
            self.update_order_display()
            
            dialog.destroy()
            
            # Показываем сообщение
            new_total = self.current_order['total']
            messagebox.showinfo("✅ Успех", 
                              f"Товар '{product_name}' добавлен в заказ!\n"
                              f"Количество: {qty} шт.\n"
                              f"Текущая сумма: {new_total:,.0f} ₽")
            
            # Переключаемся на вкладку заказа
            self.notebook.select(4)  # Вкладка "Новый заказ"
        
        # Кнопки
        btn_frame = tk.Frame(dialog, bg=self.colors['white'])
        btn_frame.pack(pady=10)
        
        tk.Button(btn_frame, text="✅ Добавить", command=add_to_cart,
                 bg=self.colors['success'], fg='white',
                 font=('Segoe UI', 10), padx=20, pady=5,
                 borderwidth=0, cursor='hand2').pack(side='left', padx=5)
        
        tk.Button(btn_frame, text="✖️ Отмена", command=dialog.destroy,
                 bg=self.colors['warning'], fg='white',
                 font=('Segoe UI', 10), padx=20, pady=5,
                 borderwidth=0, cursor='hand2').pack(side='left', padx=5)
    
    def add_product_from_catalog(self):
        """Перейти к каталогу для добавления товара"""
        self.notebook.select(0)  # Переключаемся на вкладку товаров
        messagebox.showinfo("📦 Выбор товара", "Выберите товар и нажмите '🛒 В заказ' или дважды кликните по товару")
    
    def remove_from_order(self):
        """Удалить товар из заказа"""
        selected = self.order_items_tree.selection()
        if not selected:
            messagebox.showwarning("⚠️ Внимание", "Выберите товар для удаления")
            return
        
        item_id = self.order_items_tree.item(selected[0])['values'][0]
        self.current_order['items'] = [item for item in self.current_order['items'] if item['id'] != item_id]
        self.current_order['total'] = sum(item['subtotal'] for item in self.current_order['items'])
        self.update_order_display()
    
    def clear_order(self):
        """Очистить корзину"""
        if self.current_order['items']:
            if messagebox.askyesno("🔄 Очистка", "Очистить корзину?"):
                self.current_order['items'] = []
                self.current_order['total'] = 0
                self.update_order_display()
    
    def choose_customer(self):
        """Выбрать клиента для заказа"""
        selected = self.customers_tree.selection()
        if not selected:
            messagebox.showwarning("⚠️ Внимание", "Сначала выберите клиента в списке")
            self.notebook.select(1)  # Переключаемся на вкладку клиентов
            return
        
        customer = self.customers_tree.item(selected[0])['values']
        self.current_order['customer_id'] = customer[0]
        self.current_order['customer_name'] = f"{customer[1]} {customer[2]}"
        self.customer_label.config(text=f"Клиент: {self.current_order['customer_name']}",
                                   fg=self.colors['success'])
        self.notebook.select(4)  # Переключаемся на вкладку нового заказа
        messagebox.showinfo("✅ Клиент выбран", f"Клиент: {self.current_order['customer_name']}\nТеперь добавьте товары в заказ")
    
    def create_order_for_customer(self):
        """Создать заказ для выбранного клиента"""
        selected = self.customers_tree.selection()
        if not selected:
            messagebox.showwarning("⚠️ Внимание", "Выберите клиента из списка")
            return
        
        customer = self.customers_tree.item(selected[0])['values']
        self.current_order['customer_id'] = customer[0]
        self.current_order['customer_name'] = f"{customer[1]} {customer[2]}"
        self.customer_label.config(text=f"Клиент: {self.current_order['customer_name']}",
                                   fg=self.colors['success'])
        self.notebook.select(4)  # Переключаемся на вкладку нового заказа
        messagebox.showinfo("✅ Клиент выбран", f"Клиент: {self.current_order['customer_name']}\nТеперь добавьте товары в заказ")
    
    def add_customer_and_order(self):
        """Добавить нового клиента и создать заказ"""
        dialog = tk.Toplevel(self.root)
        dialog.title("➕ Новый клиент")
        dialog.geometry("450x350")
        dialog.configure(bg=self.colors['white'])
        dialog.grab_set()
        
        tk.Label(dialog, text="Добавление нового клиента", 
                font=('Segoe UI', 14, 'bold'),
                bg=self.colors['white'],
                fg=self.colors['primary']).pack(pady=15)
        
        fields_frame = tk.Frame(dialog, bg=self.colors['white'])
        fields_frame.pack(padx=30, pady=10)
        
        fields = ['Имя:', 'Фамилия:', 'Телефон:', 'Email:']
        entries = {}
        
        for i, field in enumerate(fields):
            tk.Label(fields_frame, text=field, 
                    bg=self.colors['white'],
                    font=('Segoe UI', 10)).grid(row=i, column=0, sticky='w', pady=8)
            
            entries[field] = tk.Entry(fields_frame, width=35, font=('Segoe UI', 10),
                                     bd=1, relief='solid')
            entries[field].grid(row=i, column=1, padx=10, pady=5)
        
        def save_and_order():
            try:
                # Добавляем клиента
                self.cursor.execute('''
                    INSERT INTO customers (first_name, last_name, phone, email)
                    VALUES (?, ?, ?, ?)
                ''', (
                    entries['Имя:'].get(),
                    entries['Фамилия:'].get(),
                    entries['Телефон:'].get(),
                    entries['Email:'].get()
                ))
                
                self.conn.commit()
                customer_id = self.cursor.lastrowid
                customer_name = f"{entries['Имя:'].get()} {entries['Фамилия:'].get()}"
                
                # Устанавливаем клиента для заказа
                self.current_order['customer_id'] = customer_id
                self.current_order['customer_name'] = customer_name
                self.customer_label.config(text=f"Клиент: {customer_name}",
                                         fg=self.colors['success'])
                
                self.load_customers()
                dialog.destroy()
                self.notebook.select(4)  # Переключаемся на вкладку нового заказа
                messagebox.showinfo("✅ Успех", f"Клиент {customer_name} добавлен!\nТеперь добавьте товары в заказ")
                
            except Exception as e:
                messagebox.showerror("❌ Ошибка", f"Не удалось добавить клиента:\n{str(e)}")
        
        btn_frame = tk.Frame(dialog, bg=self.colors['white'])
        btn_frame.pack(pady=20)
        
        tk.Button(btn_frame, text="✅ Добавить и создать заказ", command=save_and_order,
                 bg=self.colors['success'], fg='white', font=('Segoe UI', 10, 'bold'),
                 padx=20, pady=8, borderwidth=0, cursor='hand2').pack(side='left', padx=5)
        tk.Button(btn_frame, text="✖️ Отмена", command=dialog.destroy,
                 bg=self.colors['warning'], fg='white', font=('Segoe UI', 10),
                 padx=20, pady=8, borderwidth=0, cursor='hand2').pack(side='left', padx=5)
    
    def update_order_display(self):
        """Обновить отображение заказа (ИСПРАВЛЕНО)"""
        # Очищаем таблицу
        for row in self.order_items_tree.get_children():
            self.order_items_tree.delete(row)
        
        # Добавляем товары
        for item in self.current_order['items']:
            values = (
                item['id'],
                item['name'],
                f"{item['price']:,.0f} ₽",
                item['quantity'],
                f"{item['subtotal']:,.0f} ₽"
            )
            self.order_items_tree.insert('', 'end', values=values)
        
        # Обновляем итого
        self.total_label.config(text=f"ИТОГО: {self.current_order['total']:,.0f} ₽")
        
        # Принудительно обновляем интерфейс
        self.order_items_tree.update_idletasks()
        self.root.update_idletasks()
    
    def complete_order(self):
        """Оформить заказ"""
        if not self.current_order['customer_id']:
            messagebox.showwarning("⚠️ Внимание", "Выберите клиента для заказа")
            self.notebook.select(1)  # Переключаемся на вкладку клиентов
            return
        
        if not self.current_order['items']:
            messagebox.showwarning("⚠️ Внимание", "Добавьте товары в заказ")
            self.notebook.select(0)  # Переключаемся на вкладку товаров
            return
        
        # Диалог выбора способа оплаты
        dialog = tk.Toplevel(self.root)
        dialog.title("💳 Способ оплаты")
        dialog.geometry("350x250")
        dialog.configure(bg=self.colors['white'])
        dialog.grab_set()
        
        tk.Label(dialog, text="Оформление заказа", 
                font=('Segoe UI', 14, 'bold'),
                bg=self.colors['white'],
                fg=self.colors['primary']).pack(pady=15)
        
        tk.Label(dialog, text=f"Сумма заказа: {self.current_order['total']:,.0f} ₽", 
                font=('Segoe UI', 12),
                bg=self.colors['white'],
                fg=self.colors['success']).pack(pady=5)
        
        tk.Label(dialog, text="Способ оплаты:", 
                bg=self.colors['white'],
                font=('Segoe UI', 10)).pack(pady=5)
        
        payment_var = tk.StringVar(value="Наличные")
        
        frame = tk.Frame(dialog, bg=self.colors['white'])
        frame.pack(pady=5)
        
        tk.Radiobutton(frame, text="💵 Наличные", variable=payment_var, value="Наличные",
                      bg=self.colors['white']).pack(anchor='w')
        tk.Radiobutton(frame, text="💳 Карта", variable=payment_var, value="Карта",
                      bg=self.colors['white']).pack(anchor='w')
        
        def save_order():
            payment = payment_var.get()
            
            try:
                # Создаем заказ
                self.cursor.execute('''
                    INSERT INTO orders (customer_id, order_date, total_amount, status, payment_method)
                    VALUES (?, ?, ?, ?, ?)
                ''', (
                    self.current_order['customer_id'],
                    datetime.now().strftime("%Y-%m-%d %H:%M"),
                    self.current_order['total'],
                    'Новый',
                    payment
                ))
                
                order_id = self.cursor.lastrowid
                
                # Добавляем товары в заказ и обновляем склад
                for item in self.current_order['items']:
                    self.cursor.execute('''
                        INSERT INTO order_items (order_id, product_id, quantity, price_per_unit, subtotal)
                        VALUES (?, ?, ?, ?, ?)
                    ''', (order_id, item['id'], item['quantity'], item['price'], item['subtotal']))
                    
                    # Уменьшаем количество на складе
                    self.cursor.execute('''
                        UPDATE products SET stock = stock - ? WHERE id = ?
                    ''', (item['quantity'], item['id']))
                
                self.conn.commit()
                
                # Очищаем текущий заказ
                self.current_order = {
                    'customer_id': None,
                    'customer_name': None,
                    'items': [],
                    'total': 0
                }
                self.update_order_display()
                self.customer_label.config(text="Клиент не выбран", fg=self.colors['warning'])
                
                # Обновляем данные
                self.load_products()
                self.load_orders()
                
                dialog.destroy()
                self.notebook.select(3)  # Переключаемся на вкладку заказов
                messagebox.showinfo("✅ Успех", f"Заказ №{order_id} успешно оформлен!")
                
            except Exception as e:
                messagebox.showerror("❌ Ошибка", f"Не удалось оформить заказ:\n{str(e)}")
        
        btn_frame = tk.Frame(dialog, bg=self.colors['white'])
        btn_frame.pack(pady=20)
        
        tk.Button(btn_frame, text="✅ Оформить", command=save_order,
                 bg=self.colors['success'], fg='white', font=('Segoe UI', 11, 'bold'),
                 padx=30, pady=8, borderwidth=0, cursor='hand2').pack(side='left', padx=5)
        tk.Button(btn_frame, text="✖️ Отмена", command=dialog.destroy,
                 bg=self.colors['warning'], fg='white', font=('Segoe UI', 11),
                 padx=30, pady=8, borderwidth=0, cursor='hand2').pack(side='left', padx=5)
    
    def change_order_status(self):
        """Изменить статус заказа"""
        selected = self.orders_tree.selection()
        if not selected:
            messagebox.showwarning("⚠️ Внимание", "Выберите заказ")
            return
        
        order = self.orders_tree.item(selected[0])['values']
        
        dialog = tk.Toplevel(self.root)
        dialog.title("📊 Изменение статуса")
        dialog.geometry("350x300")
        dialog.configure(bg=self.colors['white'])
        dialog.grab_set()
        
        tk.Label(dialog, text=f"Заказ №{order[0]}", 
                font=('Segoe UI', 14, 'bold'),
                bg=self.colors['white'],
                fg=self.colors['primary']).pack(pady=15)
        
        tk.Label(dialog, text=f"Текущий статус: {order[4]}", 
                bg=self.colors['white'],
                font=('Segoe UI', 10)).pack(pady=5)
        
        tk.Label(dialog, text="Новый статус:", 
                bg=self.colors['white'],
                font=('Segoe UI', 10)).pack(pady=5)
        
        status_var = tk.StringVar(value=order[4])
        
        statuses = ['Новый', 'В обработке', 'Доставлен', 'Отменен']
        
        frame = tk.Frame(dialog, bg=self.colors['white'])
        frame.pack(pady=5)
        
        for status in statuses:
            tk.Radiobutton(frame, text=status, variable=status_var, value=status,
                          bg=self.colors['white']).pack(anchor='w', pady=2)
        
        def update_status():
            new_status = status_var.get()
            
            self.cursor.execute('''
                UPDATE orders SET status = ? WHERE id = ?
            ''', (new_status, order[0]))
            self.conn.commit()
            
            self.load_orders()
            dialog.destroy()
            messagebox.showinfo("✅ Успех", f"Статус заказа №{order[0]} изменен на '{new_status}'")
        
        btn_frame = tk.Frame(dialog, bg=self.colors['white'])
        btn_frame.pack(pady=20)
        
        tk.Button(btn_frame, text="✅ Обновить", command=update_status,
                 bg=self.colors['success'], fg='white', font=('Segoe UI', 11),
                 padx=30, pady=8, borderwidth=0, cursor='hand2').pack(side='left', padx=5)
        tk.Button(btn_frame, text="✖️ Отмена", command=dialog.destroy,
                 bg=self.colors['warning'], fg='white', font=('Segoe UI', 11),
                 padx=30, pady=8, borderwidth=0, cursor='hand2').pack(side='left', padx=5)
    
    def view_order_details(self):
        """Просмотр деталей заказа"""
        selected = self.orders_tree.selection()
        if not selected:
            messagebox.showwarning("⚠️ Внимание", "Выберите заказ")
            return
        
        order = self.orders_tree.item(selected[0])['values']
        order_id = order[0]
        
        # Получаем детали заказа
        self.cursor.execute('''
            SELECT p.name, oi.quantity, oi.price_per_unit, oi.subtotal
            FROM order_items oi
            JOIN products p ON oi.product_id = p.id
            WHERE oi.order_id = ?
        ''', (order_id,))
        
        items = self.cursor.fetchall()
        
        # Создаем окно с деталями
        dialog = tk.Toplevel(self.root)
        dialog.title(f"📋 Детали заказа №{order_id}")
        dialog.geometry("600x400")
        dialog.configure(bg=self.colors['white'])
        dialog.grab_set()
        
        # Информация о заказе
        info_frame = tk.Frame(dialog, bg=self.colors['white'], bd=1, relief='solid')
        info_frame.pack(fill='x', padx=10, pady=10)
        
        tk.Label(info_frame, text=f"Заказ №{order_id}", 
                font=('Segoe UI', 14, 'bold'),
                bg=self.colors['white'],
                fg=self.colors['primary']).pack(anchor='w', padx=10, pady=5)
        
        tk.Label(info_frame, text=f"Клиент: {order[2]}", 
                bg=self.colors['white']).pack(anchor='w', padx=10, pady=2)
        tk.Label(info_frame, text=f"Дата: {order[1]}", 
                bg=self.colors['white']).pack(anchor='w', padx=10, pady=2)
        tk.Label(info_frame, text=f"Статус: {order[4]}", 
                bg=self.colors['white']).pack(anchor='w', padx=10, pady=2)
        tk.Label(info_frame, text=f"Сумма: {order[3]}", 
                font=('Segoe UI', 11, 'bold'),
                fg=self.colors['success'],
                bg=self.colors['white']).pack(anchor='w', padx=10, pady=5)
        
        # Таблица товаров
        table_frame = tk.Frame(dialog, bg=self.colors['white'], bd=1, relief='solid')
        table_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        columns = ('📦 Товар', '🔢 Количество', '💰 Цена', '💵 Сумма')
        tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=8)
        
        tree.heading('📦 Товар', text='Товар')
        tree.heading('🔢 Количество', text='Количество')
        tree.heading('💰 Цена', text='Цена')
        tree.heading('💵 Сумма', text='Сумма')
        
        tree.column('📦 Товар', width=250)
        tree.column('🔢 Количество', width=100, anchor='center')
        tree.column('💰 Цена', width=120, anchor='e')
        tree.column('💵 Сумма', width=120, anchor='e')
        
        for item in items:
            tree.insert('', 'end', values=(
                item[0],
                item[1],
                f"{item[2]:,.0f} ₽",
                f"{item[3]:,.0f} ₽"
            ))
        
        tree.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Кнопка закрытия
        tk.Button(dialog, text="✖️ Закрыть", command=dialog.destroy,
                 bg=self.colors['primary'], fg='white',
                 font=('Segoe UI', 10), padx=30, pady=5,
                 borderwidth=0, cursor='hand2').pack(pady=10)

# Запуск
if __name__ == "__main__":
    root = tk.Tk()
    app = FurnitureShop(root)
    root.mainloop()