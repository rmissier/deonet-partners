"""Data Transfer Object for OrderLine entity using Pydantic for validation."""

from __future__ import annotations

import uuid

from pydantic import BaseModel, Field, model_validator

from src.application.dtos.money_dto import MoneyDTO
from src.domain.models.order_line import OrderLine


class OrderLineDTO(BaseModel):
    """DTO representation of the OrderLine entity with validation."""

    product_id: str = Field(..., min_length=1)
    quantity: int = Field(..., gt=0)
    unit_price: MoneyDTO | None = None
    design_ids: list[str] = Field(default_factory=list, min_items=1)
    line_id: str = Field(default_factory=lambda: str(uuid.uuid4()))

    @model_validator(mode="after")
    def ensure_unit_price(self) -> OrderLineDTO:
        """Ensure unit_price is set."""
        if isinstance(self.unit_price, (int, float)):
            self.unit_price = MoneyDTO(amount=self.unit_price)
        if not isinstance(self.unit_price, MoneyDTO):
            self.unit_price = MoneyDTO(amount=0.0)
        return self

    @classmethod
    def from_domain(cls, order_line: OrderLine) -> OrderLineDTO:
        """Convert domain OrderLine to OrderLineDTO.

        Args:
            order_line: Domain OrderLine entity

        Returns:
            Equivalent OrderLineDTO instance

        """
        return cls(
            product_id=order_line.product_id,
            quantity=order_line.quantity,
            unit_price=MoneyDTO.from_domain(order_line.unit_price),
            design_ids=order_line.design_ids,
            line_id=order_line.line_id,
        )

    def to_domain(self) -> OrderLine:
        """Convert this OrderLineDTO to a domain OrderLine entity.

        Returns:
            Domain OrderLine entity

        """
        return OrderLine(
            product_id=self.product_id,
            quantity=self.quantity,
            unit_price=self.unit_price.to_domain(),
            design_ids=self.design_ids,
            line_id=self.line_id,
        )

    class Config:
        """Pydantic configuration."""

        str_strip_whitespace = True
        validate_default = True
