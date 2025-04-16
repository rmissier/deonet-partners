"""Data Transfer Object for Order entity using Pydantic for validation."""

from __future__ import annotations

import uuid
from datetime import date, datetime, timezone

from pydantic import BaseModel, Field, model_validator

from src.application.dtos.order_line_dto import OrderLineDTO
from src.application.dtos.shipping_info_dto import ShippingInfoDTO
from src.domain.models.order import Order
from src.domain.models.order_status import OrderStatus


class OrderDTO(BaseModel):
    """DTO representation of the Order entity with validation."""

    order_id: str = Field(default=lambda: str(uuid.uuid4()), min_length=1)
    customer_id: str = Field(..., min_length=1)
    external_id: str = Field(..., min_length=1)
    source_name: str = Field(..., min_length=1)
    shipping_info: ShippingInfoDTO
    order_lines: list[OrderLineDTO] = Field(..., min_length=1)
    status: OrderStatus = OrderStatus.NEW
    erp_id: str = ""
    order_date: date = Field(
        default_factory=lambda: datetime.now(tz=timezone.utc).date(),
    )

    class Config:
        """Pydantic configuration."""

        populate_by_name = True
        str_strip_whitespace = True
        use_enum_values = True

    @model_validator(mode="after")
    def validate_order_has_lines(self) -> OrderDTO:
        """Validate that the order has at least one line."""
        if not self.order_lines:
            msg = "Order must have at least one order line"
            raise ValueError(msg)
        return self

    @classmethod
    def from_domain(cls, order: Order) -> OrderDTO:
        """Convert domain Order to OrderDTO.

        Args:
            order: Domain Order entity

        Returns:
            Equivalent OrderDTO instance

        """
        return cls(
            order_id=order.order_id,
            customer_id=order.customer_id,
            external_id=order.external_id,
            source_name=order.source_name,
            shipping_info=ShippingInfoDTO.from_domain(order.shipping_info),
            order_lines=[OrderLineDTO.from_domain(line) for line in order.order_lines],
            status=order.status,
            erp_id=order.erp_id,
            order_date=order.order_date,
        )

    def to_domain(self) -> Order:
        """Convert this OrderDTO to a domain Order entity.

        Returns:
            Domain Order entity

        """
        return Order(
            order_id=self.order_id,
            customer_id=self.customer_id,
            external_id=self.external_id,
            source_name=self.source_name,
            shipping_info=self.shipping_info.to_domain(),
            order_lines=[line.to_domain() for line in self.order_lines],
            status=self.status,
            erp_id=self.erp_id,
            order_date=self.order_date,
        )
