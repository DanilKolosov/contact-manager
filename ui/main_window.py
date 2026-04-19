from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTableWidget, QTableWidgetItem, QLabel, QLineEdit, QPushButton,
    QComboBox, QTextEdit, QMessageBox, QFileDialog, QHeaderView
)
from PyQt6.QtCore import Qt
from models.contact import Contact, Category
from services.contact_service import ContactService
from repositories.contact_repository import ContactRepository
import sys


class ContactManagerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Менеджер контактов — PyQt6")
        self.resize(950, 620)

        self.repo = ContactRepository()
        self.service = ContactService(self.repo)

        self.current_contact: Contact | None = None

        self._create_ui()
        self.load_contacts()

    def _create_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)

        # Левая часть — таблица
        left_layout = QVBoxLayout()

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Поиск по имени или телефону...")
        self.search_input.textChanged.connect(self.search_contacts)

        self.category_filter = QComboBox()
        self.category_filter.addItem("Все категории")
        for cat in Category:
            self.category_filter.addItem(cat.value)
        self.category_filter.currentTextChanged.connect(self.filter_by_category)

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Имя", "Телефон", "Категория", "Заметки"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.itemSelectionChanged.connect(self.on_table_select)

        left_layout.addWidget(QLabel("Поиск:"))
        left_layout.addWidget(self.search_input)
        left_layout.addWidget(QLabel("Фильтр по категории:"))
        left_layout.addWidget(self.category_filter)
        left_layout.addWidget(self.table)

        # Правая часть — форма
        right_layout = QVBoxLayout()

        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Имя контакта")

        self.phone_edit = QLineEdit()
        self.phone_edit.setPlaceholderText("Телефон")

        self.category_combo = QComboBox()
        for cat in Category:
            self.category_combo.addItem(cat.value)

        self.notes_edit = QTextEdit()
        self.notes_edit.setPlaceholderText("Заметки...")

        btn_layout = QHBoxLayout()
        self.add_btn = QPushButton("Добавить")
        self.update_btn = QPushButton("Обновить")
        self.delete_btn = QPushButton("Удалить")
        self.clear_btn = QPushButton("Очистить")

        self.add_btn.clicked.connect(self.add_contact)
        self.update_btn.clicked.connect(self.update_contact)
        self.delete_btn.clicked.connect(self.delete_contact)
        self.clear_btn.clicked.connect(self.clear_form)

        btn_layout.addWidget(self.add_btn)
        btn_layout.addWidget(self.update_btn)
        btn_layout.addWidget(self.delete_btn)
        btn_layout.addWidget(self.clear_btn)

        io_layout = QHBoxLayout()
        export_btn = QPushButton("Экспорт в CSV")
        import_btn = QPushButton("Импорт из CSV")
        export_btn.clicked.connect(self.export_contacts)
        import_btn.clicked.connect(self.import_contacts)
        io_layout.addWidget(export_btn)
        io_layout.addWidget(import_btn)

        right_layout.addWidget(QLabel("Имя:"))
        right_layout.addWidget(self.name_edit)
        right_layout.addWidget(QLabel("Телефон:"))
        right_layout.addWidget(self.phone_edit)
        right_layout.addWidget(QLabel("Категория:"))
        right_layout.addWidget(self.category_combo)
        right_layout.addWidget(QLabel("Заметки:"))
        right_layout.addWidget(self.notes_edit)
        right_layout.addLayout(btn_layout)
        right_layout.addLayout(io_layout)
        right_layout.addStretch()

        main_layout.addLayout(left_layout, 2)
        main_layout.addLayout(right_layout, 1)

    def load_contacts(self, contacts: list[Contact] | None = None):
        if contacts is None:
            contacts = self.service.get_all_contacts()

        self.table.setRowCount(0)
        self.table.setRowCount(len(contacts))

        for row, contact in enumerate(contacts):
            self.table.setItem(row, 0, QTableWidgetItem(contact.name))
            self.table.setItem(row, 1, QTableWidgetItem(contact.phone))
            self.table.setItem(row, 2, QTableWidgetItem(contact.category.value))
            self.table.setItem(row, 3, QTableWidgetItem(contact.notes[:60] + "..." if len(contact.notes) > 60 else contact.notes))

        self.contacts_cache = contacts

    def on_table_select(self):
        selected = self.table.selectedItems()
        if not selected:
            return
        row = selected[0].row()
        contact = self.contacts_cache[row]
        self.current_contact = contact

        self.name_edit.setText(contact.name)
        self.phone_edit.setText(contact.phone)
        self.category_combo.setCurrentText(contact.category.value)
        self.notes_edit.setText(contact.notes)

    def add_contact(self):
        try:
            cat = next(c for c in Category if c.value == self.category_combo.currentText())
            contact = self.service.add_contact(
                name=self.name_edit.text(),
                phone=self.phone_edit.text(),
                category=cat,
                notes=self.notes_edit.toPlainText()
            )
            QMessageBox.information(self, "Успех", f"Контакт «{contact.name}» добавлен!")
            self.load_contacts()
            self.clear_form()
        except ValueError as e:
            QMessageBox.warning(self, "Ошибка", str(e))

    def update_contact(self):
        if not self.current_contact or not self.current_contact.id:
            QMessageBox.warning(self, "Ошибка", "Выберите контакт для редактирования")
            return
        try:
            cat = next(c for c in Category if c.value == self.category_combo.currentText())
            self.current_contact.name = self.name_edit.text().strip()
            self.current_contact.phone = self.phone_edit.text().strip()
            self.current_contact.category = cat
            self.current_contact.notes = self.notes_edit.toPlainText().strip()

            self.service.update_contact(self.current_contact)
            QMessageBox.information(self, "Успех", "Контакт обновлён!")
            self.load_contacts()
            self.clear_form()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", str(e))

    def delete_contact(self):
        if not self.current_contact:
            QMessageBox.warning(self, "Ошибка", "Выберите контакт")
            return
        reply = QMessageBox.question(self, "Подтверждение", f"Удалить «{self.current_contact.name}»?")
        if reply == QMessageBox.StandardButton.Yes:
            self.service.delete_contact(self.current_contact.id)
            QMessageBox.information(self, "Успех", "Контакт удалён")
            self.load_contacts()
            self.clear_form()

    def clear_form(self):
        self.name_edit.clear()
        self.phone_edit.clear()
        self.notes_edit.clear()
        self.category_combo.setCurrentIndex(0)
        self.current_contact = None
        self.table.clearSelection()

    def search_contacts(self):
        query = self.search_input.text().strip()
        contacts = self.service.search_contacts(query) if query else self.service.get_all_contacts()
        self.load_contacts(contacts)

    def filter_by_category(self):
        value = self.category_filter.currentText()
        if value == "Все категории":
            self.load_contacts()
        else:
            cat = next(c for c in Category if c.value == value)
            contacts = self.service.get_contacts_by_category(cat)
            self.load_contacts(contacts)

    def export_contacts(self):
        filename, _ = QFileDialog.getSaveFileName(self, "Экспорт в CSV", "", "CSV Files (*.csv)")
        if filename:
            self.service.export_contacts(filename)
            QMessageBox.information(self, "Успех", "Экспорт завершён!")

    def import_contacts(self):
        filename, _ = QFileDialog.getOpenFileName(self, "Импорт из CSV", "", "CSV Files (*.csv)")
        if filename:
            self.service.import_contacts(filename)
            QMessageBox.information(self, "Успех", "Импорт завершён!")
            self.load_contacts()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ContactManagerApp()
    window.show()
    sys.exit(app.exec())