from dataclasses import dataclass, field
from datetime import date
from enum import Enum
from typing import Optional


class TransactionType(str, Enum):
    INCOME = "income"
    EXPENSE = "expense"


@dataclass
class Transaction:
    id: Optional[int]
    type: TransactionType
    category: str
    description: str
    amount_net: float          # pre-VAT amount
    vat_rate: float            # e.g. 0.24 for 24%
    vat_deductible: bool       # only meaningful for expenses
    date: date
    notes: str = ""

    @property
    def vat_amount(self) -> float:
        return round(self.amount_net * self.vat_rate, 2)

    @property
    def amount_gross(self) -> float:
        return round(self.amount_net + self.vat_amount, 2)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "type": self.type.value,
            "category": self.category,
            "description": self.description,
            "amount_net": self.amount_net,
            "vat_rate": self.vat_rate,
            "vat_amount": self.vat_amount,
            "amount_gross": self.amount_gross,
            "vat_deductible": self.vat_deductible,
            "date": self.date.isoformat(),
            "notes": self.notes,
        }