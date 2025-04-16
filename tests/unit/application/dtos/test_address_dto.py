"""Unit tests for the AddressDTO application DTO."""

import pytest
from pydantic import ValidationError

from src.application.dtos.address_dto import AddressDTO
from src.domain.models.address import Address


@pytest.fixture
def valid_address_data() -> dict:
    """Fixture providing valid data for creating an AddressDTO."""
    return {
        "recipient_name": "John Doe",
        "street1": "123 Main St",
        "city": "Amsterdam",
        "postal_code": "1011AB",
        "country": "nl",  # Lowercase to test normalization
        "street2": "Floor 2",
        "state_province": "North Holland",
    }


@pytest.fixture
def domain_address() -> Address:
    """Fixture providing a valid Address domain object."""
    return Address(
        recipient_name="John Doe",
        street1="123 Main St",
        city="Amsterdam",
        postal_code="1011AB",
        country="NL",
        street2="Floor 2",
        state_province="North Holland",
    )


class TestAddressDTO:
    """Test cases for AddressDTO."""

    def test_initialization(self, valid_address_data: dict) -> None:
        """Test that AddressDTO can be initialized with valid data."""
        dto = AddressDTO(**valid_address_data)

        assert dto.recipient_name == "John Doe"
        assert dto.street1 == "123 Main St"
        assert dto.city == "Amsterdam"
        assert dto.postal_code == "1011AB"
        assert dto.country == "NL"  # Should be uppercase
        assert dto.street2 == "Floor 2"
        assert dto.state_province == "North Holland"

    def test_validation_recipient_name(self) -> None:
        """Test validation of recipient_name field."""
        with pytest.raises(ValidationError):
            AddressDTO(
                recipient_name="",  # Empty name
                street1="123 Main St",
                city="Amsterdam",
                postal_code="1011AB",
                country="NL",
            )

    def test_validation_street1(self) -> None:
        """Test validation of street1 field."""
        with pytest.raises(ValidationError):
            AddressDTO(
                recipient_name="John Doe",
                street1="",  # Empty street
                city="Amsterdam",
                postal_code="1011AB",
                country="NL",
            )

    def test_validation_city(self) -> None:
        """Test validation of city field."""
        with pytest.raises(ValidationError):
            AddressDTO(
                recipient_name="John Doe",
                street1="123 Main St",
                city="",  # Empty city
                postal_code="1011AB",
                country="NL",
            )

    def test_validation_postal_code(self) -> None:
        """Test validation of postal_code field."""
        with pytest.raises(ValidationError):
            AddressDTO(
                recipient_name="John Doe",
                street1="123 Main St",
                city="Amsterdam",
                postal_code="",  # Empty postal code
                country="NL",
            )

    def test_validation_country(self) -> None:
        """Test validation of country field."""
        # Test country too short
        with pytest.raises(ValidationError):
            AddressDTO(
                recipient_name="John Doe",
                street1="123 Main St",
                city="Amsterdam",
                postal_code="1011AB",
                country="N",  # Too short
            )

        # Test country too long
        with pytest.raises(ValidationError):
            AddressDTO(
                recipient_name="John Doe",
                street1="123 Main St",
                city="Amsterdam",
                postal_code="1011AB",
                country="NLD",  # Too long
            )

    def test_country_normalization(self) -> None:
        """Test that country code is normalized to uppercase."""
        dto = AddressDTO(
            recipient_name="John Doe",
            street1="123 Main St",
            city="Amsterdam",
            postal_code="1011AB",
            country="nl",  # Lowercase
        )
        assert dto.country == "NL"  # Should be uppercase

    def test_optional_fields(self) -> None:
        """Test optional fields default values."""
        dto = AddressDTO(
            recipient_name="John Doe",
            street1="123 Main St",
            city="Amsterdam",
            postal_code="1011AB",
            country="NL",
            # No street2 or state_province
        )

        assert dto.street2 == ""
        assert dto.state_province == ""

    def test_from_domain(self, domain_address: Address) -> None:
        """Test conversion from domain model to DTO."""
        dto = AddressDTO.from_domain(domain_address)

        assert dto.recipient_name == domain_address.recipient_name
        assert dto.street1 == domain_address.street1
        assert dto.city == domain_address.city
        assert dto.postal_code == domain_address.postal_code
        assert dto.country == domain_address.country
        assert dto.street2 == domain_address.street2
        assert dto.state_province == domain_address.state_province

    def test_to_domain(self, valid_address_data: dict) -> None:
        """Test conversion from DTO to domain model."""
        dto = AddressDTO(**valid_address_data)
        address = dto.to_domain()

        assert isinstance(address, Address)
        assert address.recipient_name == dto.recipient_name
        assert address.street1 == dto.street1
        assert address.city == dto.city
        assert address.postal_code == dto.postal_code
        assert address.country == dto.country
        assert address.street2 == dto.street2
        assert address.state_province == dto.state_province

    def test_whitespace_stripping(self) -> None:
        """Test that whitespace is stripped from string fields."""
        dto = AddressDTO(
            recipient_name=" John Doe ",
            street1=" 123 Main St ",
            city=" Amsterdam ",
            postal_code=" 1011AB ",
            country=" NL ",
        )

        assert dto.recipient_name == "John Doe"
        assert dto.street1 == "123 Main St"
        assert dto.city == "Amsterdam"
        assert dto.postal_code == "1011AB"
        assert dto.country == "NL"
