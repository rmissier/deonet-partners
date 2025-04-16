"""Unit tests for the OrderLine domain model."""

import uuid
from collections.abc import Generator

import pytest
from pytest_mock import MockerFixture

from src.domain.models.money import Money
from src.domain.models.order_line import OrderLine


@pytest.fixture
def order_line() -> OrderLine:
    """Create a sample order line for testing."""
    return OrderLine(
        product_id="prod-123",
        quantity=2,
        unit_price=Money(amount=10.0, currency="EUR"),
        design_ids=["design-1", "design-2"],
    )


class TestOrderLine:
    """Test cases for OrderLine domain model."""

    def test_initialization(self, order_line: OrderLine) -> None:
        """Test that an OrderLine can be properly initialized."""
        assert order_line.product_id == "prod-123"
        assert order_line.quantity == 2  # noqa: PLR2004
        assert order_line.unit_price.amount == 10.0  # noqa: PLR2004
        assert order_line.unit_price.currency == "EUR"
        assert order_line.design_ids == ["design-1", "design-2"]
        assert order_line.line_id is not None
        assert isinstance(order_line.line_id, str)
        uuid.UUID(order_line.line_id)
        assert order_line.line_total.amount == 20.0  # noqa: PLR2004

    def test_default_values(self) -> None:
        """Test that default values are properly set."""
        order_line = OrderLine(
            product_id="prod-123",
            quantity=2,
            unit_price=Money(amount=10.0, currency="EUR"),
        )

        assert order_line.design_ids == []
        assert isinstance(order_line.line_id, str)
        uuid.UUID(order_line.line_id)

    def test_line_total_calculation(
        self,
        order_line: OrderLine,
    ) -> None:
        """Test that line_total correctly calculates price * quantity."""
        result = order_line.line_total
        assert result.amount == order_line.unit_price.amount * order_line.quantity

    def test_add_design_id(self, order_line: OrderLine) -> None:
        """Test adding a design ID to the order line."""
        # Since the class is frozen, this should modify the list in-place
        # but not reassign the list reference
        initial_list = order_line.design_ids
        order_line.add_design_id("design-3")

        assert "design-3" in order_line.design_ids
        # Verify it's the same list object (modified in-place)
        assert order_line.design_ids is initial_list

    def test_add_duplicate_design_id(self, order_line: OrderLine) -> None:
        """Test that adding a duplicate design ID has no effect."""
        initial_count = len(order_line.design_ids)
        # Add an existing design ID
        order_line.add_design_id("design-1")

        assert len(order_line.design_ids) == initial_count
        assert order_line.design_ids.count("design-1") == 1  # Still only one occurrence

    def test_add_empty_design_id(self, order_line: OrderLine) -> None:
        """Test that adding an empty design ID raises ValueError."""
        with pytest.raises(ValueError, match="Design ID must be a non-empty string"):
            order_line.add_design_id("")

        with pytest.raises(ValueError, match="Design ID must be a non-empty string"):
            order_line.add_design_id("   ")  # Only whitespace

    def test_immutability(
        self,
        order_line: OrderLine,
        mocker: Generator[MockerFixture, None, None],
    ) -> None:
        """Test that OrderLine instances are immutable."""
        with pytest.raises(AttributeError):
            order_line.product_id = "new-product"

        with pytest.raises(AttributeError):
            order_line.quantity = 5

        with pytest.raises(AttributeError):
            order_line.unit_price = mocker.Mock()

        with pytest.raises(AttributeError):
            order_line.line_id = "new-id"
