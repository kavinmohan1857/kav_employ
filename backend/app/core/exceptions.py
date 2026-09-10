class DatabaseOperationError(Exception):
    """Raised when a database operation cannot be completed safely."""


class InvalidJobUpdateError(Exception):
    """Raised when a partial update conflicts with the stored job state."""
