"""ShippingInfo entity module.

This module defines the ShippingInfo entity, which represents shipping
information for an order.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta, timezone

from src.domain.models.address import Address
from src.domain.models.money import Money

logger = logging.getLogger(__name__)


@dataclass(frozen=True, kw_only=True)
class ShippingInfo:
    """Represents shipping information for an order."""

    address: Address
    carrier: str
    shipping_method: str = "Standard"
    shipping_cost: Money = field(default_factory=lambda: Money(amount=0.0))
    estimated_shipping_date: date | None = None
    email_address: str | None = None
    phone_number: str | None = None

    def update_estimated_shipping_date(self, days: int) -> None:
        """Update shipping date to givn number of days from today.

        Raises:
            ValueError: If days is a negative integer.

        """
        if days < 0:
            msg = "Days must be a positive integer"
            raise ValueError(msg)

        new_date = datetime.now(tz=timezone.utc).date()
        saturday = 5
        working_days = days
        while working_days > 0:
            new_date += timedelta(days=1)
            if new_date.weekday() < saturday:  # Monday to Friday
                working_days -= 1

        object.__setattr__(self, "estimated_shipping_date", new_date)

    def update_address(self, new_address: Address) -> None:
        """Update the shipping address."""
        if not isinstance(new_address, Address):
            msg = "New address must be an instance of Address"
            raise TypeError(msg)

        object.__setattr__(self, "address", new_address)
