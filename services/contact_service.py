from repositories.contact_repository import ContactRepository
from models.contact import Contact, Category


class ContactService:
    """Сервисный слой — бизнес-логика и валидация (Dependency Injection)"""

    def __init__(self, repository: ContactRepository):
        self.repository = repository

    def add_contact(self, name: str, phone: str, category: Category, notes: str = "") -> Contact:
        if not name.strip():
            raise ValueError("Имя контакта обязательно!")
        contact = Contact(
            name=name.strip(), 
            phone=phone.strip(), 
            category=category, 
            notes=notes.strip()
        )
        contact.id = self.repository.add(contact)
        return contact

    def get_all_contacts(self) -> list[Contact]:
        return self.repository.get_all()

    def update_contact(self, contact: Contact):
        self.repository.update(contact)

    def delete_contact(self, contact_id: int):
        self.repository.delete(contact_id)

    def search_contacts(self, query: str) -> list[Contact]:
        return self.repository.search(query.strip())

    def get_contacts_by_category(self, category: Category) -> list[Contact]:
        return self.repository.get_by_category(category)

    def export_contacts(self, filename: str):
        self.repository.export_to_csv(filename)

    def import_contacts(self, filename: str):
        self.repository.import_from_csv(filename)