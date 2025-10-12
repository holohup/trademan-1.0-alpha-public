"""
API integration module for spread creation.

This module provides functions for ticker validation and price fetching
using the existing Tinkoff integration and Django API endpoints.
"""

import aiohttp
from typing import Dict, List, Optional
from settings import ENDPOINT_HOST, ENDPOINTS, RETRY_SETTINGS, TCS_RO_TOKEN
from tinkoff.invest.retrying.aio.client import AsyncRetryingClient
from tinkoff.invest.utils import quotation_to_decimal


class APIError(Exception):
    """Base exception for API-related errors."""
    pass


class TickerNotFoundError(APIError):
    """Raised when a ticker is not found in the database."""
    pass


class PriceUnavailableError(APIError):
    """Raised when price data is unavailable."""
    pass


async def validate_ticker(ticker: str) -> Dict:
    """
    Validate ticker existence and API trading availability.

    Args:
        ticker: The ticker symbol to validate

    Returns:
        Dict containing ticker information including figi, lot size, etc.

    Raises:
        TickerNotFoundError: If ticker doesn't exist
        APIError: If API trading is not available or connection fails
    """
    url = ENDPOINT_HOST + ENDPOINTS['ticker'] + ticker + '/'

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 404:
                    raise TickerNotFoundError(f"Ticker {ticker} not found")
                if response.status != 200:
                    raise APIError(f"Server error: {response.status}")

                data = await response.json()

                # Check if API trading is available
                if not data.get('api_trading_available', False):
                    raise APIError(f"API trading not available for {ticker}")

                return data

    except aiohttp.ClientError as e:
        raise APIError(f"Unable to connect to trading system: {str(e)}")


async def get_current_prices(
        figis: List[str],
        include_order_book: bool = False) -> Dict[str, Dict]:
    """
    Fetch current market prices for given FIGIs.

    Args:
        figis: List of FIGI identifiers
        include_order_book: Whether to include bid/ask prices from order book

    Returns:
        Dict mapping FIGI to price data containing:
        - last_price: Latest trade price
        - bid_price: Best bid price (if include_order_book=True)
        - ask_price: Best ask price (if include_order_book=True)

    Raises:
        PriceUnavailableError: If no price data is available
        APIError: If connection fails
    """
    try:
        async with AsyncRetryingClient(TCS_RO_TOKEN, RETRY_SETTINGS) as client:
            # Get last prices
            response = await client.market_data.get_last_prices(figi=figis)

            if not response.last_prices:
                raise PriceUnavailableError("No price data available")

            # Build price data dictionary
            price_data = {}
            for price_item in response.last_prices:
                figi = price_item.figi
                price_data[figi] = {
                    'figi': figi,
                    'last_price': quotation_to_decimal(price_item.price)
                }

            # Optionally fetch order book data for bid/ask prices
            if include_order_book:
                await _add_order_book_data(client, figis, price_data)

            return price_data

    except Exception as e:
        if isinstance(e, (PriceUnavailableError, APIError)):
            raise
        raise APIError(f"Unable to fetch prices: {str(e)}")


async def _add_order_book_data(client, figis: List[str], price_data: Dict):
    """Helper function to add order book data to price data."""
    for figi in figis:
        if figi in price_data:
            try:
                order_book = await client.market_data.get_order_book(
                    figi=figi, depth=1
                )

                if order_book.bids:
                    price_data[figi]['bid_price'] = quotation_to_decimal(
                        order_book.bids[0].price
                    )

                if order_book.asks:
                    price_data[figi]['ask_price'] = quotation_to_decimal(
                        order_book.asks[0].price
                    )

            except Exception:
                # If order book fails, continue without bid/ask data
                pass


async def create_spread(spread_data: Dict) -> int:
    """
    Create a new spread in the database.

    Args:
        spread_data: Dictionary containing spread parameters:
        - far_leg_figi: FIGI of the far leg
        - near_leg_figi: FIGI of the near leg
        - sell: Boolean indicating sell direction
        - price: Spread price
        - amount: Amount to trade
        - editable_ratio: Optional ratio override

    Returns:
        The ID of the created spread

    Raises:
        APIError: If creation fails or connection issues occur
    """
    url = ENDPOINT_HOST + ENDPOINTS['spreads']

    # Prepare payload for Django API
    payload = {
        'far_leg_figi': spread_data['far_leg_figi'],
        'near_leg_figi': spread_data['near_leg_figi'],
        'sell': spread_data['sell'],
        'price': spread_data['price'],
        'amount': spread_data['amount']
    }

    # Add optional ratio if provided
    if 'editable_ratio' in spread_data and spread_data['editable_ratio']:
        payload['editable_ratio'] = spread_data['editable_ratio']

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload) as response:
                if response.status == 201:
                    data = await response.json()
                    return data['id']
                error_text = await response.text()
                raise APIError(f"Error creating spread: {error_text}")

    except aiohttp.ClientError as e:
        raise APIError(f"Unable to connect to trading system: {str(e)}")


async def check_duplicate_spread(
        far_leg_figi: str,
        near_leg_figi: str) -> Optional[int]:
    """
    Check if a spread with the same legs already exists.

    Args:
        far_leg_figi: FIGI of the far leg
        near_leg_figi: FIGI of the near leg

    Returns:
        The ID of the existing spread if found, None otherwise

    Raises:
        APIError: If connection fails or server error occurs
    """
    url = ENDPOINT_HOST + ENDPOINTS['spreads']

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status != 200:
                    raise APIError(f"Server error: {response.status}")

                spreads = await response.json()

                # Check for duplicate spread with same legs
                for spread in spreads:
                    far_match = spread['far_leg']['figi'] == far_leg_figi
                    near_match = spread['near_leg']['figi'] == near_leg_figi
                    if far_match and near_match:
                        return spread['id']

                return None

    except aiohttp.ClientError as e:
        raise APIError(f"Unable to connect to trading system: {str(e)}")