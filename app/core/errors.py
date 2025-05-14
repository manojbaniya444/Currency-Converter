"""Custom error types for the application."""

from typing import Any, Dict, List, Optional

from fastapi import HTTPException, status


class ExchangeAPIError(HTTPException):
    """Exception raise when there is an error with the exchange rate api."""

    def __init__(
        self,
        detail: str = "Error communicating with the exchange api.",
        status_code: int = status.HTTP_503_SERVICE_UNAVAILABLE,
    ) -> None:
        """Initialize the HTTPException in base class."""
        super().__init__(status_code=status_code, detail=detail)


class CurrencyNotFoundError(HTTPException):
    """Exception raise when a requested currency is not found."""

    def __init__(
        self,
        currency_code: str,
        available_currencies: Optional[List[str]] = None,
    ) -> None:
        """Init the execption."""
        detail: Dict[str, Any] = {
            "error": f"Currency '{currency_code}' not found",
            "message": "Please provide a valid currency code",
        }

        if available_currencies:
            detail["available_currencies"] = available_currencies

        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)


class InvalidAmountError(HTTPException):
    """Exception raise when an invalid amount is provided."""

    def __init__(self, detail: str = "Amoung must be a positive amount") -> None:
        """Init the exception."""
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)
