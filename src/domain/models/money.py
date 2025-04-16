"""Represents a monetary value."""

from dataclasses import dataclass
from typing import Self


@dataclass(frozen=True, kw_only=True)
class Money:
    """Represents a monetary value (simplified)."""

    amount: float = 0.0
    currency: str = "EUR"

    def __post_init__(self) -> None:
        """Validate monetary amount."""
        if self.amount < 0:
            msg = "Money amount cannot be negative"
            raise ValueError(msg)
        if not self.currency or len(self.currency) != 3:  # noqa: PLR2004
            msg = "Currency must be a 3-character string"
            raise ValueError(msg)

    def __add__(self, other: Self) -> Self:
        """Add two Money instances."""
        if self.currency != other.currency:
            msg = (
                f"Cannot add different currencies: {self.currency} and {other.currency}"
            )
            raise ValueError(msg)
        amount = self.amount + other.amount
        return Money(amount=amount, currency=self.currency)

    def __mul__(self, factor: float) -> Self:
        """Multiply Money by a scalar."""
        if not isinstance(factor, (int, float)):
            return NotImplemented
        amount = self.amount * factor
        return Money(amount=amount, currency=self.currency)

    def __rmul__(self, factor: float) -> Self:
        """Right-multiply Money by a scalar."""
        return self.__mul__(factor)
