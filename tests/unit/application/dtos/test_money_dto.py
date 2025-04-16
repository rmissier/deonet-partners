"""Unit tests for the MoneyDTO application DTO."""

import pytest
from pydantic import ValidationError

from src.application.dtos.money_dto import MoneyDTO
from src.domain.models.money import Money


@pytest.fixture
def valid_money_data() -> dict:
    """Fixture providing valid data for creating a MoneyDTO."""
    return {
        "amount": 19.99,
        "currency": "eur",  # Lowercase to test normalization
    }


@pytest.fixture
def domain_money() -> Money:
    """Fixture providing a valid Money domain object."""
    return Money(amount=19.99, currency="EUR")


class TestMoneyDTO:
    """Test cases for MoneyDTO."""

    def test_initialization(self, valid_money_data: dict) -> None:
        """Test that MoneyDTO can be initialized with valid data."""
        dto = MoneyDTO(**valid_money_data)

        assert dto.amount == 19.99  # noqa: PLR2004
        assert dto.currency == "EUR"  # Should be uppercase

    def test_default_currency(self) -> None:
        """Test default currency is EUR."""
        dto = MoneyDTO(amount=10.0)

        assert dto.currency == "EUR"

    def test_amount_validation(self) -> None:
        """Test validation of amount field."""
        # Negative amount should fail
        with pytest.raises(ValidationError):
            MoneyDTO(amount=-10.0)

        # Zero amount should be valid
        dto = MoneyDTO(amount=0.0)
        assert dto.amount == 0.0

    def test_currency_validation(self) -> None:
        """Test validation of currency field."""
        # Currency too short
        with pytest.raises(ValidationError):
            MoneyDTO(amount=10.0, currency="EU")

        # Currency too long
        with pytest.raises(ValidationError):
            MoneyDTO(amount=10.0, currency="EURO")

    def test_currency_normalization(self) -> None:
        """Test that currency code is normalized to uppercase."""
        dto = MoneyDTO(amount=10.0, currency="usd")
        assert dto.currency == "USD"

    def test_from_domain(self, domain_money: Money) -> None:
        """Test conversion from domain model to DTO."""
        dto = MoneyDTO.from_domain(domain_money)

        assert dto.amount == domain_money.amount
        assert dto.currency == domain_money.currency

    def test_to_domain(self, valid_money_data: dict) -> None:
        """Test conversion from DTO to domain model."""
        dto = MoneyDTO(**valid_money_data)
        money = dto.to_domain()

        assert isinstance(money, Money)
        assert money.amount == dto.amount
        assert money.currency == dto.currency

    def test_immutability(self, valid_money_data: dict) -> None:
        """Test that MoneyDTO instances are immutable."""
        dto = MoneyDTO(**valid_money_data)

        with pytest.raises(ValueError, match="amount"):
            dto.amount = 30.0

        with pytest.raises(ValueError, match="currency"):
            dto.currency = "USD"
