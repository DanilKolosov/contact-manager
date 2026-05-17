import pytest
from models.contact import Contact, Category
from repositories.contact_repository import ContactRepository
from services.contact_service import ContactService


def test_add_contact_empty_name_raises_error():
    repo = ContactRepository(":memory:")
    service = ContactService(repo)
    
    with pytest.raises(ValueError):
        service.add_contact(name="", phone="123", category=Category.FRIENDS)


def test_add_and_get_contact():
    repo = ContactRepository(":memory:")
    service = ContactService(repo)
    
    service.add_contact("Тестовый Друг", "+79991234567", Category.FRIENDS, "Это тест")
    
    all_contacts = service.get_all_contacts()
    assert len(all_contacts) == 1
    assert all_contacts[0].name == "Тестовый Друг"