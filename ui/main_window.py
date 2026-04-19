import tkinter as tk
from tkinter import messagebox, filedialog
from models.contact import Contact, Category
from services.contact_service import ContactService
from repositories.contact_repository import ContactRepository


class ContactManagerApp:
    def __init__(self):
        self.repo = ContactRepository()
        self.service = ContactService(self.repo)

        self.root = tk.Tk()
        self.root.title("Менеджер контактов")
        self.root.geometry("900x600")

        self.current_contact: Contact | None = None
        self.contacts_cache: list[Contact] = []

        self._create_widgets()
        self.load_contacts()

    def _create_widgets(self):
        # Список контактов
        list_frame = tk.Frame(self.root)
        list_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        tk.Label(list_frame, text="Контакты", font=("Arial", 14, "bold")).pack(anchor="w")
        self.contact_list = tk.Listbox(list_frame, width=60, height=25, font=("Arial", 11))
        self.contact_list.pack(fill=tk.BOTH, expand=True)
        self.contact_list.bind('<<ListboxSelect>>', self.on_select)

        # Панель деталей
        detail_frame = tk.Frame(self.root, padx=10, pady=10)
        detail_frame.pack(side=tk.RIGHT, fill=tk.Y)

        fields = [
            ("Имя:", "name_entry"),
            ("Телефон:", "phone_entry"),
            ("Email:", "email_entry")
        ]
        for i, (label, attr) in enumerate(fields):
            tk.Label(detail_frame, text=label).grid(row=i, column=0, sticky="w", pady=5)
            setattr(self, attr, tk.Entry(detail_frame, width=40))
            getattr(self, attr).grid(row=i, column=1, pady=5)

        tk.Label(detail_frame, text="Категория:").grid(row=3, column=0, sticky="w", pady=5)
        self.category_var = tk.StringVar(value=Category.FRIENDS.value)
        self.category_combo = tk.OptionMenu(detail_frame, self.category_var,
                                            *[c.value for c in Category])
        self.category_combo.grid(row=3, column=1, sticky="ew", pady=5)

        tk.Label(detail_frame, text="Заметки:").grid(row=4, column=0, sticky="nw", pady=5)
        self.notes_text = tk.Text(detail_frame, width=40, height=6)
        self.notes_text.grid(row=4, column=1, pady=5)

        # Кнопки
        btn_frame = tk.Frame(detail_frame)
        btn_frame.grid(row=5, column=0, columnspan=2, pady=15)

        tk.Button(btn_frame, text="Добавить", width=12, command=self.add_contact).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Обновить", width=12, command=self.update_contact).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Удалить", width=12, command=self.delete_contact).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Очистить", width=12, command=self.clear_form).pack(side=tk.LEFT, padx=5)

        # Поиск и фильтр
        search_frame = tk.Frame(self.root)
        search_frame.pack(fill=tk.X, padx=10, pady=5)

        tk.Label(search_frame, text="Поиск:").pack(side=tk.LEFT)
        self.search_entry = tk.Entry(search_frame, width=30)
        self.search_entry.pack(side=tk.LEFT, padx=5)
        tk.Button(search_frame, text="Найти", command=self.search).pack(side=tk.LEFT, padx=5)
        tk.Button(search_frame, text="Все", command=self.load_contacts).pack(side=tk.LEFT, padx=5)

        self.filter_var = tk.StringVar(value="Все")
        tk.Label(search_frame, text="Фильтр:").pack(side=tk.LEFT, padx=(20, 5))
        filter_menu = tk.OptionMenu(search_frame, self.filter_var, "Все",
                                    *[c.value for c in Category],
                                    command=lambda _: self.filter_by_category())
        filter_menu.pack(side=tk.LEFT)

        # Импорт/Экспорт
        io_frame = tk.Frame(self.root)
        io_frame.pack(fill=tk.X, padx=10, pady=10)
        tk.Button(io_frame, text="Экспорт в CSV", command=self.export).pack(side=tk.LEFT, padx=5)
        tk.Button(io_frame, text="Импорт из CSV", command=self.import_data).pack(side=tk.LEFT, padx=5)

    def load_contacts(self, contacts: list[Contact] | None = None):
        self.contact_list.delete(0, tk.END)
        if contacts is None:
            contacts = self.service.get_all_contacts()
        self.contacts_cache = contacts

        for contact in contacts:
            text = f"{contact.name}  •  {contact.category.value}  •  {contact.phone}"
            self.contact_list.insert(tk.END, text)

    def on_select(self, event):
        selection = self.contact_list.curselection()
        if not selection:
            return
        idx = selection[0]
        contact = self.contacts_cache[idx]
        self.current_contact = contact

        # заполняем форму
        self.name_entry.delete(0, tk.END)
        self.name_entry.insert(0, contact.name)
        self.phone_entry.delete(0, tk.END)
        self.phone_entry.insert(0, contact.phone)
        self.email_entry.delete(0, tk.END)
        self.email_entry.insert(0, contact.email)
        self.category_var.set(contact.category.value)
        self.notes_text.delete(1.0, tk.END)
        self.notes_text.insert(tk.END, contact.notes)

    def add_contact(self):
        try:
            cat = next(c for c in Category if c.value == self.category_var.get())
            contact = self.service.add_contact(
                name=self.name_entry.get(),
                phone=self.phone_entry.get(),
                email=self.email_entry.get(),
                category=cat,
                notes=self.notes_text.get(1.0, tk.END).strip()
            )
            messagebox.showinfo("Готово", f"Контакт «{contact.name}» добавлен!")
            self.load_contacts()
            self.clear_form()
        except ValueError as e:
            messagebox.showerror("Ошибка", str(e))

    def update_contact(self):
        if not self.current_contact or not self.current_contact.id:
            messagebox.showerror("Ошибка", "Выберите контакт для редактирования")
            return
        try:
            cat = next(c for c in Category if c.value == self.category_var.get())
            self.current_contact.name = self.name_entry.get().strip()
            self.current_contact.phone = self.phone_entry.get().strip()
            self.current_contact.email = self.email_entry.get().strip()
            self.current_contact.category = cat
            self.current_contact.notes = self.notes_text.get(1.0, tk.END).strip()

            self.service.update_contact(self.current_contact)
            messagebox.showinfo("Готово", "Контакт обновлён!")
            self.load_contacts()
            self.clear_form()
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    def delete_contact(self):
        if not self.current_contact or not self.current_contact.id:
            messagebox.showerror("Ошибка", "Выберите контакт для удаления")
            return
        if messagebox.askyesno("Подтверждение", f"Удалить контакт «{self.current_contact.name}»?"):
            self.service.delete_contact(self.current_contact.id)
            messagebox.showinfo("Готово", "Контакт удалён")
            self.load_contacts()
            self.clear_form()

    def clear_form(self):
        self.name_entry.delete(0, tk.END)
        self.phone_entry.delete(0, tk.END)
        self.email_entry.delete(0, tk.END)
        self.notes_text.delete(1.0, tk.END)
        self.category_var.set(Category.FRIENDS.value)
        self.current_contact = None

    def search(self):
        query = self.search_entry.get().strip()
        contacts = self.service.search_contacts(query) if query else None
        self.load_contacts(contacts)

    def filter_by_category(self):
        value = self.filter_var.get()
        if value == "Все":
            self.load_contacts()
        else:
            cat = next(c for c in Category if c.value == value)
            contacts = self.service.get_contacts_by_category(cat)
            self.load_contacts(contacts)

    def export(self):
        filename = filedialog.asksaveasfilename(defaultextension=".csv",
                                                filetypes=[("CSV files", "*.csv")])
        if filename:
            self.service.export_contacts(filename)
            messagebox.showinfo("Готово", "Контакты экспортированы!")

    def import_data(self):
        filename = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if filename:
            self.service.import_contacts(filename)
            messagebox.showinfo("Готово", "Контакты импортированы!")
            self.load_contacts()

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    app = ContactManagerApp()
    app.run()