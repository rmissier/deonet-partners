"""Unit tests for the ShippingInfo domain model."""

from datetime import date, datetime, timedelta, timezone

import pytest
from pytest_mock import MockerFixture

from src.domain.models.address import Address
from src.domain.models.money import Money
from src.domain.models.shipping_info import ShippingInfo


@pytest.fixture
def address() -> Address:
    """Create a mock Address instance."""
    return Address(
        recipient_name="John Doe",
        street1="123 Main St",
        city="Amsterdam",
        postal_code="1011AB",
        country="NL",
    )


@pytest.fixture
def shipping_info(address: Address) -> ShippingInfo:
    """Create a sample shipping info instance for testing."""
    return ShippingInfo(
        address=address,
        carrier="DHL",
        shipping_method="Express",
        shipping_cost=Money(amount=15.99),
        email_address="john.doe@example.com",
    )


class TestShippingInfo:
    """Test cases for ShippingInfo domain model."""

    def test_initialization(self, address: Address) -> None:
        """Test that ShippingInfo can be properly initialized."""
        shipping_info = ShippingInfo(
            address=address,
            carrier="DHL",
            shipping_method="Express",
            shipping_cost=Money(amount=15.99),
            estimated_shipping_date=date(2023, 12, 25),
            email_address="john.doe@example.com",
            phone_number="+31612345678",
        )

        assert shipping_info.address == address
        assert shipping_info.carrier == "DHL"
        assert shipping_info.shipping_method == "Express"
        assert shipping_info.shipping_cost.amount == 15.99  # noqa: PLR2004
        assert shipping_info.estimated_shipping_date == date(2023, 12, 25)
        assert shipping_info.email_address == "john.doe@example.com"
        assert shipping_info.phone_number == "+31612345678"

    def test_default_values(self, address: Address) -> None:
        """Test that default values are properly set."""
        shipping_info = ShippingInfo(
            address=address,
            carrier="DHL",
        )

        assert shipping_info.shipping_method == "Standard"
        assert shipping_info.shipping_cost.amount == 0.0
        assert shipping_info.estimated_shipping_date is None
        assert shipping_info.email_address is None
        assert shipping_info.phone_number is None

    def test_update_estimated_shipping_date(
        self,
        mocker: MockerFixture,
        shipping_info: ShippingInfo,
    ) -> None:
        """Test updating estimated shipping date."""
        # Freeze time for consistent testing
        fixed_date = datetime(2023, 11, 20, tzinfo=timezone.utc).date()  # A Monday

        mock_datetime = mocker.patch("src.domain.models.shipping_info.datetime")
        mock_datetime.now.return_value = datetime(2023, 11, 20, tzinfo=timezone.utc)

        # Update to 3 working days
        shipping_info.update_estimated_shipping_date(3)

        # Should be Thursday (Monday + 3 working days)
        expected_date = fixed_date + timedelta(days=3)
        assert shipping_info.estimated_shipping_date == expected_date

    def test_update_estimated_shipping_date_with_weekend(
        self,
        mocker: MockerFixture,
        shipping_info: ShippingInfo,
    ) -> None:
        """Test updating estimated shipping date across a weekend."""
        # Freeze time for consistent testing - Friday
        fixed_date = datetime(2023, 11, 24, tzinfo=timezone.utc).date()  # A Friday

        mock_datetime = mocker.patch("src.domain.models.shipping_info.datetime")
        mock_datetime.now.return_value = datetime(2023, 11, 24, tzinfo=timezone.utc)

        # Update to 3 working days
        shipping_info.update_estimated_shipping_date(3)

        # Should be Wednesday (Friday + weekend + 3 working days)
        expected_date = fixed_date + timedelta(days=5)  # Skip Sat and Sun
        assert shipping_info.estimated_shipping_date == expected_date

    def test_update_estimated_shipping_date_negative_days(
        self,
        shipping_info: ShippingInfo,
    ) -> None:
        """Test that negative days value raises ValueError."""
        with pytest.raises(ValueError, match="Days must be a positive integer"):
            shipping_info.update_estimated_shipping_date(-1)

    def test_update_address(self, shipping_info: ShippingInfo) -> None:
        """Test updating the shipping address."""
        new_address = Address(
            recipient_name="Jane Smith",
            street1="456 Oak St",
            city="Rotterdam",
            postal_code="3011AB",
            country="NL",
        )

        shipping_info.update_address(new_address)
        assert shipping_info.address == new_address
        assert shipping_info.address.recipient_name == "Jane Smith"

    def test_update_address_with_invalid_type(self, shipping_info: ShippingInfo) -> None:
        """Test that updating with non-Address type raises TypeError."""
        with pytest.raises(
            TypeError,
            match="New address must be an instance of Address",
        ):
            shipping_info.update_address("Invalid address")

    def test_immutability(self, shipping_info: ShippingInfo) -> None:
        """Test that ShippingInfo instances are immutable."""
        with pytest.raises(AttributeError):
            shipping_info.carrier = "UPS"

        with pytest.raises(AttributeError):
            shipping_info.shipping_method = "Standard"

        # Methods should use object.__setattr__ to bypass frozen=True
        # which we test in other test methods
