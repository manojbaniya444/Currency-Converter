"""Currency Converter."""

# core
from typing import Dict, List

# fastapi
from fastapi import APIRouter, HTTPException, Query, status

# app
from app.api.dependencies import ExchangeServiceDep
from app.core.errors import InvalidAmountError

converter_router = APIRouter(prefix="/api/v1/currency", tags=["currency"])


@converter_router.get(
    "/rates/{base_currency}",
    response_model=Dict[str, float],
    summary="Get latest exchange rates",
    description="Fetch the latest exchange rates for the specified base currency",
)
async def get_exchange_rates(
    exchange_service: ExchangeServiceDep, base_currency: str = "USD"
) -> Dict[str, float]:
    """
    Get the latest exchange rates for a base currency.

    Args:
        base_currency: 3-letter currency code (default: USD)
        exchange_service: ExchangeService dependency

    Returns:
        Dict of currency codes and their exchange rates
    """
    try:
        rates = await exchange_service.get_exchange_rates(base_currency.upper())
        return rates
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error))


@converter_router.get(
    "/convert",
    summary="Convert currency",
    description="Convert an amount one currency to another",
)
async def convert_currency(
    exchange_service: ExchangeServiceDep,
    amount: float = Query(..., gt=0, description="Amount to convert"),
    from_currency: str = Query(..., description="Source currency code"),
    to_currency: str = Query(..., description="Target currency code"),
) -> Dict:
    """
    Convert an amount from one currency to another.

    Args:
        amount: The amount to convert (must be positive)
        from_currency: Source currency code
        to_currency: Target currency code
        exchange_service: ExchangeService dependency

    Returns:
        Dict containing conversion details
    """
    try:
        result = await exchange_service.convert_currency(
            amount, from_currency.upper(), to_currency.upper()
        )
        return result
    except ValueError:
        raise InvalidAmountError()


@converter_router.get(
    "/currencies",
    response_model=List[str],
    summary="Get available currencies",
    description="Get a list of all available currency codes",
)
async def get_available_currencies(
    exchange_service: ExchangeServiceDep,
) -> List[str]:
    """
    Get a list of all available currency codes.

    Args:
        exchange_service: ExchangeService dependency

    Returns:
        List of currency codes
    """
    return await exchange_service.get_available_currencies()
