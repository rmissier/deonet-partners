"""OrderStatus enumeration module.

This module defines the possible statuses of an order in the system.
"""

from enum import Enum


class OrderStatus(Enum):
    """Represents the possible statuses of an order in the system."""

    NEW = "new"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
