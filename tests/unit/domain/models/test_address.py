"""Unit tests for the Address domain model."""

import pytest

from src.domain.models.address import Address


class TestAddress:
    """Test cases for Address value object."""

    def test_initialization(self) -> None:
        """Test that Address can be initialized with valid values."""
        address = Address(
            recipient_name="John Doe",
            street1="123 Main St",
            city="Amsterdam",
            postal_code="1011AB",
            country="NL",
        )

        assert address.recipient_name == "John Doe"
        assert address.street1 == "123 Main St"
        assert address.city == "Amsterdam"
        assert address.postal_code == "1011AB"
        assert address.country == "NL"
        assert address.street2 == ""
        assert address.state_province == ""

    def test_initialization_with_optional_fields(self) -> None:
        """Test that Address can be initialized with all fields."""
        address = Address(
            recipient_name="John Doe",
            street1="123 Main St",
            city="New York",
            postal_code="10001",
            country="US",
            street2="Apt 4B",
            state_province="NY",
        )

        assert address.street2 == "Apt 4B"
        assert address.state_province == "NY"

    def test_immutability(self) -> None:
        """Test that Address instances are immutable."""
        address = Address(
            recipient_name="John Doe",
            street1="123 Main St",
            city="Amsterdam",
            postal_code="1011AB",
            country="NL",
        )

        with pytest.raises(AttributeError):
            address.recipient_name = "Jane Doe"

        with pytest.raises(AttributeError):
            address.country = "BE"

    def test_equality(self) -> None:
        """Test that identical Address instances are equal."""
        address1 = Address(
            recipient_name="John Doe",
            street1="123 Main St",
            city="Amsterdam",
            postal_code="1011AB",
            country="NL",
        )

        address2 = Address(
            recipient_name="John Doe",
            street1="123 Main St",
            city="Amsterdam",
            postal_code="1011AB",
            country="NL",
        )

        assert address1 == address2

    def test_inequality(self) -> None:
        """Test that different Address instances are not equal."""
        address1 = Address(
            recipient_name="John Doe",
            street1="123 Main St",
            city="Amsterdam",
            postal_code="1011AB",
            country="NL",
        )

        address2 = Address(
            recipient_name="Jane Doe",  # Different name
            street1="123 Main St",
            city="Amsterdam",
            postal_code="1011AB",
            country="NL",
        )

        assert address1 != address2
