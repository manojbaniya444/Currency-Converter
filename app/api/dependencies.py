"""API dependencies shared across routes."""

from typing import Annotated

from fastapi import Depends

from app.services.exchange_service import ExchangeService


def get_exchange_service() -> ExchangeService:
    """Dependency for getting the exchange service."""
    return ExchangeService()


ExchangeServiceDep = Annotated[ExchangeService, Depends(get_exchange_service)]
