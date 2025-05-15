"""Currency exchange service."""

import json
import logging
from datetime import datetime
from typing import Dict, List, Optional

import httpx
import redis
import requests

from app.core.config import settings
from app.core.errors import CurrencyNotFoundError, ExchangeAPIError

logger = logging.getLogger(__name__)


class ExchangeService:
    """Service for handling currency exchange."""

    def __init__(self) -> None:
        """Init exchange service."""
        self.api_key = settings.EXCHANGE_API_KEY
        self.api_url = settings.EXCHANGE_API_URL

        self.redis_client: Optional[redis.Redis] = None
        if settings.REDIS_HOST:
            try:
                self.redis_client = redis.Redis(
                    host=settings.REDIS_HOST,
                    port=settings.REDIS_PORT,
                    decode_responses=True,
                )
                self.redis_client.ping()
                logger.info("Redis cache connection establish success.")

            except redis.ConnectionError:
                logger.warning("Failed to connect to Redis, running without cache.")
                self.redis_client = None

    async def get_exchange_rates(self, base_currency: str = "USD") -> Dict[str, float]:
        """
        Get the latest exchange rates for a base currency.

        Args:
            base_currency: The base currency code (default: USD)

        Returns:
            Dict of currency codes and their exchange rates

        Raises:
            CurrencyNotFoundError: If the base currency is not found
            ExchangeAPIError: If there is an error communicating with the exchange api
        """
        cache_key = f"exchange_rates:{base_currency}"
        rates_data = await self._get_from_cache(cache_key)

        if not rates_data or "rates" not in rates_data:
            rates_data = await self._fetch_from_api(base_currency)
            await self._store_in_cache(cache_key, rates_data)

        return rates_data["rates"]

    async def convert_currency(
        self,
        amount: float,
        from_currency: str,
        to_currency: str,
    ):
        """
        Convert an amount from one currency to another.

        Args:
            amount: The amount to convert
            from_currency: The source currency code
            to_currency: The target currency code

        Returns:
            Dict containing conversion details

        Raises:
            InvalidAmountError: If amount is not positive
            CurrencyNotFoundError: If either currency is not found
            ExchangeAPIError: If there is an error with the exchange API
        """
        if amount <= 0:
            raise ValueError("Amoung must be positive")

        rates = await self.get_exchange_rates(from_currency)

        if to_currency not in rates:
            valid_currencies = list(rates.keys())
            valid_currencies.append(from_currency)
            raise CurrencyNotFoundError(to_currency, valid_currencies)

        converted_amount = amount * rates[to_currency]

        return {
            "amount": amount,
            "from": from_currency,
            "to": to_currency,
            "rate": rates[to_currency],
            "converted_amount": converted_amount,
            "timestamp": datetime.now().isoformat(),
        }

    async def get_available_currencies(self) -> List[str]:
        """
        Get a list of all available currency codes.

        Returns:
            List of currency codes
        """
        rates = await self.get_exchange_rates("USD")
        currencies = list(rates.keys())
        currencies.append("USD")
        return sorted(currencies)

    async def _fetch_from_api(self, base_currency: str) -> Dict:
        """Fetch exchange rates from the api."""
        try:
            url = f"{self.api_url}/{base_currency}"
            headers = {}

            if self.api_key:
                headers["Authorization"] = f"Bearer {self.api_key}"

            logger.info(f"Fetching exchange rates for {base_currency} from api")

            async with httpx.AsyncClient() as client:
                response = await client.get(url=url, headers=headers, timeout=10)

            # response = requests.get(url, headers=headers, timeout=10)
            logger.info("Using Async HTTPx for requests")

            if response.status_code == 404:
                raise CurrencyNotFoundError(base_currency)

            if response.status_code != 200:
                error_message = f"api returned status code {response.status_code}"
                logger.error(error_message)
                raise ExchangeAPIError(error_message)

            data = response.json()
            return data

        except requests.RequestException as err:
            logger.error(f"error fetching exchange rates: {str(err)}")
            raise ExchangeAPIError(f"Error fetching exchange rates {str(err)}")

    async def _get_from_cache(self, key: str) -> Optional[Dict]:
        """Get data from cache."""
        if not self.redis_client:
            return None

        try:
            cached_data = self.redis_client.get(key)
            if cached_data:
                logger.info(f"Cache hit for {key}")
                return json.loads(cached_data)
        except (redis.RedisError, json.JSONDecodeError) as e:
            logger.warning(f"Error reading from cache: {str(e)}")

        return None

    async def _store_in_cache(self, key: str, data: Dict) -> None:
        """Store data in Redis Cache."""
        if not self.redis_client:
            return

        try:
            self.redis_client.setex(key, settings.REDIS_TTL, json.dumps(data))

            logger.info(f"Stored data in cache with key {key}")
        except redis.RedisError as err:
            logger.warning(f"Error storing in cache: {str(err)}")
