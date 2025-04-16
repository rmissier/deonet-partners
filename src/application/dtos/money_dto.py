"""Data Transfer Object for Money value object using Pydantic for validation."""

from pydantic import BaseModel, Field, field_validator

from src.domain.models.money import Money


class MoneyDTO(BaseModel):
    """DTO representation of the Money value object with validation."""

    amount: float = Field(..., ge=0.0)
    currency: str = Field(default="EUR", min_length=3, max_length=3)

    @field_validator("currency")
    @classmethod
    def validate_currency(cls, value: str) -> str:
        """Validate that currency is uppercase."""
        return value.upper()

    @classmethod
    def from_domain(cls, money: Money) -> "MoneyDTO":
        """Convert domain Money object to MoneyDTO.

        Args:
            money: Domain Money value object

        Returns:
            Equivalent MoneyDTO instance

        """
        return cls(amount=money.amount, currency=money.currency)

    def to_domain(self) -> Money:
        """Convert this MoneyDTO to a domain Money value object.

        Returns:
            Domain Money value object

        """
        return Money(amount=self.amount, currency=self.currency)

    class Config:
        """Pydantic configuration."""

        str_strip_whitespace = True
        frozen = True
