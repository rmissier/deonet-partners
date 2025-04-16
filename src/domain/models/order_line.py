"""OrderLine Entity.

This module defines the OrderLine entity, which represents a line item within an order.
It includes properties for product ID, quantity, unit price, and design IDs.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.domain.models.money import Money


@dataclass(frozen=True, kw_only=True)
class OrderLine:
    """Represents a line item within an order."""

    product_id: str
    quantity: int
    unit_price: Money
    design_ids: list[str] = field(default_factory=list)
    line_id: str = field(default_factory=lambda: str(uuid.uuid4()))

    @property
    def line_total(self) -> Money:
        """Calculate the total price for this order line."""
        return self.unit_price * self.quantity

    def add_design_id(self, design_id: str) -> None:
        """Add a design ID to the order line if not already present."""
        stripped_id = design_id.strip()
        if not stripped_id:
            msg = "Design ID must be a non-empty string"
            raise ValueError(msg)
        if stripped_id not in self.design_ids:
            self.design_ids.append(stripped_id)
