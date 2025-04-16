"""Represents a shipping address."""

from dataclasses import dataclass


@dataclass(frozen=True, kw_only=True)
class Address:
    """Represents a shipping address."""

    recipient_name: str
    street1: str
    city: str
    postal_code: str
    country: str
    street2: str = ""
    state_province: str = ""
