from dataclasses import dataclass
from datetime import date
from decimal import Decimal, ROUND_HALF_UP


@dataclass
class Transaction:
    """
    Represents one financial transaction in FinTrack.

    Monetary amounts are stored as integer cents.
    VAT rate is stored as a decimal fraction.
    Example: 25.5% VAT = Decimal("0.255").
    """

    transaction_date: date
    description: str
    category: str
    transaction_type: str
    gross_cents: int
    vat_rate: Decimal
    vat_deductible: bool = False

    def __post_init__(self):
        """Validate transaction data after creation."""

        if not isinstance(self.transaction_date, date):
            raise ValueError("Invalid transaction date.")

        if not self.description.strip():
            raise ValueError("Description cannot be empty.")

        if not self.category.strip():
            raise ValueError("Category cannot be empty.")

        if self.transaction_type not in ("income", "expense"):
            raise ValueError("Type must be income or expense.")

        if not isinstance(self.gross_cents, int) or isinstance(
            self.gross_cents, bool
        ):
            raise ValueError("Gross amount must be integer cents.")

        if self.gross_cents <= 0:
            raise ValueError("Gross amount must be positive.")

        self.vat_rate = Decimal(str(self.vat_rate))

        if not self.vat_rate.is_finite() or not (
            Decimal("0") <= self.vat_rate <= Decimal("1")
        ):
            raise ValueError("Invalid VAT rate.")

        if not isinstance(self.vat_deductible, bool):
            raise ValueError("VAT deductibility must be True or False.")

        if self.transaction_type == "income":
            self.vat_deductible = False

    @property
    def vat_cents(self) -> int:
        """Calculate the VAT included in the gross amount."""

        gross = Decimal(self.gross_cents)

        net = gross / (Decimal("1") + self.vat_rate)

        return int(
            (gross - net).quantize(
                Decimal("1"),
                rounding=ROUND_HALF_UP,
            )
        )

    @property
    def net_cents(self) -> int:
        """Calculate the amount excluding VAT."""

        return self.gross_cents - self.vat_cents

    @property
    def deductible_vat_cents(self) -> int:
        """Return deductible VAT for eligible expenses."""

        if self.transaction_type == "expense" and self.vat_deductible:
            return self.vat_cents

        return 0

    def to_dict(self) -> dict:
        """Convert transaction into a dictionary."""

        return {
            "transaction_date": self.transaction_date.isoformat(),
            "description": self.description,
            "category": self.category,
            "transaction_type": self.transaction_type,
            "gross_cents": self.gross_cents,
            "net_cents": self.net_cents,
            "vat_cents": self.vat_cents,
            "vat_rate": str(self.vat_rate),
            "vat_deductible": self.vat_deductible,
            "deductible_vat_cents": self.deductible_vat_cents,
        }