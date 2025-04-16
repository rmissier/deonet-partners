"""Unit tests for the Order domain model."""

import uuid
from datetime import date
from unittest.mock import Mock

import pytest
from pytest_mock import MockerFixture

from src.domain.models.money import Money
from src.domain.models.order import Order
from src.domain.models.order_status import OrderStatus


@pytest.fixture
def mocked_shipping_info(mocker: MockerFixture) -> Mock:
    """Create a mocked shipping info instance."""
    mock = mocker.Mock()
    mock.shipping_cost = Money(amount=10.0)
    mock.update_address = mocker.Mock()
    return mock


@pytest.fixture
def mocked_order_line(mocker: MockerFixture) -> Mock:
    """Create a mocked order line instance."""
    mock = mocker.Mock()
    mock.line_id = str(uuid.uuid4())
    mock.line_total = Money(amount=20.0)
    return mock


@pytest.fixture
def sample_order(mocked_shipping_info: Mock, mocked_order_line: Mock) -> Order:
    """Create a sample order for testing."""
    return Order(
        order_id=str(uuid.uuid4()),
        customer_id="customer123",
        external_id="ext456",
        source_name="website",
        shipping_info=mocked_shipping_info,
        order_lines=[mocked_order_line],
    )


class TestOrder:
    """Test cases for Order domain model."""

    def test_order_initialization(
        self,
        mocked_shipping_info: Mock,
        mocked_order_line: Mock,
    ) -> None:
        """Test that an order can be properly initialized with valid data."""
        order = Order(
            customer_id="customer123",
            external_id="ext456",
            source_name="website",
            shipping_info=mocked_shipping_info,
            order_lines=[mocked_order_line],
        )

        assert order.customer_id == "customer123"
        assert order.external_id == "ext456"
        assert order.source_name == "website"
        assert order.shipping_info == mocked_shipping_info
        assert len(order.order_lines) == 1
        assert order.order_lines[0] == mocked_order_line
        assert order.status == OrderStatus.NEW
        assert order.erp_id is None
        assert isinstance(order.order_id, str)
        assert isinstance(order.order_date, date)

    def test_total_amount_calculation(
        self,
        mocker: MockerFixture,
        sample_order: Order,
    ) -> None:
        """Test that total_amount correctly sums order lines and shipping."""
        # Setup: order has one line of $20 and $10 shipping
        assert sample_order.total_amount.amount == 30.0  # noqa: PLR2004

        # Add another line of $20
        mock_line2 = mocker.Mock()
        mock_line2.line_total = Money(amount=20.0)
        sample_order.order_lines.append(mock_line2)

        assert sample_order.total_amount.amount == 50.0  # noqa: PLR2004

    def test_mark_as_processing_success(self, sample_order: Order) -> None:
        """Test successful transition to PROCESSING status."""
        sample_order.mark_as_processing()
        assert sample_order.status == OrderStatus.PROCESSING

    def test_mark_as_processing_invalid_status(self, sample_order: Order) -> None:
        """Test that only NEW orders can be marked as PROCESSING."""
        # First move to PROCESSING
        sample_order.mark_as_processing()

        # Then try again - should raise ValueError
        with pytest.raises(ValueError, match="Order cannot be processed from status"):
            sample_order.mark_as_processing()

    def test_mark_as_processing_no_lines(self, mocked_shipping_info: Mock) -> None:
        """Test that orders without lines cannot be marked as PROCESSING."""
        order = Order(
            customer_id="customer123",
            external_id="ext456",
            source_name="website",
            shipping_info=mocked_shipping_info,
            order_lines=[],
        )

        with pytest.raises(
            ValueError,
            match="Order cannot be processed without order lines",
        ):
            order.mark_as_processing()

    def test_mark_as_completed(self, sample_order: Order) -> None:
        """Test transition to COMPLETED status."""
        # From NEW to COMPLETED (direct completion)
        sample_order.mark_as_completed()
        assert sample_order.status == OrderStatus.COMPLETED

        # Reset and test from PROCESSING to COMPLETED
        object.__setattr__(sample_order, "status", OrderStatus.PROCESSING)
        sample_order.mark_as_completed()
        assert sample_order.status == OrderStatus.COMPLETED

    def test_mark_as_failed(self, sample_order: Order) -> None:
        """Test transition to FAILED status with reason."""
        sample_order.mark_as_failed("Out of stock")
        assert sample_order.status == OrderStatus.FAILED

    def test_assign_erp_id(self, sample_order: Order) -> None:
        """Test assigning ERP ID to an order."""
        sample_order.assign_erp_id("ERP12345")
        assert sample_order.erp_id == "ERP12345"

    def test_assign_empty_erp_id(self, sample_order: Order) -> None:
        """Test that empty ERP IDs are not allowed."""
        with pytest.raises(ValueError, match="ERP ID cannot be empty"):
            sample_order.assign_erp_id("")

        with pytest.raises(ValueError, match="ERP ID cannot be empty"):
            sample_order.assign_erp_id("   ")

    def test_add_order_line(self, sample_order: Order) -> None:
        """Test adding an order line to NEW orders."""
        initial_count = len(sample_order.order_lines)
        new_line = Mock()
        new_line.line_id = str(uuid.uuid4())

        sample_order.add_order_line(new_line)

        assert len(sample_order.order_lines) == initial_count + 1
        assert sample_order.order_lines[-1] == new_line

    def test_add_order_line_invalid_status(
        self,
        sample_order: Order,
        mocked_order_line: Mock,
    ) -> None:
        """Test that lines can only be added to NEW orders."""
        object.__setattr__(sample_order, "status", OrderStatus.PROCESSING)

        with pytest.raises(
            ValueError,
            match="Cannot modify lines unless order status is NEW",
        ):
            sample_order.add_order_line(mocked_order_line)

    def test_remove_order_line(self, sample_order: Order) -> None:
        """Test removing an order line from an order."""
        line_id = sample_order.order_lines[0].line_id
        initial_count = len(sample_order.order_lines)

        sample_order.remove_order_line(line_id)

        # Since we're mocking with a list comprehension, we need to check differently
        assert len(sample_order.order_lines) < initial_count

    def test_update_shipping_address(self, sample_order: Order) -> None:
        """Test updating the shipping address."""
        mock_address = Mock()

        # Method returns a new Order instance
        sample_order.update_shipping_address(mock_address)

        # Check that update_address was called on shipping_info
        sample_order.shipping_info.update_address.assert_called_once_with(mock_address)
