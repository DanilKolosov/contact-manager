import sqlite3
import csv
from models.contact import Contact, Category


class ContactRepository:
    """Репозиторий для работы с базой данных (без email)"""

    def __init__(self, db_name: str = "contacts.db"):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self._create_table()

    def _create_table(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS contacts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                phone TEXT,
                category TEXT NOT NULL,
                notes TEXT
            )
        ''')
        self.conn.commit()

    def add(self, contact: Contact) -> int:
        self.cursor.execute('''
            INSERT INTO contacts (name, phone, category, notes)
            VALUES (?, ?, ?, ?)
        ''', (contact.name, contact.phone, contact.category.value, contact.notes))
        self.conn.commit()
        return self.cursor.lastrowid

    def get_all(self) -> list[Contact]:
        self.cursor.execute("SELECT * FROM contacts")
        return [Contact.from_row(row) for row in self.cursor.fetchall()]

    def get_by_id(self, contact_id: int) -> Contact | None:
        self.cursor.execute("SELECT * FROM contacts WHERE id = ?", (contact_id,))
        row = self.cursor.fetchone()
        return Contact.from_row(row) if row else None

    def update(self, contact: Contact):
        if not contact.id:
            return
        self.cursor.execute('''
            UPDATE contacts 
            SET name=?, phone=?, category=?, notes=?
            WHERE id=?
        ''', (contact.name, contact.phone, contact.category.value, contact.notes, contact.id))
        self.conn.commit()

    def delete(self, contact_id: int):
        self.cursor.execute("DELETE FROM contacts WHERE id = ?", (contact_id,))
        self.conn.commit()

    def search(self, query: str) -> list[Contact]:
        q = f"%{query}%"
        self.cursor.execute('''
            SELECT * FROM contacts 
            WHERE name LIKE ? OR phone LIKE ?
        ''', (q, q))
        return [Contact.from_row(row) for row in self.cursor.fetchall()]

    def get_by_category(self, category: Category) -> list[Contact]:
        self.cursor.execute("SELECT * FROM contacts WHERE category = ?", (category.value,))
        return [Contact.from_row(row) for row in self.cursor.fetchall()]

    def export_to_csv(self, filename: str):
        contacts = self.get_all()
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=["id", "name", "phone", "category", "notes"])
            writer.writeheader()
            for c in contacts:
                writer.writerow(c.to_dict())

    def import_from_csv(self, filename: str):
        with open(filename, 'r', newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    contact = Contact(
                        name=row["name"],
                        phone=row.get("phone", ""),
                        category=Category(row["category"]),
                        notes=row.get("notes", "")
                    )
                    self.add(contact)
                except Exception as e:
                    print(f"Ошибка импорта строки: {e}")
                    
                    