"""Unit tests for the OrderDTO application DTO."""

import uuid
from datetime import date, datetime, timedelta, timezone
from typing import Any
from unittest.mock import Mock

import pytest
from pydantic import ValidationError

from src.application.dtos.address_dto import AddressDTO
from src.application.dtos.money_dto import MoneyDTO
from src.application.dtos.order_dto import OrderDTO
from src.application.dtos.order_line_dto import OrderLineDTO
from src.application.dtos.shipping_info_dto import ShippingInfoDTO
from src.domain.models.order import Order
from src.domain.models.order_status import OrderStatus


@pytest.fixture
def money_dto() -> MoneyDTO:
    """Create a money DTO."""
    return MoneyDTO(amount=19.99, currency="EUR")


@pytest.fixture
def address_dto() -> AddressDTO:
    """Create an address DTO."""
    return AddressDTO(
        recipient_name="John Doe",
        street1="123 Main St",
        city="Amsterdam",
        postal_code="1011AB",
        country="NL",
        street2="Floor 2",
        state_province="North Holland",
    )


@pytest.fixture
def shipping_info_dto(address_dto: AddressDTO, money_dto: MoneyDTO) -> ShippingInfoDTO:
    """Create a shipping info DTO."""
    return ShippingInfoDTO(
        address=address_dto,
        carrier="DHL",
        shipping_method="Express",
        shipping_cost=money_dto,
        estimated_shipping_date=(
            datetime.now(tz=timezone.utc) + timedelta(days=10)
        ).date(),
        email_address="test@example.com",
        phone_number="+31612345678",
    )


@pytest.fixture
def order_line_dto(money_dto: MoneyDTO) -> OrderLineDTO:
    """Create an order line DTO."""
    return OrderLineDTO(
        line_id=str(uuid.uuid4()),
        product_id="prod-123",
        quantity=2,
        unit_price=money_dto,
        design_ids=["design-1", "design-2"],
    )


@pytest.fixture
def order_dto_data(
    shipping_info_dto: ShippingInfoDTO,
    order_line_dto: OrderLineDTO,
) -> dict[str, Any]:
    """Fixture providing valid data for creating an OrderDTO."""
    return {
        "order_id": str(uuid.uuid4()),
        "customer_id": "cust-123",
        "external_id": "ext-456",
        "source_name": "webshop",
        "shipping_info": shipping_info_dto,
        "order_lines": [order_line_dto, order_line_dto],
        "status": OrderStatus.NEW,
        "erp_id": "ERP-789",
        "order_date": datetime.now(tz=timezone.utc).date(),
    }


@pytest.fixture
def order(order_dto_data: dict[str, Any]) -> Order:
    """Create an Order object."""
    return OrderDTO(**order_dto_data).to_domain()


class TestOrderDTO:
    """Test cases for OrderDTO."""

    def test_initialization(self, order_dto_data: dict[str, Any]) -> None:
        """Test that OrderDTO can be initialized with valid data."""
        dto = OrderDTO(**order_dto_data)

        assert dto.order_id == order_dto_data["order_id"]
        assert dto.customer_id == "cust-123"
        assert dto.external_id == "ext-456"
        assert dto.source_name == "webshop"
        assert dto.shipping_info == order_dto_data["shipping_info"]
        assert dto.order_lines == order_dto_data["order_lines"]
        assert dto.status == OrderStatus.NEW.value
        assert dto.erp_id == "ERP-789"
        assert dto.order_date == order_dto_data["order_date"]

    def test_default_values(
        self,
        shipping_info_dto: ShippingInfoDTO,
        order_line_dto: OrderLineDTO,
    ) -> None:
        """Test that default values are properly set."""
        # Minimal required fields
        dto = OrderDTO(
            customer_id="cust-123",
            external_id="ext-456",
            source_name="webshop",
            shipping_info=shipping_info_dto,
            order_lines=[order_line_dto],
        )

        assert dto.order_id is not None  # Auto-generated
        assert dto.status == OrderStatus.NEW
        assert dto.erp_id == ""
        assert isinstance(dto.order_date, date)

    def test_customer_id_validation(self, order_dto_data: dict[str, Any]) -> None:
        """Test validation of customer_id field."""
        # Empty customer_id should fail
        invalid_data = dict(order_dto_data)
        invalid_data["customer_id"] = ""

        with pytest.raises(ValidationError):
            OrderDTO(**invalid_data)

        # Whitespace-only customer_id should fail after stripping
        invalid_data["customer_id"] = "   "
        with pytest.raises(ValidationError):
            OrderDTO(**invalid_data)

    def test_external_id_validation(self, order_dto_data: dict[str, Any]) -> None:
        """Test validation of external_id field."""
        # Empty external_id should fail
        invalid_data = dict(order_dto_data)
        invalid_data["external_id"] = ""

        with pytest.raises(ValidationError):
            OrderDTO(**invalid_data)

    def test_source_name_validation(self, order_dto_data: dict[str, Any]) -> None:
        """Test validation of source_name field."""
        # Empty source_name should fail
        invalid_data = dict(order_dto_data)
        invalid_data["source_name"] = ""

        with pytest.raises(ValidationError):
            OrderDTO(**invalid_data)

    def test_order_lines_validation(self, shipping_info_dto: Mock) -> None:
        """Test validation of order_lines field."""
        # Empty order_lines should fail
        with pytest.raises(ValidationError):
            OrderDTO(
                customer_id="cust-123",
                external_id="ext-456",
                source_name="webshop",
                shipping_info=shipping_info_dto,
                order_lines=[],
            )

    def test_from_domain(self, order: Order) -> None:
        """Test conversion from domain model to DTO."""
        # Convert from domain
        dto = OrderDTO.from_domain(order)

        # Verify
        assert dto.customer_id == order.customer_id
        assert dto.external_id == order.external_id
        assert dto.shipping_info == ShippingInfoDTO.from_domain(order.shipping_info)
        assert dto.source_name == order.source_name
        assert dto.order_id == order.order_id
        assert dto.erp_id == order.erp_id
        assert dto.order_date == order.order_date
        assert len(dto.order_lines) == len(order.order_lines)
        assert dto.status == order.status

    def test_to_domain(
        self,
        order_dto_data: dict[str, Any],
    ) -> None:
        """Test conversion from DTO to domain model."""
        dto = OrderDTO(**order_dto_data)
        order = dto.to_domain()
        # Verify
        assert order.customer_id == dto.customer_id
        assert order.external_id == dto.external_id
        assert order.source_name == dto.source_name
        assert order.order_id == dto.order_id
        assert order.erp_id == dto.erp_id
        assert order.order_date == dto.order_date
        assert order.status == dto.status
        assert len(order.order_lines) == len(dto.order_lines)
        assert order.shipping_info == dto.shipping_info.to_domain()
        assert order.shipping_info.address == dto.shipping_info.address.to_domain()
        assert (
            order.shipping_info.shipping_cost
            == dto.shipping_info.shipping_cost.to_domain()
        )
        assert (
            order.shipping_info.estimated_shipping_date
            == dto.shipping_info.estimated_shipping_date
        )
        assert order.shipping_info.email_address == dto.shipping_info.email_address
        assert order.shipping_info.phone_number == dto.shipping_info.phone_number
        assert order.shipping_info.carrier == dto.shipping_info.carrier
        assert order.shipping_info.shipping_method == dto.shipping_info.shipping_method
