"""Unit tests for the OrderLineDTO application DTO."""

import uuid

import pytest
from pydantic import ValidationError
from pytest_mock import MockerFixture

from src.application.dtos.money_dto import MoneyDTO
from src.application.dtos.order_line_dto import OrderLineDTO
from src.domain.models.money import Money
from src.domain.models.order_line import OrderLine


@pytest.fixture
def money_dto() -> MoneyDTO:
    """Fixture providing a valid MoneyDTO instance."""
    return MoneyDTO(amount=19.99, currency="EUR")


@pytest.fixture
def order_line_dto_data(money_dto: MoneyDTO) -> dict:
    """Fixture providing valid data for creating an OrderLineDTO."""
    return {
        "product_id": "prod-123",
        "quantity": 2,
        "unit_price": money_dto,
        "design_ids": ["design-1", "design-2"],
        "line_id": str(uuid.uuid4()),
    }


@pytest.fixture
def order_line() -> OrderLine:
    """Fixture providing a valid OrderLine domain object."""
    return OrderLine(
        product_id="prod-123",
        quantity=2,
        unit_price=Money(amount=19.99),
        design_ids=["design-1", "design-2"],
        line_id=str(uuid.uuid4()),
    )


class TestOrderLineDTO:
    """Test cases for OrderLineDTO."""

    def test_initialization(self, order_line_dto_data: dict) -> None:
        """Test that OrderLineDTO can be initialized with valid data."""
        dto = OrderLineDTO(**order_line_dto_data)

        assert dto.product_id == order_line_dto_data["product_id"]
        assert dto.quantity == order_line_dto_data["quantity"]
        assert dto.unit_price == order_line_dto_data["unit_price"]
        assert dto.design_ids == order_line_dto_data["design_ids"]
        assert dto.line_id == order_line_dto_data["line_id"]

    def test_product_id_validation(self, order_line_dto_data: dict) -> None:
        """Test validation of product_id field."""
        # Empty product_id should fail
        invalid_data = dict(order_line_dto_data)
        invalid_data["product_id"] = ""

        with pytest.raises(ValidationError):
            OrderLineDTO(**invalid_data)

        # Whitespace-only product_id should fail after stripping
        invalid_data["product_id"] = "   "
        with pytest.raises(ValidationError):
            OrderLineDTO(**invalid_data)

    def test_quantity_validation(self, order_line_dto_data: dict) -> None:
        """Test validation of quantity field."""
        # Zero quantity should fail
        invalid_data = dict(order_line_dto_data)
        invalid_data["quantity"] = 0

        with pytest.raises(ValidationError):
            OrderLineDTO(**invalid_data)

        # Negative quantity should fail
        invalid_data["quantity"] = -1
        with pytest.raises(ValidationError):
            OrderLineDTO(**invalid_data)

    def test_design_ids_validation(self, order_line_dto_data: dict) -> None:
        """Test validation of design_ids field."""
        # Empty list should fail (min_items=1)
        invalid_data = dict(order_line_dto_data)
        invalid_data["design_ids"] = []

        with pytest.raises(ValidationError):
            OrderLineDTO(**invalid_data)

    def test_auto_generated_line_id(self, order_line_dto_data: dict) -> None:
        """Test that line_id is auto-generated if not provided."""
        data = dict(order_line_dto_data)
        data.pop("line_id")

        dto = OrderLineDTO(**data)

        assert dto.line_id is not None
        assert isinstance(dto.line_id, str)
        # Verify it's a valid UUID
        uuid.UUID(dto.line_id)

    def test_ensure_unit_price_validator(self, order_line_dto_data: dict) -> None:
        """Test that unit_price is defaulted if not provided."""
        data = dict(order_line_dto_data)
        data["unit_price"] = None

        dto = OrderLineDTO(**data)

        assert dto.unit_price is not None
        assert dto.unit_price.amount == 0.0
        assert dto.unit_price.currency == "EUR"

    def test_from_domain(
        self,
        mocker: MockerFixture,
        order_line: OrderLine,
    ) -> None:
        """Test conversion from domain model to DTO."""
        mock = mocker.patch(
            "src.application.dtos.money_dto.MoneyDTO.from_domain",
            return_value=MoneyDTO(amount=19.99),
        )
        dto = OrderLineDTO.from_domain(order_line)

        assert dto.product_id == order_line.product_id
        assert dto.quantity == order_line.quantity
        assert dto.design_ids == order_line.design_ids
        assert dto.line_id == order_line.line_id
        mock.assert_called_once_with(order_line.unit_price)

    def test_to_domain(self, order_line_dto_data: dict) -> None:
        """Test conversion from DTO to domain model."""
        dto = OrderLineDTO(**order_line_dto_data)

        domain = dto.to_domain()
        assert isinstance(domain, OrderLine)
        assert domain.product_id == dto.product_id
        assert domain.quantity == dto.quantity
        assert domain.design_ids == dto.design_ids
        assert domain.line_id == dto.line_id
        assert domain.unit_price == Money(amount=19.99, currency="EUR")
