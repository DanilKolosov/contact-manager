from dataclasses import dataclass
from enum import Enum


class Category(Enum):
    FRIENDS = "Друзья"
    FAMILY = "Семья"
    WORK = "Работа"


@dataclass
class Contact:
    id: int | None = None
    name: str = ""
    phone: str = ""
    # email убран полностью
    category: Category = Category.FRIENDS
    notes: str = ""

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "phone": self.phone,
            # "email" удалён
            "category": self.category.value,
            "notes": self.notes
        }

    @classmethod
    def from_row(cls, row):
        return cls(
            id=row[0],
            name=row[1],
            phone=row[2] or "",
            # email был на позиции 3, теперь сдвигаем индексы
            category=Category(row[3]),
            notes=row[4] or ""
        )