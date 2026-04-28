
import tkinter as tk
from tkinter import messagebox, ttk
import requests
import json
import os

class GitHubUserFinder:
    def __init__(self, root):
        self.root = root
        self.root.title("GitHub User Finder")
        self.root.geometry("600x500")

        # Загрузка избранных пользователей
        self.favorites = self.load_favorites()

        self.setup_ui()

    def setup_ui(self):
        # Основной фрейм для поиска
        search_frame = tk.Frame(self.root)
        search_frame.pack(pady=10, padx=20, fill="x")

        tk.Label(search_frame, text="Введите имя пользователя GitHub:").pack(anchor="w")

        # Поле ввода с подсказкой
        self.search_entry = tk.Entry(search_frame, width=50, font=("Arial", 10))
        self.search_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.search_entry.bind("<Return>", lambda event: self.search_user())  # Поиск по Enter

        # Кнопка поиска
        search_btn = tk.Button(search_frame, text="Найти", command=self.search_user,
                               bg="#4CAF50", fg="white", font=("Arial", 10, "bold"))
        search_btn.pack(side="left")

        # Фрейм для результатов поиска
        results_frame = tk.LabelFrame(self.root, text="Результаты поиска", padx=10, pady=10)
        results_frame.pack(pady=10, padx=20, fill="both", expand=True)

        # Список результатов с прокруткой
        results_scrollbar = tk.Scrollbar(results_frame)
        results_scrollbar.pack(side="right", fill="y")

        self.results_listbox = tk.Listbox(results_frame, height=8, width=70,
                                       yscrollcommand=results_scrollbar.set, font=("Arial", 9))
        self.results_listbox.pack(fill="both", expand=True)
        results_scrollbar.config(command=self.results_listbox.yview)

        # Кнопка добавления в избранное
        add_fav_btn = tk.Button(self.root, text="Добавить в избранное",
                               command=self.add_to_favorites, bg="#2196F3", fg="white")
        add_fav_btn.pack(pady=5)

        # Фрейм для избранных пользователей
        favorites_frame = tk.LabelFrame(self.root, text="Избранные пользователи", padx=10, pady=10)
        favorites_frame.pack(pady=10, padx=20, fill="both", expand=True)

        # Список избранных с прокруткой
        favorites_scrollbar = tk.Scrollbar(favorites_frame)
        favorites_scrollbar.pack(side="right", fill="y")

        self.favorites_listbox = tk.Listbox(favorites_frame, height=8, width=70,
                                   yscrollcommand=favorites_scrollbar.set, font=("Arial", 9))
        self.favorites_listbox.pack(fill="both", expand=True)
        favorites_scrollbar.config(command=self.favorites_listbox.yview)

        self.update_favorites_list()

    def search_user(self):
        username = self.search_entry.get().strip()

        # Валидация ввода
        if not username:
            messagebox.showerror("Ошибка", "Поле поиска не должно быть пустым!")
            self.search_entry.focus()
            return

        if len(username) < 1:
            messagebox.showerror("Ошибка", "Имя пользователя должно содержать хотя бы 1 символ!")
            return

        # Очистка предыдущего результата
        self.results_listbox.delete(0, tk.END)

        try:
            # Исправленный URL — https://
            response = requests.get(f"https://api.github.com/users/{username}")

            if response.status_code == 200:
                user_data = response.json()
                self.display_user(user_data)
            elif response.status_code == 404:
                messagebox.showwarning("Не найдено", f"Пользователь '{username}' не найден на GitHub")
            else:
                messagebox.showerror("Ошибка API",
                                 f"Ошибка сервера: код {response.status_code}")
        except requests.exceptions.ConnectionError:
            messagebox.showerror("Ошибка сети", "Не удалось подключиться к GitHub API.\nПроверьте интернет‑соединение.")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Произошла непредвиденная ошибка: {e}")

    def display_user(self, user_data):
        # Форматируем информацию о пользователе
        login = user_data.get('login', 'Нет логина')
        name = user_data.get('name', 'Нет имени')
        company = user_data.get('company', 'Не указана')
        location = user_data.get('location', 'Не указано')
        public_repos = user_data.get('public_repos', 0)

        info = f"{login} | {name} | Компания: {company} | Локация: {location} | Репозиториев: {public_repos}"
        self.results_listbox.insert(tk.END, info)

    def add_to_favorites(self):
        selection = self.results_listbox.curselection()
        if not selection:
            messagebox.showwarning("Предупреждение", "Выберите пользователя из результатов поиска!")
            return

        user_info = self.results_listbox.get(selection[0])
        if user_info not in self.favorites:
            self.favorites.append(user_info)
            self.save_favorites()
            self.update_favorites_list()
            messagebox.showinfo("Успех", "Пользователь добавлен в избранное!")
        else:
            messagebox.showwarning("Уже в избранном", "Этот пользователь уже находится в списке избранных!")

    def load_favorites(self):
        if os.path.exists("users.json"):
            with open("users.json", "r", encoding="utf-8") as f:
                try:
                    return json.load(f)
                except json.JSONDecodeError:
                    messagebox.showwarning("Предупреждение", "Файл users.json повреждён, создаётся новый.")
                    return []
        return []

    def save_favorites(self):
        with open("users.json", "w", encoding="utf-8") as f:
            json.dump(self.favorites, f, ensure_ascii=False, indent=4)

    def update_favorites_list(self):
        self.favorites_listbox.delete(0, tk.END)
        for user in self.favorites:
            self.favorites_listbox.insert(tk.END, user)

# Запуск приложения
if __name__ == "__main__":
    root = tk.Tk()
    app = GitHubUserFinder(root)
    root.mainloop()
