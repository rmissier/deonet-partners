"""Data Transfer Object for Address domain model using Pydantic for validation."""

from __future__ import annotations

from pydantic import BaseModel, Field, field_validator

from src.domain.models.address import Address


class AddressDTO(BaseModel):
    """Data Transfer Object for Address entities with validation."""

    recipient_name: str = Field(..., min_length=1)
    street1: str = Field(..., min_length=1)
    city: str = Field(..., min_length=1)
    postal_code: str = Field(..., min_length=1)
    country: str = Field(..., min_length=2, max_length=2)
    street2: str = ""
    state_province: str = ""

    @field_validator("country")
    @classmethod
    def validate_country(cls, value: str) -> str:
        """Validate that country is a two-letter ISO country code."""
        return value.upper()

    @classmethod
    def from_domain(cls, address: Address) -> AddressDTO:
        """Convert domain Address to AddressDTO.

        Args:
            address: Domain address entity

        Returns:
            Equivalent AddressDTO instance

        """
        return cls(
            recipient_name=address.recipient_name,
            street1=address.street1,
            city=address.city,
            postal_code=address.postal_code,
            country=address.country,
            street2=address.street2 or "",
            state_province=address.state_province or "",
        )

    def to_domain(self) -> Address:
        """Convert this AddressDTO to a domain Address entity.

        Returns:
            Domain Address entity

        """
        return Address(
            recipient_name=self.recipient_name,
            street1=self.street1,
            city=self.city,
            postal_code=self.postal_code,
            country=self.country,
            street2=self.street2 or "",
            state_province=self.state_province or "",
        )

    class Config:
        """Pydantic configuration."""

        populate_by_name = True
        str_strip_whitespace = True
