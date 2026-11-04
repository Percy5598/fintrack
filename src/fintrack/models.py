from dataclasses import dataclass
from datetime import date
from decimal import Decimal, ROUND_HALF_UP


def to_cents(amount: Decimal | str | float) -> int:
    """Convert a monetary amount to integer cents."""
    value = Decimal(str(amount))
    return int(
        (value * 100).quantize(
            Decimal("1"),
            rounding=ROUND_HALF_UP,
        )
    )


def from_cents(amount: int) -> Decimal:
    """Convert integer cents to a Decimal euro amount."""
    return Decimal(amount) / 100


@dataclass(frozen=True)
class Transaction:
    transaction_date: date
    description: str
    category: str
    transaction_type: str
    gross_cents: int
    vat_rate: Decimal
    vat_deductible: bool = True

    def __post_init__(self) -> None:
        if self.transaction_type not in {"income", "expense"}:
            raise ValueError("Transaction type must be income or expense.")

        if self.gross_cents < 0:
            raise ValueError("Transaction amount cannot be negative.")

        if not self.description.strip():
            raise ValueError("Description cannot be empty.")

        if not Decimal("0") <= self.vat_rate <= Decimal("100"):
            raise ValueError("VAT rate must be between 0 and 100.")

    @property
    def net_cents(self) -> int:
        """Calculate the amount excluding VAT."""
        divisor = Decimal("1") + self.vat_rate / Decimal("100")

        return int(
            (Decimal(self.gross_cents) / divisor).quantize(
                Decimal("1"),
                rounding=ROUND_HALF_UP,
            )
        )

    @property
    def vat_cents(self) -> int:
        """Calculate the VAT portion of the gross amount."""
        return self.gross_cents - self.net_cents

    @property
    def deductible_vat_cents(self) -> int:
        """Return deductible VAT for eligible expense transactions."""
        if self.transaction_type == "expense" and self.vat_deductible:
            return self.vat_cents

        return 0