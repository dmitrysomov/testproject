import tkinter as tk
from tkinter import ttk, messagebox
import json
from datetime import datetime

class ExpenseTracker:
    def __init__(self, root):
        self.root = root
        self.root.title("Expense Tracker")
        self.root.geometry("800x600")
        
        # Данные расходов
        self.expenses = []
        self.load_data()
        
        self.setup_ui()
    
    def setup_ui(self):
        # Фрейм для ввода данных
        input_frame = ttk.LabelFrame(self.root, text="Добавить расход")
        input_frame.pack(fill="x", padx=10, pady=5)
        
        # Поле суммы
        ttk.Label(input_frame, text="Сумма:").grid(row=0, column=0, padx=5, pady=5)
        self.amount_entry = ttk.Entry(input_frame)
        self.amount_entry.grid(row=0, column=1, padx=5, pady=5)
        
        # Поле категории
        ttk.Label(input_frame, text="Категория:").grid(row=0, column=2, padx=5, pady=5)
        self.category_var = tk.StringVar()
        categories = ["Еда", "Транспорт", "Развлечения", "Жильё", "Прочее"]
        self.category_combo = ttk.Combobox(input_frame, textvariable=self.category_var, values=categories)
        self.category_combo.grid(row=0, column=3, padx=5, pady=5)
        
        # Поле даты
        ttk.Label(input_frame, text="Дата (ГГГГ-ММ-ДД):").grid(row=0, column=4, padx=5, pady=5)
        self.date_entry = ttk.Entry(input_frame)
        self.date_entry.grid(row=0, column=5, padx=5, pady=5)
        # Кнопка добавления
        self.add_button = ttk.Button(input_frame, text="Добавить расход", command=self.add_expense)
        self.add_button.grid(row=0, column=6, padx=5, pady=5)
        
        # Фрейм для фильтрации
        filter_frame = ttk.LabelFrame(self.root, text="Фильтрация")
        filter_frame.pack(fill="x", padx=10, pady=5)
        
        # Фильтр по категории
        ttk.Label(filter_frame, text="Категория:").grid(row=0, column=0, padx=5, pady=5)
        self.filter_category_var = tk.StringVar()
        self.filter_category_combo = ttk.Combobox(filter_frame, textvariable=self.filter_category_var,
                                                   values=["Все"] + categories)
        self.filter_category_combo.set("Все")
        self.filter_category_combo.grid(row=0, column=1, padx=5, pady=5)
        
        # Фильтр по дате
        ttk.Label(filter_frame, text="С:").grid(row=0, column=2, padx=5, pady=5)
        self.start_date_entry = ttk.Entry(filter_frame)
        self.start_date_entry.grid(row=0, column=3, padx=5, pady=5)
        ttk.Label(filter_frame, text="По:").grid(row=0, column=4, padx=5, pady=5)
        self.end_date_entry = ttk.Entry(filter_frame)
        self.end_date_entry.grid(row=0, column=5, padx=5, pady=5)
        # Кнопка фильтрации
        self.filter_button = ttk.Button(filter_frame, text="Применить фильтр", command=self.apply_filter)
        self.filter_button.grid(row=0, column=6, padx=5, pady=5)
        
        # Таблица расходов
        columns = ("ID", "Сумма", "Категория", "Дата")
        self.tree = ttk.Treeview(self.root, columns=columns, show="headings")
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100)
        self.tree.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Фрейм для итогов
        summary_frame = ttk.LabelFrame(self.root, text="Итоги")
        summary_frame.pack(fill="x", padx=10, pady=5)
        self.total_label = ttk.Label(summary_frame, text="Общая сумма: 0 руб.")
        self.total_label.pack(padx=5, pady=5)
        
        self.update_table()
        self.update_total()
    
    def validate_input(self, amount_str, date_str):
        """Проверка корректности ввода"""
        try:
            amount = float(amount_str)
            if amount <= 0:
                raise ValueError("Сумма должна быть положительной")
        except ValueError:
            messagebox.showerror("Ошибка", "Некорректная сумма")
            return False
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Ошибка", "Некорректный формат даты (используйте ГГГГ-ММ-ДД)")
            return False
        return True
    
    def add_expense(self):
        """Добавление нового расхода"""
        amount_str = self.amount_entry.get()
        category = self.category_var.get()
        date_str = self.date_entry.get()
        if not self.validate_input(amount_str, date_str):
            return
        expense = {
            "id": len(self.expenses) + 1,
            "amount": float(amount_str),
            "category": category,
            "date": date_str
        }
        self.expenses.append(expense)
        self.save_data()
        self.update_table()
        self.update_total()
        # Очистка полей ввода
        self.amount_entry.delete(0, tk.END)
        self.date_entry.delete(0, tk.END)
    
    def update_table(self, filtered_expenses=None):
        """Обновление таблицы расходов"""
        # Очистка таблицы
        for item in self.tree.get_children():
            self.tree.delete(item)
        # Заполнение таблицы
        expenses_to_show = filtered_expenses if filtered_expenses is not None else self.expenses
        for expense in expenses_to_show:
            self.tree.insert("", "end", values=(
                expense["id"],
                f"{expense['amount']:.2f}",
                expense["category"],
                expense["date"]
            ))
    
    def apply_filter(self):
        """Применение фильтров"""
        filtered = []
        selected_category = self.filter_category_var.get()
        start_date_str = self.start_date_entry.get()
        end_date_str = self.end_date_entry.get()
        for expense in self.expenses:
            # Фильтр по категории
            if selected_category != "Все" and expense["category"] != selected_category:
                continue
            # Фильтр по дате
            try:
                expense_date = datetime.strptime(expense["date"], "%Y-%m-%d")
                if start_date_str:
                    start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
                    if expense_date < start_date:
                        continue
                if end_date_str:
                    end_date = datetime.strptime(end_date_str, "%Y-%m-%d")
                    if expense_date > end_date:
                        continue
            except ValueError:
                continue  # Пропускаем записи с некорректной датой
            filtered.append(expense)
        self.update_table(filtered)
