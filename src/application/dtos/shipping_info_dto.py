"""Data Transfer Object for ShippingInfo entity using Pydantic for validation."""

from __future__ import annotations

import logging
from datetime import date, datetime, timedelta, timezone
from typing import Self

import phonenumbers
from pydantic import BaseModel, EmailStr, Field, model_validator

from src.application.dtos.address_dto import AddressDTO
from src.application.dtos.money_dto import MoneyDTO
from src.domain.models.shipping_info import ShippingInfo

logger = logging.getLogger(__name__)


class ShippingInfoDTO(BaseModel):
    """DTO representation of the ShippingInfo entity with validation."""

    address: AddressDTO
    carrier: str = Field(..., min_length=1)
    shipping_method: str = Field(default="Standard", min_length=1)
    shipping_cost: MoneyDTO | None = None
    estimated_shipping_date: date | None = None
    email_address: EmailStr | None = None
    phone_number: str | None = None

    class Config:
        """Pydantic configuration."""

        populate_by_name = True
        str_strip_whitespace = True

    @model_validator(mode="after")
    def validate_phone(self) -> Self:
        """Validate and format phone number."""
        if not self.phone_number:
            return self
        try:
            parsed_number = phonenumbers.parse(self.phone_number, self.address.country)
            if not phonenumbers.is_valid_number(parsed_number):
                msg = f"Invalid phone number format: {self.phone_number}"
                raise ValueError(msg)

            # Format to E.164
            self.phone_number = phonenumbers.format_number(
                parsed_number,
                phonenumbers.PhoneNumberFormat.E164,
            )
        except phonenumbers.NumberParseException:
            logger.exception("Error parsing phone number: %s", self.phone_number)
            self.phone_number = None

        return self

    @model_validator(mode="after")
    def validate_shipping_date(self) -> Self:
        """Validate the estimated shipping date is in the future."""
        if self.estimated_shipping_date:
            today = datetime.now(tz=timezone.utc).date()
            if self.estimated_shipping_date <= today:
                msg = "Estimated shipping date must be in the future"
                raise ValueError(msg)
        else:
            # Set default (7 days from now)
            self.estimated_shipping_date = (
                datetime.now(tz=timezone.utc) + timedelta(days=7)
            ).date()

        return self

    @model_validator(mode="after")
    def set_default_shipping_cost(self) -> Self:
        """Set default shipping cost if not provided."""
        if isinstance(self.shipping_cost, (int, float)):
            self.shipping_cost = MoneyDTO(amount=self.shipping_cost)
        if not isinstance(self.shipping_cost, MoneyDTO):
            self.shipping_cost = MoneyDTO(amount=0.0)
        return self

    @classmethod
    def from_domain(cls, shipping_info: ShippingInfo) -> ShippingInfoDTO:
        """Convert domain ShippingInfo to ShippingInfoDTO.

        Args:
            shipping_info: Domain ShippingInfo entity

        Returns:
            Equivalent ShippingInfoDTO instance

        """
        return cls(
            address=AddressDTO.from_domain(shipping_info.address),
            carrier=shipping_info.carrier,
            shipping_method=shipping_info.shipping_method,
            shipping_cost=MoneyDTO.from_domain(shipping_info.shipping_cost),
            estimated_shipping_date=shipping_info.estimated_shipping_date,
            email_address=shipping_info.email_address,
            phone_number=shipping_info.phone_number,
        )

    def to_domain(self) -> ShippingInfo:
        """Convert this ShippingInfoDTO to a domain ShippingInfo entity.

        Returns:
            Domain ShippingInfo entity

        """
        return ShippingInfo(
            address=self.address.to_domain(),
            carrier=self.carrier,
            shipping_method=self.shipping_method,
            shipping_cost=self.shipping_cost.to_domain() if self.shipping_cost else None,
            estimated_shipping_date=self.estimated_shipping_date,
            email_address=self.email_address,
            phone_number=self.phone_number,
        )
