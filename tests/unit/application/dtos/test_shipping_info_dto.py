"""Unit tests for the ShippingInfoDTO application DTO."""

from datetime import date, datetime, timedelta, timezone
from unittest.mock import Mock

import phonenumbers
import pytest
from pydantic import ValidationError
from pytest_mock import MockerFixture

from src.application.dtos.address_dto import AddressDTO
from src.application.dtos.money_dto import MoneyDTO
from src.application.dtos.shipping_info_dto import ShippingInfoDTO
from src.domain.models.address import Address
from src.domain.models.money import Money
from src.domain.models.shipping_info import ShippingInfo


@pytest.fixture
def address_dto() -> AddressDTO:
    """Fixture providing a valid AddressDTO instance."""
    return AddressDTO(
        recipient_name="John Doe",
        street1="123 Main St",
        city="Amsterdam",
        postal_code="1011AB",
        country="NL",
    )


@pytest.fixture
def money_dto() -> MoneyDTO:
    """Fixture providing a valid MoneyDTO instance."""
    return MoneyDTO(amount=15.99)


@pytest.fixture
def shipping_info_dto_data(
    address_dto: AddressDTO,
    money_dto: MoneyDTO,
) -> dict:
    """Fixture providing valid data for creating a ShippingInfoDTO."""
    return {
        "address": address_dto,
        "carrier": "DHL",
        "shipping_method": "Express",
        "shipping_cost": money_dto,
        "estimated_shipping_date": (
            datetime.now(tz=timezone.utc) + timedelta(days=10)
        ).date(),
        "email_address": "john.doe@example.com",
        "phone_number": "+31612345678",
    }


@pytest.fixture
def mocked_shipping_info(mocker: MockerFixture) -> Mock:
    """Fixture providing a mock ShippingInfo domain object."""
    mocked_address = mocker.Mock(spec=Address)
    mocked_money = mocker.Mock(amount=15.99, currency="EUR")
    return mocker.Mock(
        spec=ShippingInfo,
        address=mocked_address,
        carrier="DHL",
        shipping_method="Express",
        shipping_cost=mocked_money,
        estimated_shipping_date=(
            datetime.now(tz=timezone.utc) + timedelta(days=10)
        ).date(),
        email_address="john.doe@example.com",
        phone_number="+31612345678",
    )


class TestShippingInfoDTO:
    """Test cases for ShippingInfoDTO."""

    def test_initialization(self, shipping_info_dto_data: dict) -> None:
        """Test that ShippingInfoDTO can be initialized with valid data."""
        dto = ShippingInfoDTO(**shipping_info_dto_data)

        assert dto.address == shipping_info_dto_data["address"]
        assert dto.carrier == "DHL"
        assert dto.shipping_method == "Express"
        assert dto.shipping_cost == shipping_info_dto_data["shipping_cost"]
        assert (
            dto.estimated_shipping_date
            == shipping_info_dto_data["estimated_shipping_date"]
        )
        assert dto.email_address == "john.doe@example.com"
        assert dto.phone_number == "+31612345678"

    def test_carrier_validation(self, shipping_info_dto_data: dict) -> None:
        """Test validation of carrier field."""
        # Empty carrier should fail
        invalid_data = dict(shipping_info_dto_data)
        invalid_data["carrier"] = ""

        with pytest.raises(ValidationError):
            ShippingInfoDTO(**invalid_data)

        # Whitespace-only carrier should fail after stripping
        invalid_data["carrier"] = "   "
        with pytest.raises(ValidationError):
            ShippingInfoDTO(**invalid_data)

    def test_shipping_method_validation(
        self,
        shipping_info_dto_data: dict,
    ) -> None:
        """Test validation of shipping_method field."""
        # Empty shipping_method should fail
        invalid_data = dict(shipping_info_dto_data)
        invalid_data["shipping_method"] = ""

        with pytest.raises(ValidationError):
            ShippingInfoDTO(**invalid_data)

        # Default shipping_method
        data = dict(shipping_info_dto_data)
        data.pop("shipping_method")
        dto = ShippingInfoDTO(**data)
        assert dto.shipping_method == "Standard"

    def test_email_validation(self, shipping_info_dto_data: dict) -> None:
        """Test validation of email_address field."""
        # Invalid email should fail
        invalid_data = dict(shipping_info_dto_data)
        invalid_data["email_address"] = "not-an-email"

        with pytest.raises(ValidationError):
            ShippingInfoDTO(**invalid_data)

        # None should be valid
        valid_data = dict(shipping_info_dto_data)
        valid_data["email_address"] = None
        dto = ShippingInfoDTO(**valid_data)
        assert dto.email_address is None

    def test_phone_validation(
        self,
        mocker: MockerFixture,
        shipping_info_dto_data: dict,
    ) -> None:
        """Test validation of phone_number field."""
        # Set up the mock
        patcher = mocker.patch("src.application.dtos.shipping_info_dto.phonenumbers")
        patcher.parse.return_value = mocker.Mock()
        patcher.is_valid_number.return_value = True
        patcher.format_number.return_value = "+31612345678"
        patcher.NumberParseException = phonenumbers.NumberParseException

        # Test with valid phone
        dto = ShippingInfoDTO(**shipping_info_dto_data)
        assert dto.phone_number == "+31612345678"

        # Test with invalid phone
        patcher.is_valid_number.return_value = False
        with pytest.raises(ValueError, match="Invalid phone number format"):
            ShippingInfoDTO(**shipping_info_dto_data)

        # Test with parsing error
        patcher.parse.side_effect = phonenumbers.NumberParseException(
            1,
            "Cannot parse",
        )
        dto = ShippingInfoDTO(**shipping_info_dto_data)
        assert dto.phone_number is None

        # Test with None phone number
        patcher.parse.side_effect = None
        data = dict(shipping_info_dto_data)
        data["phone_number"] = None
        dto = ShippingInfoDTO(**data)
        assert dto.phone_number is None

    def test_shipping_date_validation(self, shipping_info_dto_data: dict) -> None:
        """Test validation of estimated_shipping_date field."""
        # Past date should fail
        invalid_data = dict(shipping_info_dto_data)
        invalid_data["estimated_shipping_date"] = date(2000, 1, 1)

        with pytest.raises(
            ValueError,
            match="Estimated shipping date must be in the future",
        ):
            ShippingInfoDTO(**invalid_data)

        # None should set default date (7 days in future)
        today = datetime.now(tz=timezone.utc).date()
        data = dict(shipping_info_dto_data)
        data["estimated_shipping_date"] = None

        dto = ShippingInfoDTO(**data)
        assert dto.estimated_shipping_date == today + timedelta(days=7)

    def test_default_shipping_cost(self, shipping_info_dto_data: dict) -> None:
        """Test that shipping_cost gets a default if None."""
        data = dict(shipping_info_dto_data)
        data["shipping_cost"] = None

        dto = ShippingInfoDTO(**data)

        assert dto.shipping_cost is not None
        assert dto.shipping_cost.amount == 0.0
        assert dto.shipping_cost.currency == "EUR"

    def test_from_domain(
        self,
        mocker: MockerFixture,
        mocked_shipping_info: Mock,
    ) -> None:
        """Test conversion from domain model to DTO."""
        # Setup mocks and patchers
        mocked_address_dto = mocker.Mock(spec=AddressDTO, country="NL")
        mock_money_dto = mocker.Mock(spec=MoneyDTO)
        patcher_address = mocker.patch(
            "src.application.dtos.address_dto.AddressDTO.from_domain",
            return_value=mocked_address_dto,
        )
        patcher_money = mocker.patch(
            "src.application.dtos.money_dto.MoneyDTO.from_domain",
            return_value=mock_money_dto,
        )

        # Convert from domain
        dto = ShippingInfoDTO.from_domain(mocked_shipping_info)

        # Verify
        assert dto.address == mocked_address_dto
        assert dto.carrier == mocked_shipping_info.carrier
        assert dto.shipping_method == mocked_shipping_info.shipping_method
        assert dto.shipping_cost == mock_money_dto
        assert (
            dto.estimated_shipping_date == mocked_shipping_info.estimated_shipping_date
        )
        assert dto.email_address == mocked_shipping_info.email_address
        assert dto.phone_number == mocked_shipping_info.phone_number

        patcher_address.assert_called_once_with(
            mocked_shipping_info.address,
        )
        patcher_money.assert_called_once_with(
            mocked_shipping_info.shipping_cost,
        )

    def test_to_domain(
        self,
        mocker: MockerFixture,
        shipping_info_dto_data: dict,
    ) -> None:
        """Test conversion from DTO to domain model."""
        dto = ShippingInfoDTO(**shipping_info_dto_data)

        # Create mocks for to_domain methods
        mock_address = Mock(spec=Address)
        mock_money = Mock(spec=Money)
        patcher_address = mocker.patch(
            "src.application.dtos.address_dto.AddressDTO.to_domain",
            return_value=mock_address,
        )
        patcher_money = mocker.patch(
            "src.application.dtos.money_dto.MoneyDTO.to_domain",
            return_value=mock_money,
        )

        # Convert to domain
        domain = dto.to_domain()

        # Verify
        assert isinstance(domain, ShippingInfo)
        assert domain.address == mock_address
        assert domain.carrier == dto.carrier
        assert domain.shipping_method == dto.shipping_method
        assert domain.shipping_cost == mock_money
        assert domain.estimated_shipping_date == dto.estimated_shipping_date
        assert domain.email_address == dto.email_address
        assert domain.phone_number == dto.phone_number
        patcher_address.assert_called_once()
        patcher_money.assert_called_once()
