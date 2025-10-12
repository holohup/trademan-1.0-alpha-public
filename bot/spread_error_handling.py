"""
Error handling and user feedback module for spread creation.

This module provides comprehensive error handling for all spread creation operations,
including API connection errors, validation failures, and user-friendly error messages.
"""

import logging
import asyncio
from typing import Dict, Optional, Any, Callable, Awaitable
from functools import wraps
from aiogram import types
try:
    from spread_validation import (
        ValidationError,
        PriceValidationError,
        AmountValidationError,
        TickerValidationError,
        get_validation_error_message,
    )
    from spread_api import APIError, TickerNotFoundError, PriceUnavailableError
except ImportError:
    # Handle import errors for testing
    class ValidationError(Exception):
        pass
    class PriceValidationError(ValidationError):
        pass
    class AmountValidationError(ValidationError):
        pass
    class TickerValidationError(ValidationError):
        pass
    class APIError(Exception):
        pass
    class TickerNotFoundError(APIError):
        pass
    class PriceUnavailableError(APIError):
        pass
    def get_validation_error_message(error):
        return f"❌ {str(error)}"
from spread_state import clear_state


# Configure logging for spread creation operations
logger = logging.getLogger('spread_creation')


class SessionTimeoutError(Exception):
    """Raised when a user session has timed out."""
    pass


class SpreadCreationError(Exception):
    """Base exception for spread creation specific errors."""
    pass


def handle_spread_errors(func: Callable) -> Callable:
    """
    Decorator to handle errors in spread creation functions.

    Provides comprehensive error handling with user-friendly messages
    and proper logging for all spread creation operations.

    Args:
        func: Async function to wrap with error handling

    Returns:
        Wrapped function with error handling
    """
    @wraps(func)
    async def wrapper(*args, **kwargs):
        # Extract message or callback_query from args
        message_or_callback = args[0] if args else None
        user_id = None
        
        if isinstance(message_or_callback, types.Message):
            user_id = message_or_callback.from_user.id
            send_message = message_or_callback.answer
        elif isinstance(message_or_callback, types.CallbackQuery):
            user_id = message_or_callback.from_user.id
            send_message = lambda text, **kwargs: message_or_callback.message.edit_text(text, **kwargs)
        else:
            # Fallback for other function signatures
            send_message = None

        try:
            return await func(*args, **kwargs)
            
        except ValidationError as e:
            # Handle validation errors with user-friendly messages
            error_message = get_validation_error_message(e)
            
            logger.warning(
                f"Validation error for user {user_id}: {str(e)}",
                extra={
                    'user_id': user_id,
                    'error_type': type(e).__name__,
                    'function': func.__name__
                }
            )
            
            if send_message:
                await send_message(error_message, parse_mode="Markdown")
            
        except TickerNotFoundError as e:
            # Handle ticker not found errors
            error_message = f"❌ **Ticker Not Found**\n\n{str(e)}\n\n💡 Please check the ticker symbol and try again with /addspread"
            
            logger.warning(
                f"Ticker not found for user {user_id}: {str(e)}",
                extra={
                    'user_id': user_id,
                    'error_type': 'TickerNotFoundError',
                    'function': func.__name__
                }
            )
            
            if send_message:
                await send_message(error_message, parse_mode="Markdown")
            
            # Clear session on ticker errors
            if user_id:
                clear_state(user_id)
                
        except PriceUnavailableError as e:
            # Handle price unavailable errors
            error_message = (
                f"❌ **Price Data Unavailable**\n\n"
                f"{str(e)}\n\n"
                f"💡 Market data may be temporarily unavailable. "
                f"Please try again in a few moments with /addspread"
            )
            
            logger.warning(
                f"Price unavailable for user {user_id}: {str(e)}",
                extra={
                    'user_id': user_id,
                    'error_type': 'PriceUnavailableError',
                    'function': func.__name__
                }
            )
            
            if send_message:
                await send_message(error_message, parse_mode="Markdown")
                
        except APIError as e:
            # Handle general API errors
            error_message = (
                f"❌ **Connection Error**\n\n"
                f"Unable to connect to trading system: {str(e)}\n\n"
                f"💡 Please check your connection and try again with /addspread"
            )
            
            logger.error(
                f"API error for user {user_id}: {str(e)}",
                extra={
                    'user_id': user_id,
                    'error_type': 'APIError',
                    'function': func.__name__
                }
            )
            
            if send_message:
                await send_message(error_message, parse_mode="Markdown")
                
        except SessionTimeoutError as e:
            # Handle session timeout errors
            error_message = (
                f"⏰ **Session Expired**\n\n"
                f"Your spread creation session has timed out.\n\n"
                f"💡 Please start over with /addspread"
            )
            
            logger.info(
                f"Session timeout for user {user_id}",
                extra={
                    'user_id': user_id,
                    'error_type': 'SessionTimeoutError',
                    'function': func.__name__
                }
            )
            
            if send_message:
                await send_message(error_message, parse_mode="Markdown")
            
            # Clear expired session
            if user_id:
                clear_state(user_id)
                
        except SpreadCreationError as e:
            # Handle spread creation specific errors
            error_message = (
                f"❌ **Spread Creation Failed**\n\n"
                f"{str(e)}\n\n"
                f"💡 Please try again with /addspread"
            )
            
            logger.error(
                f"Spread creation error for user {user_id}: {str(e)}",
                extra={
                    'user_id': user_id,
                    'error_type': 'SpreadCreationError',
                    'function': func.__name__
                }
            )
            
            if send_message:
                await send_message(error_message, parse_mode="Markdown")
                
        except asyncio.TimeoutError:
            # Handle timeout errors
            error_message = (
                f"⏰ **Request Timeout**\n\n"
                f"The request took too long to complete.\n\n"
                f"💡 Please try again with /addspread"
            )
            
            logger.error(
                f"Timeout error for user {user_id}",
                extra={
                    'user_id': user_id,
                    'error_type': 'TimeoutError',
                    'function': func.__name__
                }
            )
            
            if send_message:
                await send_message(error_message, parse_mode="Markdown")
                
        except Exception as e:
            # Handle unexpected errors
            error_message = (
                f"❌ **Unexpected Error**\n\n"
                f"An unexpected error occurred: {str(e)}\n\n"
                f"💡 Please try again with /addspread or contact support"
            )
            
            logger.error(
                f"Unexpected error for user {user_id}: {str(e)}",
                extra={
                    'user_id': user_id,
                    'error_type': type(e).__name__,
                    'function': func.__name__
                },
                exc_info=True
            )
            
            if send_message:
                await send_message(error_message, parse_mode="Markdown")
            
            # Clear session on unexpected errors
            if user_id:
                clear_state(user_id)
    
    return wrapper


async def handle_api_connection_error(
    error: Exception,
    user_message_func: Callable[[str], Awaitable[None]],
    operation_name: str = "operation"
) -> None:
    """
    Handle API connection errors with retry suggestions.

    Args:
        error: The exception that occurred
        user_message_func: Function to send message to user
        operation_name: Name of the operation that failed
    """
    if isinstance(error, APIError):
        if "connect" in str(error).lower():
            message = (
                f"❌ **Connection Failed**\n\n"
                f"Unable to connect to the trading system during {operation_name}.\n\n"
                f"💡 **Suggestions:**\n"
                f"• Check your internet connection\n"
                f"• Try again in a few moments\n"
                f"• Contact support if the problem persists"
            )
        elif "timeout" in str(error).lower():
            message = (
                f"⏰ **Request Timeout**\n\n"
                f"The {operation_name} request timed out.\n\n"
                f"💡 **Suggestions:**\n"
                f"• Try again with a stable connection\n"
                f"• Check if the trading system is available"
            )
        else:
            message = (
                f"❌ **API Error**\n\n"
                f"Error during {operation_name}: {str(error)}\n\n"
                f"💡 Please try again or contact support if the issue persists"
            )
    else:
        message = (
            f"❌ **Unexpected Error**\n\n"
            f"An unexpected error occurred during {operation_name}.\n\n"
            f"💡 Please try again with /addspread"
        )
    
    await user_message_func(message)


def get_user_friendly_error_message(
    error: Exception,
    context: Optional[Dict[str, Any]] = None
) -> str:
    """
    Generate user-friendly error messages based on error type and context.

    Args:
        error: The exception that occurred
        context: Additional context about the error

    Returns:
        User-friendly error message with suggestions
    """
    context = context or {}
    
    if isinstance(error, ValidationError):
        return get_validation_error_message(error)
    
    elif isinstance(error, TickerNotFoundError):
        ticker = context.get('ticker', 'ticker')
        return (
            f"❌ **Ticker Not Found**\n\n"
            f"The ticker '{ticker}' was not found in our database.\n\n"
            f"💡 **Suggestions:**\n"
            f"• Check the spelling of the ticker symbol\n"
            f"• Make sure the ticker is listed on MOEX\n"
            f"• Try using the full ticker name (e.g., GAZP instead of GAZ)"
        )
    
    elif isinstance(error, PriceUnavailableError):
        return (
            f"❌ **Price Data Unavailable**\n\n"
            f"Current market prices are not available for this instrument.\n\n"
            f"💡 **Possible reasons:**\n"
            f"• Market is closed\n"
            f"• Instrument is not actively traded\n"
            f"• Temporary data provider issue\n\n"
            f"Please try again later or during market hours."
        )
    
    elif isinstance(error, APIError):
        if "trading not available" in str(error).lower():
            return (
                f"❌ **API Trading Not Available**\n\n"
                f"This instrument does not support API trading.\n\n"
                f"💡 You can only create spreads with instruments that support automated trading."
            )
        else:
            return (
                f"❌ **Trading System Error**\n\n"
                f"{str(error)}\n\n"
                f"💡 Please try again or contact support if the issue persists."
            )
    
    elif isinstance(error, SessionTimeoutError):
        return (
            f"⏰ **Session Expired**\n\n"
            f"Your spread creation session has timed out for security reasons.\n\n"
            f"💡 Please start over with /addspread"
        )
    
    elif isinstance(error, SpreadCreationError):
        return (
            f"❌ **Spread Creation Failed**\n\n"
            f"{str(error)}\n\n"
            f"💡 Please check your parameters and try again."
        )
    
    else:
        return (
            f"❌ **Unexpected Error**\n\n"
            f"An unexpected error occurred: {str(error)}\n\n"
            f"💡 Please try again with /addspread or contact support."
        )


def log_spread_operation(
    operation: str,
    user_id: int,
    success: bool,
    details: Optional[Dict[str, Any]] = None,
    error: Optional[Exception] = None
) -> None:
    """
    Log spread creation operations for monitoring and debugging.

    Args:
        operation: Name of the operation (e.g., 'ticker_validation', 'spread_creation')
        user_id: Telegram user ID
        success: Whether the operation was successful
        details: Additional operation details
        error: Exception if operation failed
    """
    details = details or {}
    
    log_data = {
        'operation': operation,
        'user_id': user_id,
        'success': success,
        **details
    }
    
    if success:
        logger.info(
            f"Spread operation '{operation}' succeeded for user {user_id}",
            extra=log_data
        )
    else:
        error_info = {
            'error_type': type(error).__name__ if error else 'Unknown',
            'error_message': str(error) if error else 'Unknown error'
        }
        
        logger.error(
            f"Spread operation '{operation}' failed for user {user_id}: {error_info['error_message']}",
            extra={**log_data, **error_info},
            exc_info=error is not None
        )


async def validate_session_timeout(
    user_id: int,
    max_age_seconds: int = 1800
) -> None:
    """
    Validate that user session hasn't timed out.

    Args:
        user_id: Telegram user ID
        max_age_seconds: Maximum session age in seconds (default: 30 minutes)

    Raises:
        SessionTimeoutError: If session has timed out
    """
    try:
        from spread_state import get_state, _state_storage
        import time
        
        stored_data = _state_storage.get(user_id)
        if not stored_data:
            raise SessionTimeoutError("No active session found")
        
        session_age = time.time() - stored_data['timestamp']
        if session_age > max_age_seconds:
            clear_state(user_id)
            raise SessionTimeoutError(f"Session expired after {session_age:.0f} seconds")
    except ImportError:
        # For testing purposes
        raise SessionTimeoutError("No active session found")


def create_error_recovery_suggestions(error_type: str, context: Dict[str, Any]) -> str:
    """
    Create specific recovery suggestions based on error type and context.

    Args:
        error_type: Type of error that occurred
        context: Context information about the error

    Returns:
        Formatted recovery suggestions
    """
    suggestions = {
        'ticker_validation': [
            "Double-check the ticker symbol spelling",
            "Ensure the ticker is listed on MOEX",
            "Try using the standard ticker format (e.g., GAZP, SBER)"
        ],
        'price_fetch': [
            "Wait for market hours if market is closed",
            "Try again in a few moments",
            "Check if the instrument is actively traded"
        ],
        'api_connection': [
            "Check your internet connection",
            "Verify the trading system is available",
            "Try again in a few minutes"
        ],
        'validation': [
            "Review the input format requirements",
            "Check the minimum and maximum allowed values",
            "Ensure all required fields are filled"
        ],
        'session_timeout': [
            "Start a new session with /addspread",
            "Complete the process more quickly next time",
            "Contact support if you need extended session time"
        ]
    }
    
    error_suggestions = suggestions.get(error_type, [
        "Try the operation again",
        "Contact support if the problem persists",
        "Check the system status"
    ])
    
    formatted_suggestions = "\n".join([f"• {suggestion}" for suggestion in error_suggestions])
    return f"💡 **Suggestions:**\n{formatted_suggestions}"