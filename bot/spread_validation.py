"""
Input validation module for spread creation.

This module provides comprehensive validation functions for all user inputs
during the spread creation process, including price, amount, and ticker validation.
"""

import re
from decimal import Decimal
from typing import Dict, List, Optional, Tuple, Any


class ValidationError(Exception):
    """Base exception for validation errors."""
    pass


class PriceValidationError(ValidationError):
    """Raised when price validation fails."""
    pass


class AmountValidationError(ValidationError):
    """Raised when amount validation fails."""
    pass


class TickerValidationError(ValidationError):
    """Raised when ticker validation fails."""
    pass


def validate_price_input(
    price_input: str,
    min_price: Optional[int] = None,
    max_price: Optional[int] = None,
    min_price_increment: Optional[Decimal] = None
) -> int:
    """
    Validate price input from user.

    Args:
        price_input: Raw price input string from user
        min_price: Minimum allowed price (optional)
        max_price: Maximum allowed price (optional)
        min_price_increment: Minimum price increment for validation (optional)

    Returns:
        Validated price as integer

    Raises:
        PriceValidationError: If validation fails
    """
    # Check for empty or whitespace-only input
    if not price_input or not price_input.strip():
        raise PriceValidationError("Price cannot be empty")

    # Remove whitespace
    price_str = price_input.strip()

    # Check if input is a valid integer
    try:
        price = int(price_str)
    except ValueError:
        raise PriceValidationError("Price must be a valid integer")

    # Check if price is positive
    if price <= 0:
        raise PriceValidationError("Price must be a positive integer")

    # Check minimum price constraint
    if min_price is not None and price < min_price:
        raise PriceValidationError(
            f"Price must be at least {min_price}"
        )

    # Check maximum price constraint
    if max_price is not None and price > max_price:
        raise PriceValidationError(
            f"Price cannot exceed {max_price}"
        )

    # Check price increment constraint
    if min_price_increment is not None:
        increment_int = int(min_price_increment * 100)  # Convert to kopecks
        if increment_int > 0 and (price % increment_int) != 0:
            raise PriceValidationError(
                f"Price must be a multiple of {min_price_increment}"
            )

    return price


def validate_amount_input(
    amount_input: str,
    min_lot: Optional[int] = None,
    max_amount: Optional[int] = None
) -> int:
    """
    Validate amount input from user.

    Args:
        amount_input: Raw amount input string from user
        min_lot: Minimum lot size requirement (optional)
        max_amount: Maximum allowed amount (optional)

    Returns:
        Validated amount as integer

    Raises:
        AmountValidationError: If validation fails
    """
    # Check for empty or whitespace-only input
    if not amount_input or not amount_input.strip():
        raise AmountValidationError("Amount cannot be empty")

    # Remove whitespace
    amount_str = amount_input.strip()

    # Check if input is a valid integer
    try:
        amount = int(amount_str)
    except ValueError:
        raise AmountValidationError("Amount must be a valid integer")

    # Check if amount is positive
    if amount <= 0:
        raise AmountValidationError("Amount must be a positive integer")

    # Check minimum lot requirement
    if min_lot is not None and amount < min_lot:
        raise AmountValidationError(
            f"Amount must be at least {min_lot} (minimum lot requirement)"
        )

    # Check maximum amount constraint
    if max_amount is not None and amount > max_amount:
        raise AmountValidationError(
            f"Amount cannot exceed {max_amount}"
        )

    return amount


def validate_ticker_format(ticker: str) -> str:
    """
    Validate ticker format and normalize it.

    Args:
        ticker: Raw ticker string from user

    Returns:
        Normalized ticker string (uppercase, trimmed)

    Raises:
        TickerValidationError: If ticker format is invalid
    """
    # Check for empty or None input
    if not ticker:
        raise TickerValidationError("Ticker cannot be empty")

    # Remove whitespace and convert to uppercase
    normalized_ticker = ticker.strip().upper()

    # Check if ticker is empty after normalization
    if not normalized_ticker:
        raise TickerValidationError("Ticker cannot be empty")

    # Check ticker format - should contain only letters and numbers
    if not re.match(r'^[A-Z0-9]+$', normalized_ticker):
        raise TickerValidationError(
            "Ticker must contain only letters and numbers"
        )

    # Check ticker length constraints
    if len(normalized_ticker) < 2:
        raise TickerValidationError(
            "Ticker must be at least 2 characters long"
        )

    if len(normalized_ticker) > 12:
        raise TickerValidationError(
            "Ticker cannot be longer than 12 characters"
        )

    return normalized_ticker


def validate_ticker_pair(far_leg: str, near_leg: str) -> Tuple[str, str]:
    """
    Validate a pair of tickers for spread creation.

    Args:
        far_leg: Far leg ticker
        near_leg: Near leg ticker

    Returns:
        Tuple of (normalized_far_leg, normalized_near_leg)

    Raises:
        TickerValidationError: If validation fails
    """
    # Validate individual tickers
    normalized_far = validate_ticker_format(far_leg)
    normalized_near = validate_ticker_format(near_leg)

    # Check that tickers are different
    if normalized_far == normalized_near:
        raise TickerValidationError(
            "Far leg and near leg tickers must be different"
        )

    return normalized_far, normalized_near


def validate_spread_direction(direction: str) -> str:
    """
    Validate spread direction input.

    Args:
        direction: Direction string ('buy' or 'sell')

    Returns:
        Validated direction string

    Raises:
        ValidationError: If direction is invalid
    """
    if not direction:
        raise ValidationError("Direction cannot be empty")

    normalized_direction = direction.strip().lower()

    if normalized_direction not in ['buy', 'sell']:
        raise ValidationError("Direction must be 'buy' or 'sell'")

    return normalized_direction


def validate_lot_requirements(
    amount: int,
    far_leg_data: Dict[str, Any],
    near_leg_data: Dict[str, Any]
) -> bool:
    """
    Validate that amount meets lot requirements for both legs.

    Args:
        amount: Trade amount
        far_leg_data: Far leg ticker data containing lot size
        near_leg_data: Near leg ticker data containing lot size

    Returns:
        True if amount meets requirements

    Raises:
        AmountValidationError: If lot requirements are not met
    """
    far_lot = far_leg_data.get('lot', 1)
    near_lot = near_leg_data.get('lot', 1)

    # Check far leg lot requirement
    if amount % far_lot != 0:
        raise AmountValidationError(
            f"Amount must be a multiple of {far_lot} "
            f"(lot size for {far_leg_data.get('ticker', 'far leg')})"
        )

    # Check near leg lot requirement
    if amount % near_lot != 0:
        raise AmountValidationError(
            f"Amount must be a multiple of {near_lot} "
            f"(lot size for {near_leg_data.get('ticker', 'near leg')})"
        )

    return True


def validate_price_reasonableness(
    price: int,
    market_price: Optional[int],
    tolerance_percent: float = 50.0
) -> bool:
    """
    Validate that custom price is reasonable compared to market price.

    Args:
        price: Custom price to validate
        market_price: Current market price (optional)
        tolerance_percent: Maximum deviation percentage from market price

    Returns:
        True if price is reasonable

    Raises:
        PriceValidationError: If price is unreasonable
    """
    if market_price is None:
        # Cannot validate without market price
        return True

    if market_price <= 0:
        # Invalid market price
        return True

    # Calculate percentage deviation
    deviation = abs(price - market_price) / market_price * 100

    if deviation > tolerance_percent:
        raise PriceValidationError(
            f"Price deviates {deviation:.1f}% from market price "
            f"({market_price}). Maximum allowed deviation is "
            f"{tolerance_percent}%"
        )

    return True


def get_validation_error_message(error: ValidationError) -> str:
    """
    Get user-friendly error message for validation errors.

    Args:
        error: Validation error instance

    Returns:
        User-friendly error message with suggestions
    """
    error_msg = str(error)

    # Add helpful suggestions based on error type
    if isinstance(error, PriceValidationError):
        if "empty" in error_msg.lower():
            return f"❌ {error_msg}\n\n💡 Please enter a price as a whole number (e.g., 150)"
        elif "integer" in error_msg.lower():
            return f"❌ {error_msg}\n\n💡 Please enter only numbers without decimals or symbols"
        elif "positive" in error_msg.lower():
            return f"❌ {error_msg}\n\n💡 Price must be greater than 0"
        elif "multiple" in error_msg.lower():
            return f"❌ {error_msg}\n\n💡 Check the minimum price increment for this instrument"
        else:
            return f"❌ {error_msg}"

    elif isinstance(error, AmountValidationError):
        if "empty" in error_msg.lower():
            return f"❌ {error_msg}\n\n💡 Please enter an amount as a whole number (e.g., 5)"
        elif "integer" in error_msg.lower():
            return f"❌ {error_msg}\n\n💡 Please enter only numbers without decimals"
        elif "positive" in error_msg.lower():
            return f"❌ {error_msg}\n\n💡 Amount must be greater than 0"
        elif "lot" in error_msg.lower():
            return f"❌ {error_msg}\n\n💡 Check the lot size requirements shown in the menu"
        else:
            return f"❌ {error_msg}"

    elif isinstance(error, TickerValidationError):
        if "empty" in error_msg.lower():
            return f"❌ {error_msg}\n\n💡 Please provide a valid ticker symbol (e.g., GAZP, GZZ4)"
        elif "letters and numbers" in error_msg.lower():
            return f"❌ {error_msg}\n\n💡 Use only letters and numbers (no spaces or symbols)"
        elif "different" in error_msg.lower():
            return f"❌ {error_msg}\n\n💡 Choose two different instruments for the spread"
        elif "characters" in error_msg.lower():
            return f"❌ {error_msg}\n\n💡 Ticker should be 2-12 characters (e.g., GAZP, GZZ4)"
        else:
            return f"❌ {error_msg}"

    else:
        return f"❌ {error_msg}"


def validate_session_completeness(state: Dict[str, Any]) -> List[str]:
    """
    Validate that all required fields are present for spread creation.

    Args:
        state: Spread creation state dictionary

    Returns:
        List of missing or invalid fields (empty if all valid)
    """
    missing_fields = []

    # Check required ticker data
    if not state.get('far_leg_data'):
        missing_fields.append('far_leg_data')
    if not state.get('near_leg_data'):
        missing_fields.append('near_leg_data')

    # Check direction
    if not state.get('direction'):
        missing_fields.append('direction')

    # Check price
    if state.get('custom_price') is None:
        missing_fields.append('custom_price')

    # Check amount
    if not state.get('amount'):
        missing_fields.append('amount')

    return missing_fields