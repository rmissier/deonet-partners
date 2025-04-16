"""Order entity representing a customer's order in the system.

This module defines the Order class, which serves as the aggregate root for
order-related operations. It includes properties for order ID, customer ID,
external ID, source, shipping information, order lines, status, order date,
and ERP ID. The class also provides methods for managing order state transitions,
adding/removing order lines, and updating shipping information.
"""

from __future__ import annotations

import logging
import uuid
from dataclasses import dataclass, field
from datetime import date, datetime, timezone
from typing import TYPE_CHECKING

from src.domain.models.money import Money
from src.domain.models.order_status import OrderStatus

if TYPE_CHECKING:
    from src.domain.models.address import Address
    from src.domain.models.order_line import OrderLine
    from src.domain.models.shipping_info import ShippingInfo

logger = logging.getLogger(__name__)


@dataclass(frozen=True, kw_only=True)
class Order:
    """Internal order representation (Aggregate Root)."""

    order_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    customer_id: str
    external_id: str
    source_name: str
    shipping_info: ShippingInfo
    order_lines: list[OrderLine] = field(default_factory=list)
    status: OrderStatus = OrderStatus.NEW
    erp_id: str | None = None
    order_date: date = field(
        default_factory=lambda: datetime.now(tz=timezone.utc).date(),
    )

    @property
    def total_amount(self) -> Money:
        """Calculate the total amount of the order."""
        line_total = Money(
            amount=0.0,
            currency=self.shipping_info.shipping_cost.currency,
        )
        for line in self.order_lines:
            line_total += line.line_total
        return line_total + self.shipping_info.shipping_cost

    # --- State Transitions / Commands (now return new instances) ---

    def mark_as_processing(self) -> None:
        """Return a new Order with PROCESSING status.

        Raises:
            ValueError: If the order is not in NEW status or has no lines.

        """
        if self.status != OrderStatus.NEW:
            msg = f"Order cannot be processed from status {self.status.value}"
            raise ValueError(msg)
        if not self.order_lines:
            msg = "Order cannot be processed without order lines"
            raise ValueError(msg)

        object.__setattr__(self, "status", OrderStatus.PROCESSING)
        logger.info("Order %s marked as PROCESSING.", self.order_id)

    def mark_as_completed(self) -> None:
        """Return a new Order with COMPLETED status.

        Raises:
            ValueError: If the order is not in PROCESSING or NEW status.

        """
        if self.status not in (OrderStatus.PROCESSING, OrderStatus.NEW):
            msg = f"Order cannot be completed from status {self.status.value}"
            raise ValueError(msg)

        object.__setattr__(self, "status", OrderStatus.COMPLETED)
        logger.info("Order %s marked as COMPLETED.", self.order_id)

    def mark_as_failed(self, reason: str) -> None:
        """Return a new Order with FAILED status.

        Args:
            reason: Reason for failure

        Raises:
            ValueError: If the order is not in PROCESSING or NEW status.

        """
        object.__setattr__(self, "status", OrderStatus.FAILED)
        logger.error("Order %s marked as FAILED. Reason: %s", self.order_id, reason)

    def assign_erp_id(self, erp_id: str) -> None:
        """Return a new Order with the assigned ERP ID.

        Args:
            erp_id: ERP system ID to assign

        Raises:
            ValueError: If the ERP ID is empty or already assigned.

        """
        stripped_id = erp_id.strip()
        if not stripped_id:
            msg = "ERP ID cannot be empty"
            raise ValueError(msg)

        if self.erp_id and self.erp_id != stripped_id:
            logger.warning("Overwriting existing ERP ID for order %s", self.order_id)

        object.__setattr__(self, "erp_id", stripped_id)
        logger.info("Assigned ERP ID %s to order %s", stripped_id, self.order_id)

    # --- Aggregate Management (now return new instances) ---

    def add_order_line(self, line: OrderLine) -> None:
        """Return a new Order with an additional order line.

        Args:
            line: OrderLine to add

        Raises:
            ValueError: If the order is not in NEW status.

        """
        if self.status != OrderStatus.NEW:
            msg = "Cannot modify lines unless order status is NEW"
            raise ValueError(msg)

        self.order_lines.append(line)
        logger.info("Added order line %s to order %s", line.line_id, self.order_id)

    def remove_order_line(self, line_id: str) -> None:
        """Return a new Order with the specified order line removed.

        Args:
            line_id: ID of the line to remove

        Raises:
            ValueError: If the order line with the specified ID is not found.

        """
        if self.status != OrderStatus.NEW:
            msg = "Cannot modify lines unless order status is NEW"
            raise ValueError(msg)

        order_lines = [line for line in self.order_lines if line.line_id != line_id]
        object.__setattr__(self, "order_lines", order_lines)
        logger.info("Removed order line %s from order %s", line_id, self.order_id)

    def update_shipping_address(self, new_address: Address) -> Order:
        """Return a new Order with updated shipping address.

        Args:
            new_address: New address to use

        Returns:
            New Order instance with updated shipping address

        """
        if self.status not in (OrderStatus.NEW, OrderStatus.PROCESSING):
            msg = (
                "Cannot update shipping address unless order status is NEW or PROCESSING"
            )
            raise ValueError(msg)

        self.shipping_info.update_address(new_address)
        logger.info("Updated shipping address for order %s", self.order_id)
