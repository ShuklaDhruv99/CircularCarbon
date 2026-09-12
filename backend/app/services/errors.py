"""Shared service-layer error types."""


class NotFoundError(Exception):
    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(message)


class ValidationError(Exception):
    """Raised when request input fails a domain-level validation rule.

    Maps to HTTP 422 at the API layer (see `app/main.py`).
    """

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(message)
