"""
Comprehensive logging system for spread creation operations.

This module provides structured logging for all spread creation activities,
including user actions, API calls, errors, and success events with full context
for troubleshooting and monitoring.
"""

import logging
import time
from typing import Dict, Optional, Any, Union
from datetime import datetime


class SpreadLogger:
    """
    Comprehensive logger for spread creation operations.
    
    Provides structured logging with consistent format and context
    for all spread creation activities.
    """
    
    def __init__(self, logger_name: str = 'spread_creation'):
        """
        Initialize the spread logger.
        
        Args:
            logger_name: Name for the logger instance
        """
        self.logger = logging.getLogger(logger_name)
    
    def log_creation_attempt(
        self,
        user_id: int,
        far_leg_ticker: str,
        near_leg_ticker: str,
        direction: Optional[str] = None,
        price: Optional[int] = None,
        amount: Optional[int] = None
    ) -> None:
        """
        Log a spread creation attempt with all available parameters.
        
        Args:
            user_id: Telegram user ID
            far_leg_ticker: Far leg ticker symbol
            near_leg_ticker: Near leg ticker symbol
            direction: Spread direction ('buy' or 'sell')
            price: Spread price
            amount: Trade amount
        """
        # Build message with available parameters
        message_parts = [
            f"Spread creation attempt by user {user_id}:",
            f"{far_leg_ticker}/{near_leg_ticker}"
        ]
        
        if direction:
            message_parts.append(f"direction={direction}")
        if price is not None:
            message_parts.append(f"price={price}")
        if amount is not None:
            message_parts.append(f"amount={amount}")
        
        message = " ".join(message_parts)
        
        # Prepare structured data for logging
        extra_data = {
            'user_id': user_id,
            'far_leg_ticker': far_leg_ticker,
            'near_leg_ticker': near_leg_ticker,
            'direction': direction,
            'price': price,
            'amount': amount,
            'operation': 'spread_creation_attempt',
            'timestamp': datetime.utcnow().isoformat()
        }
        
        self.logger.info(message, extra=extra_data)
    
    def log_creation_success(
        self,
        user_id: int,
        spread_id: int,
        far_leg_ticker: str,
        near_leg_ticker: str,
        direction: Optional[str] = None,
        price: Optional[int] = None,
        amount: Optional[int] = None
    ) -> None:
        """
        Log successful spread creation with all details.
        
        Args:
            user_id: Telegram user ID
            spread_id: Created spread ID
            far_leg_ticker: Far leg ticker symbol
            near_leg_ticker: Near leg ticker symbol
            direction: Spread direction
            price: Spread price
            amount: Trade amount
        """
        message_parts = [
            f"Spread created successfully - ID {spread_id} by user {user_id}:",
            f"{far_leg_ticker}/{near_leg_ticker}"
        ]
        
        if direction:
            message_parts.append(f"direction={direction}")
        if price is not None:
            message_parts.append(f"price={price}")
        if amount is not None:
            message_parts.append(f"amount={amount}")
        
        message = " ".join(message_parts)
        
        extra_data = {
            'user_id': user_id,
            'spread_id': spread_id,
            'far_leg_ticker': far_leg_ticker,
            'near_leg_ticker': near_leg_ticker,
            'direction': direction,
            'price': price,
            'amount': amount,
            'operation': 'spread_creation_success',
            'timestamp': datetime.utcnow().isoformat()
        }
        
        self.logger.info(message, extra=extra_data)
    
    def log_creation_error(
        self,
        user_id: int,
        error: Exception,
        far_leg_ticker: Optional[str] = None,
        near_leg_ticker: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Log spread creation error with full context for troubleshooting.
        
        Args:
            user_id: Telegram user ID
            error: Exception that occurred
            far_leg_ticker: Far leg ticker symbol (if available)
            near_leg_ticker: Near leg ticker symbol (if available)
            context: Additional context information
        """
        error_type = type(error).__name__
        error_message = str(error)
        
        message_parts = [
            f"Spread creation error for user {user_id}:",
            f"{error_type}: {error_message}"
        ]
        
        if far_leg_ticker and near_leg_ticker:
            message_parts.insert(1, f"{far_leg_ticker}/{near_leg_ticker}")
        
        message = " ".join(message_parts)
        
        extra_data = {
            'user_id': user_id,
            'error_type': error_type,
            'error_message': error_message,
            'far_leg_ticker': far_leg_ticker,
            'near_leg_ticker': near_leg_ticker,
            'context': context or {},
            'operation': 'spread_creation_error',
            'timestamp': datetime.utcnow().isoformat()
        }
        
        self.logger.error(message, extra=extra_data, exc_info=True)
    
    def log_user_action(
        self,
        user_id: int,
        action: str,
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Log user actions during spread creation process.
        
        Args:
            user_id: Telegram user ID
            action: Action performed by user
            details: Additional action details
        """
        message = f"User action: {action} by user {user_id}"
        
        extra_data = {
            'user_id': user_id,
            'action': action,
            'details': details or {},
            'operation': 'user_action',
            'timestamp': datetime.utcnow().isoformat()
        }
        
        self.logger.info(message, extra=extra_data)
    
    def log_api_call(
        self,
        user_id: int,
        endpoint: str,
        method: str,
        params: Optional[Dict[str, Any]] = None,
        response_status: Optional[int] = None,
        duration_ms: Optional[float] = None
    ) -> None:
        """
        Log API calls made during spread creation.
        
        Args:
            user_id: Telegram user ID
            endpoint: API endpoint called
            method: HTTP method
            params: Request parameters
            response_status: HTTP response status
            duration_ms: Call duration in milliseconds
        """
        message_parts = [f"API call: {method} {endpoint} for user {user_id}"]
        
        if response_status is not None:
            message_parts.append(f"status={response_status}")
        if duration_ms is not None:
            message_parts.append(f"duration={duration_ms:.1f}ms")
        
        message = " ".join(message_parts)
        
        extra_data = {
            'user_id': user_id,
            'endpoint': endpoint,
            'method': method,
            'params': params or {},
            'response_status': response_status,
            'duration_ms': duration_ms,
            'operation': 'api_call',
            'timestamp': datetime.utcnow().isoformat()
        }
        
        self.logger.debug(message, extra=extra_data)
    
    def log_validation_error(
        self,
        user_id: int,
        field: str,
        value: Any,
        error_message: str
    ) -> None:
        """
        Log validation errors with field and value context.
        
        Args:
            user_id: Telegram user ID
            field: Field that failed validation
            value: Value that was validated
            error_message: Validation error message
        """
        message = (
            f"Validation error for field {field} by user {user_id}: "
            f"value='{value}' - {error_message}"
        )
        
        extra_data = {
            'user_id': user_id,
            'field': field,
            'value': value,
            'error_message': error_message,
            'operation': 'validation_error',
            'timestamp': datetime.utcnow().isoformat()
        }
        
        self.logger.warning(message, extra=extra_data)
    
    def log_session_event(
        self,
        user_id: int,
        event: str,
        session_data: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Log session-related events (start, timeout, cleanup, etc.).
        
        Args:
            user_id: Telegram user ID
            event: Session event type
            session_data: Additional session information
        """
        message = f"Session event: {event} for user {user_id}"
        
        extra_data = {
            'user_id': user_id,
            'event': event,
            'session_data': session_data or {},
            'operation': 'session_event',
            'timestamp': datetime.utcnow().isoformat()
        }
        
        self.logger.info(message, extra=extra_data)


# Global logger instance
_spread_logger: Optional[SpreadLogger] = None


def get_spread_logger() -> SpreadLogger:
    """
    Get the global spread logger instance.
    
    Returns:
        SpreadLogger instance
    """
    global _spread_logger
    if _spread_logger is None:
        _spread_logger = SpreadLogger()
    return _spread_logger


# Convenience functions for common logging operations
def log_spread_creation_attempt(
    user_id: int,
    far_leg_ticker: str,
    near_leg_ticker: str,
    direction: Optional[str] = None,
    price: Optional[int] = None,
    amount: Optional[int] = None
) -> None:
    """
    Log a spread creation attempt.
    
    Args:
        user_id: Telegram user ID
        far_leg_ticker: Far leg ticker symbol
        near_leg_ticker: Near leg ticker symbol
        direction: Spread direction
        price: Spread price
        amount: Trade amount
    """
    logger = get_spread_logger()
    logger.log_creation_attempt(
        user_id=user_id,
        far_leg_ticker=far_leg_ticker,
        near_leg_ticker=near_leg_ticker,
        direction=direction,
        price=price,
        amount=amount
    )
    
    # Record in monitoring system
    try:
        from spread_monitoring import record_creation_attempt
        record_creation_attempt(user_id, far_leg_ticker, near_leg_ticker)
    except ImportError:
        pass  # Monitoring not available


def log_spread_creation_success(
    user_id: int,
    spread_id: int,
    far_leg_ticker: str,
    near_leg_ticker: str,
    direction: Optional[str] = None,
    price: Optional[int] = None,
    amount: Optional[int] = None
) -> None:
    """
    Log successful spread creation.
    
    Args:
        user_id: Telegram user ID
        spread_id: Created spread ID
        far_leg_ticker: Far leg ticker symbol
        near_leg_ticker: Near leg ticker symbol
        direction: Spread direction
        price: Spread price
        amount: Trade amount
    """
    logger = get_spread_logger()
    logger.log_creation_success(
        user_id=user_id,
        spread_id=spread_id,
        far_leg_ticker=far_leg_ticker,
        near_leg_ticker=near_leg_ticker,
        direction=direction,
        price=price,
        amount=amount
    )
    
    # Record in monitoring system
    try:
        from spread_monitoring import record_creation_success
        record_creation_success(user_id, spread_id, far_leg_ticker, near_leg_ticker)
    except ImportError:
        pass  # Monitoring not available


def log_spread_creation_error(
    user_id: int,
    error: Exception,
    far_leg_ticker: Optional[str] = None,
    near_leg_ticker: Optional[str] = None,
    context: Optional[Dict[str, Any]] = None
) -> None:
    """
    Log spread creation error.
    
    Args:
        user_id: Telegram user ID
        error: Exception that occurred
        far_leg_ticker: Far leg ticker symbol
        near_leg_ticker: Near leg ticker symbol
        context: Additional context
    """
    logger = get_spread_logger()
    logger.log_creation_error(
        user_id=user_id,
        error=error,
        far_leg_ticker=far_leg_ticker,
        near_leg_ticker=near_leg_ticker,
        context=context
    )
    
    # Record in monitoring system
    try:
        from spread_monitoring import record_creation_error
        record_creation_error(
            user_id=user_id,
            error_type=type(error).__name__,
            error_message=str(error),
            far_leg_ticker=far_leg_ticker,
            near_leg_ticker=near_leg_ticker
        )
    except ImportError:
        pass  # Monitoring not available


def log_user_action(
    user_id: int,
    action: str,
    details: Optional[Dict[str, Any]] = None
) -> None:
    """
    Log user action.
    
    Args:
        user_id: Telegram user ID
        action: Action performed
        details: Additional details
    """
    logger = get_spread_logger()
    logger.log_user_action(user_id=user_id, action=action, details=details)
    
    # Record in monitoring system
    try:
        from spread_monitoring import record_user_action
        record_user_action(user_id, action, details)
    except ImportError:
        pass  # Monitoring not available


def log_api_call(
    user_id: int,
    endpoint: str,
    method: str,
    params: Optional[Dict[str, Any]] = None,
    response_status: Optional[int] = None,
    duration_ms: Optional[float] = None
) -> None:
    """
    Log API call.
    
    Args:
        user_id: Telegram user ID
        endpoint: API endpoint
        method: HTTP method
        params: Request parameters
        response_status: Response status
        duration_ms: Duration in milliseconds
    """
    logger = get_spread_logger()
    logger.log_api_call(
        user_id=user_id,
        endpoint=endpoint,
        method=method,
        params=params,
        response_status=response_status,
        duration_ms=duration_ms
    )
    
    # Record in monitoring system
    try:
        from spread_monitoring import record_api_call
        record_api_call(user_id, endpoint, method, response_status, duration_ms)
    except ImportError:
        pass  # Monitoring not available


def log_validation_error(
    user_id: int,
    field: str,
    value: Any,
    error_message: str
) -> None:
    """
    Log validation error.
    
    Args:
        user_id: Telegram user ID
        field: Field that failed validation
        value: Invalid value
        error_message: Error message
    """
    logger = get_spread_logger()
    logger.log_validation_error(
        user_id=user_id,
        field=field,
        value=value,
        error_message=error_message
    )


def log_session_event(
    user_id: int,
    event: str,
    session_data: Optional[Dict[str, Any]] = None
) -> None:
    """
    Log session event.
    
    Args:
        user_id: Telegram user ID
        event: Event type
        session_data: Session data
    """
    logger = get_spread_logger()
    logger.log_session_event(
        user_id=user_id,
        event=event,
        session_data=session_data
    )


def configure_spread_logging(
    level: int = logging.INFO,
    log_format: Optional[str] = None,
    add_file_handler: bool = False,
    log_file_path: Optional[str] = None
) -> None:
    """
    Configure the spread creation logging system.
    
    Args:
        level: Logging level (default: INFO)
        log_format: Custom log format string
        add_file_handler: Whether to add file handler
        log_file_path: Path for log file (if file handler enabled)
    """
    logger = logging.getLogger('spread_creation')
    logger.setLevel(level)
    
    # Avoid duplicate handlers
    if logger.handlers:
        return
    
    # Default format with structured data
    if log_format is None:
        log_format = (
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s '
            '[user_id=%(user_id)s operation=%(operation)s]'
        )
    
    formatter = logging.Formatter(log_format)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # Optional file handler
    if add_file_handler and log_file_path:
        file_handler = logging.FileHandler(log_file_path)
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)


class LoggingContext:
    """
    Context manager for timing operations and automatic logging.
    
    Usage:
        with LoggingContext(user_id=123, operation='api_call') as ctx:
            # Perform operation
            ctx.add_data('endpoint', 'validate_ticker')
            result = await api_call()
            ctx.add_data('status', 200)
        # Automatically logs with timing information
    """
    
    def __init__(
        self,
        user_id: int,
        operation: str,
        log_level: int = logging.INFO
    ):
        """
        Initialize logging context.
        
        Args:
            user_id: Telegram user ID
            operation: Operation being performed
            log_level: Logging level for this context
        """
        self.user_id = user_id
        self.operation = operation
        self.log_level = log_level
        self.start_time = None
        self.data = {}
        self.logger = get_spread_logger()
    
    def __enter__(self):
        """Start timing and return context."""
        self.start_time = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Log operation completion with timing."""
        duration_ms = (time.time() - self.start_time) * 1000
        
        if exc_type is not None:
            # Log error
            self.logger.log_creation_error(
                user_id=self.user_id,
                error=exc_val,
                context={
                    'operation': self.operation,
                    'duration_ms': duration_ms,
                    **self.data
                }
            )
        else:
            # Log success
            message = f"Operation {self.operation} completed for user {self.user_id} in {duration_ms:.1f}ms"
            
            extra_data = {
                'user_id': self.user_id,
                'operation': self.operation,
                'duration_ms': duration_ms,
                'timestamp': datetime.utcnow().isoformat(),
                **self.data
            }
            
            self.logger.logger.log(self.log_level, message, extra=extra_data)
    
    def add_data(self, key: str, value: Any) -> None:
        """
        Add data to be included in the log.
        
        Args:
            key: Data key
            value: Data value
        """
        self.data[key] = value