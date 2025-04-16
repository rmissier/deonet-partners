"""Unit tests for the Money value object."""

import pytest

from src.domain.models.money import Money


class TestMoney:
    """Test cases for Money value object."""

    def test_initialization(self) -> None:
        """Test that Money can be initialized with valid values."""
        money = Money(amount=100.0, currency="EUR")
        assert money.amount == 100.0  # noqa: PLR2004
        assert money.currency == "EUR"

    def test_default_currency(self) -> None:
        """Test that default currency is EUR."""
        money = Money(amount=100.0)
        assert money.currency == "EUR"

    def test_negative_amount(self) -> None:
        """Test that negative amounts are not allowed."""
        with pytest.raises(ValueError, match="Money amount cannot be negative"):
            Money(amount=-10.0)

    def test_addition(self) -> None:
        """Test adding two Money instances with the same currency."""
        m1 = Money(amount=10.0)
        m2 = Money(amount=20.0)
        result = m1 + m2

        assert isinstance(result, Money)
        assert result.amount == 30.0  # noqa: PLR2004
        assert result.currency == "EUR"

    def test_addition_different_currencies(self) -> None:
        """Test that adding different currencies raises an error."""
        m1 = Money(amount=10.0, currency="EUR")
        m2 = Money(amount=20.0, currency="USD")

        with pytest.raises(ValueError, match="Cannot add different currencies"):
            m1 + m2

    def test_multiplication(self) -> None:
        """Test multiplying Money by a scalar."""
        money = Money(amount=10.0)
        result = money * 3

        assert isinstance(result, Money)
        assert result.amount == 30.0  # noqa: PLR2004
        assert result.currency == "EUR"

    def test_right_multiplication(self) -> None:
        """Test right-multiplying Money by a scalar."""
        money = Money(amount=10.0)
        result = 3 * money

        assert isinstance(result, Money)
        assert result.amount == 30.0  # noqa: PLR2004
        assert result.currency == "EUR"

    def test_immutability(self) -> None:
        """Test that Money instances are immutable."""
        money = Money(amount=10.0)

        with pytest.raises(AttributeError):
            money.amount = 20.0

        with pytest.raises(AttributeError):
            money.currency = "USD"
