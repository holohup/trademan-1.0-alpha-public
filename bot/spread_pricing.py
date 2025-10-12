"""
Spread pricing calculation module.

This module provides functions for calculating market-neutral spread prices,
ratios, and generating explanations for different asset type combinations.
"""

from decimal import Decimal
from typing import Dict, Any, List

from settings import RETRY_SETTINGS, TCS_RO_TOKEN
from tinkoff.invest.retrying.aio.client import AsyncRetryingClient
from tinkoff.invest.utils import quotation_to_decimal


class SpreadPriceCalculationError(Exception):
    """Exception raised when spread price calculation fails."""
    pass


def calculate_ratio(
    far_leg_data: Dict[str, Any],
    near_leg_data: Dict[str, Any]
) -> int:
    """
    Calculate the market-neutral ratio between far and near legs.

    For stock-future spreads: Uses the future's basic_asset_size
    For future-future spreads: Ratio based on basic_asset_size comparison
    For stock-stock spreads: Always 1:1

    Args:
        far_leg_data: Dictionary containing far leg asset information
        near_leg_data: Dictionary containing near leg asset information

    Returns:
        Integer ratio for market-neutral position

    Raises:
        SpreadPriceCalculationError: If required data is missing
    """
    far_asset_type = far_leg_data.get('asset_type')
    near_asset_type = near_leg_data.get('asset_type')

    # Stock-stock spread: always 1:1
    if far_asset_type == 'S' and near_asset_type == 'S':
        return 1

    # Future involved: use basic_asset_size
    if far_asset_type == 'F':
        return _calculate_future_ratio(far_leg_data, near_leg_data)

    # Near leg is future, far leg is stock (unusual but possible)
    if near_asset_type == 'F':
        return _calculate_near_future_ratio(near_leg_data)

    # Default case: 1:1 ratio
    return 1


def _calculate_future_ratio(
    far_leg_data: Dict[str, Any],
    near_leg_data: Dict[str, Any]
) -> int:
    """Calculate ratio when far leg is a future."""
    far_basic_size = far_leg_data.get('basic_asset_size')
    if far_basic_size is None:
        ticker = far_leg_data.get('ticker', 'unknown')
        raise SpreadPriceCalculationError(
            f"Missing basic_asset_size for future {ticker}"
        )

    near_asset_type = near_leg_data.get('asset_type')
    if near_asset_type == 'S':
        # Stock-future spread: 1 future = basic_asset_size stocks
        return far_basic_size

    if near_asset_type == 'F':
        # Future-future spread: ratio of basic asset sizes
        near_basic_size = near_leg_data.get('basic_asset_size')
        if near_basic_size is None:
            ticker = near_leg_data.get('ticker', 'unknown')
            raise SpreadPriceCalculationError(
                f"Missing basic_asset_size for future {ticker}"
            )
        return far_basic_size // near_basic_size

    return 1


def _calculate_near_future_ratio(near_leg_data: Dict[str, Any]) -> int:
    """Calculate ratio when near leg is a future."""
    near_basic_size = near_leg_data.get('basic_asset_size')
    if near_basic_size is None:
        ticker = near_leg_data.get('ticker', 'unknown')
        raise SpreadPriceCalculationError(
            f"Missing basic_asset_size for future {ticker}"
        )
    return 1  # 1 stock per unit, ratio handled in price calculation


def calculate_spread_price(
    far_leg_data: Dict[str, Any],
    near_leg_data: Dict[str, Any],
    price_data: Dict[str, Dict[str, Any]],
    direction: str
) -> Dict[str, Any]:
    """
    Calculate market-neutral spread price based on current market data.

    For buying spread: sell far leg at bid, buy near leg at ask
    For selling spread: buy far leg at ask, sell near leg at bid

    Args:
        far_leg_data: Dictionary containing far leg asset information
        near_leg_data: Dictionary containing near leg asset information
        price_data: Dictionary mapping FIGI to price information
        direction: 'buy' or 'sell' indicating spread direction

    Returns:
        Dictionary containing:
        - spread_price: Calculated spread price
        - ratio: Market-neutral ratio
        - far_leg_price: Price used for far leg
        - near_leg_price: Price used for near leg

    Raises:
        SpreadPriceCalculationError: If calculation fails or data is missing
    """
    if direction not in ('buy', 'sell'):
        raise SpreadPriceCalculationError(f"Invalid direction: {direction}")

    # Validate and get FIGIs
    far_figi, near_figi = _validate_figis(far_leg_data, near_leg_data)

    # Check price data availability
    _validate_price_data_availability(
        far_figi, near_figi, price_data, far_leg_data, near_leg_data
    )

    # Calculate ratio and prices
    ratio = calculate_ratio(far_leg_data, near_leg_data)
    far_price, near_price = _get_direction_prices(
        price_data[far_figi], price_data[near_figi], direction
    )

    # Calculate spread price: far_leg_price * ratio - near_leg_price
    spread_price = far_price * ratio - near_price

    return {
        'spread_price': spread_price,
        'ratio': ratio,
        'far_leg_price': far_price,
        'near_leg_price': near_price
    }


def _validate_figis(
    far_leg_data: Dict[str, Any],
    near_leg_data: Dict[str, Any]
) -> tuple:
    """Validate and return FIGIs from leg data."""
    far_figi = far_leg_data.get('figi')
    near_figi = near_leg_data.get('figi')

    if not far_figi or not near_figi:
        raise SpreadPriceCalculationError("Missing FIGI data for legs")

    return far_figi, near_figi


def _validate_price_data_availability(
    far_figi: str,
    near_figi: str,
    price_data: Dict[str, Dict[str, Any]],
    far_leg_data: Dict[str, Any],
    near_leg_data: Dict[str, Any]
) -> None:
    """Validate that price data is available for both legs."""
    missing_figis = []
    if far_figi not in price_data:
        missing_figis.append(f"{far_leg_data.get('ticker', far_figi)}")
    if near_figi not in price_data:
        missing_figis.append(f"{near_leg_data.get('ticker', near_figi)}")

    if missing_figis:
        raise SpreadPriceCalculationError(
            f"Price data unavailable for: {', '.join(missing_figis)}"
        )


def _get_direction_prices(
    far_price_info: Dict[str, Any],
    near_price_info: Dict[str, Any],
    direction: str
) -> tuple:
    """Get prices based on spread direction."""
    if direction == 'buy':
        # Buy spread: sell far leg (use bid), buy near leg (use ask)
        far_price = _get_price_for_selling(far_price_info)
        near_price = _get_price_for_buying(near_price_info)
    else:  # sell
        # Sell spread: buy far leg (use ask), sell near leg (use bid)
        far_price = _get_price_for_buying(far_price_info)
        near_price = _get_price_for_selling(near_price_info)

    return far_price, near_price


def _get_price_for_buying(price_info: Dict[str, Any]) -> Decimal:
    """Get the price for buying an asset (ask price or last price fallback)."""
    return price_info.get('ask_price') or price_info['last_price']


def _get_price_for_selling(price_info: Dict[str, Any]) -> Decimal:
    """Get the price for selling an asset (bid price or last price fallback)."""
    return price_info.get('bid_price') or price_info['last_price']


def get_market_neutral_explanation(
    far_leg_data: Dict[str, Any],
    near_leg_data: Dict[str, Any],
    direction: str,
    ratio: int
) -> str:
    """
    Generate human-readable explanation of market-neutral spread position.

    Args:
        far_leg_data: Dictionary containing far leg asset information
        near_leg_data: Dictionary containing near leg asset information
        direction: 'buy' or 'sell' indicating spread direction
        ratio: Market-neutral ratio between legs

    Returns:
        Formatted explanation string in Russian
    """
    far_ticker = far_leg_data.get('ticker', 'unknown')
    near_ticker = near_leg_data.get('ticker', 'unknown')
    far_asset_type = far_leg_data.get('asset_type', 'unknown')
    near_asset_type = near_leg_data.get('asset_type', 'unknown')

    # Asset type descriptions
    asset_type_names = {
        'S': 'акции',
        'F': 'фьючерс',
        'B': 'облигации'
    }

    far_type_name = asset_type_names.get(far_asset_type, 'инструмент')
    near_type_name = asset_type_names.get(near_asset_type, 'инструмент')

    if direction == 'buy':
        # Buy spread: sell far leg, buy near leg
        direction_text = "Покупка спреда"
        far_action = "Продать"
        near_action = "Купить"
    else:
        # Sell spread: buy far leg, sell near leg
        direction_text = "Продажа спреда"
        far_action = "Купить"
        near_action = "Продать"

    return (
        f"{direction_text} (market-neutral позиция):\n"
        f"• {far_action} 1 {far_ticker} ({far_type_name})\n"
        f"• {near_action} {ratio} {near_ticker} ({near_type_name})\n"
        f"Соотношение: 1:{ratio}"
    )


async def get_spread_prices_with_market_data(
    far_leg_data: Dict[str, Any],
    near_leg_data: Dict[str, Any]
) -> Dict[str, Dict[str, Any]]:
    """
    Fetch current market data and calculate spread prices for both directions.

    This function integrates with the Tinkoff API to fetch current prices
    and order book data, then calculates spread prices for both buy and sell
    directions using market-neutral ratios.

    Args:
        far_leg_data: Dictionary containing far leg asset information
        near_leg_data: Dictionary containing near leg asset information

    Returns:
        Dictionary containing 'buy' and 'sell' spread calculations

    Raises:
        SpreadPriceCalculationError: If price data is unavailable or API fails
    """
    try:
        # Fetch current market prices
        price_data = await _fetch_market_prices_with_order_book(
            [far_leg_data['figi'], near_leg_data['figi']]
        )

        # Calculate prices for both directions
        buy_result = calculate_spread_price(
            far_leg_data, near_leg_data, price_data, 'buy'
        )
        sell_result = calculate_spread_price(
            far_leg_data, near_leg_data, price_data, 'sell'
        )

        return {
            'buy': buy_result,
            'sell': sell_result
        }

    except Exception as e:
        if isinstance(e, SpreadPriceCalculationError):
            raise
        raise SpreadPriceCalculationError(
            f"Unable to fetch prices: {str(e)}"
        )


async def _fetch_market_prices_with_order_book(
    figis: List[str]
) -> Dict[str, Dict[str, Any]]:
    """
    Fetch current market prices and order book data from Tinkoff API.

    Args:
        figis: List of FIGI identifiers to fetch prices for

    Returns:
        Dictionary mapping FIGI to price data containing last_price,
        and optionally bid_price and ask_price if available

    Raises:
        SpreadPriceCalculationError: If no price data is available
    """
    async with AsyncRetryingClient(TCS_RO_TOKEN, RETRY_SETTINGS) as client:
        # Get last prices
        response = await client.market_data.get_last_prices(figi=figis)

        if not response.last_prices:
            raise SpreadPriceCalculationError("No price data available")

        # Build price data dictionary with last prices
        price_data: Dict[str, Dict[str, Any]] = {}
        for price_item in response.last_prices:
            figi = price_item.figi
            price_data[figi] = {
                'figi': figi,
                'last_price': quotation_to_decimal(price_item.price)
            }

        # Try to fetch order book data for bid/ask prices
        await _add_order_book_data(client, figis, price_data)

        return price_data


async def _add_order_book_data(
    client,
    figis: List[str],
    price_data: Dict[str, Dict[str, Any]]
) -> None:
    """
    Add order book data (bid/ask prices) to price data.

    This function attempts to fetch order book data for each FIGI.
    If order book data is unavailable for any instrument, it continues
    without raising an error (graceful degradation to last prices).
    """
    for figi in figis:
        if figi in price_data:
            await _fetch_single_order_book(client, figi, price_data)


async def _fetch_single_order_book(
    client,
    figi: str,
    price_data: Dict[str, Dict[str, Any]]
) -> None:
    """Fetch order book data for a single FIGI."""
    try:
        order_book = await client.market_data.get_order_book(
            figi=figi, depth=1
        )

        # Add bid price if available
        if order_book.bids:
            price_data[figi]['bid_price'] = quotation_to_decimal(
                order_book.bids[0].price
            )

        # Add ask price if available
        if order_book.asks:
            price_data[figi]['ask_price'] = quotation_to_decimal(
                order_book.asks[0].price
            )

    except Exception:
        # If order book fails, continue without bid/ask data
        # The calculation will fall back to using last prices
        pass