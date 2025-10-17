"""
Tests for spread creation logging functionality.

This module tests the comprehensive logging system for spread creation operations,
including success logging, error logging, and log message formats.
"""

import pytest
import logging
from unittest.mock import Mock, patch, MagicMock
from spread_logging import (
    SpreadLogger,
    log_spread_creation_attempt,
    log_spread_creation_success,
    log_spread_creation_error,
    log_user_action,
    log_api_call,
    log_validation_error,
    log_session_event,
    configure_spread_logging,
)


class TestSpreadLogger:
    """Test the SpreadLogger class."""

    def test_init_creates_logger_with_correct_name(self):
        """Test that SpreadLogger initializes with correct logger name."""
        spread_logger = SpreadLogger()
        assert spread_logger.logger.name == 'spread_creation'

    def test_init_with_custom_name(self):
        """Test that SpreadLogger can be initialized with custom name."""
        spread_logger = SpreadLogger(logger_name='custom_spread')
        assert spread_logger.logger.name == 'custom_spread'

    def test_log_creation_attempt_with_all_params(self):
        """Test logging spread creation attempt with all parameters."""
        spread_logger = SpreadLogger()
        
        with patch.object(spread_logger.logger, 'info') as mock_info:
            spread_logger.log_creation_attempt(
                user_id=12345,
                far_leg_ticker='GAZP',
                near_leg_ticker='GZZ4',
                direction='buy',
                price=150,
                amount=10
            )
            
            mock_info.assert_called_once()
            call_args = mock_info.call_args
            
            # Check log message
            assert 'Spread creation attempt' in call_args[0][0]
            
            # Check extra data
            extra = call_args[1]['extra']
            assert extra['user_id'] == 12345
            assert extra['far_leg_ticker'] == 'GAZP'
            assert extra['near_leg_ticker'] == 'GZZ4'
            assert extra['direction'] == 'buy'
            assert extra['price'] == 150
            assert extra['amount'] == 10
            assert extra['operation'] == 'spread_creation_attempt'

    def test_log_creation_attempt_with_minimal_params(self):
        """Test logging spread creation attempt with minimal parameters."""
        spread_logger = SpreadLogger()
        
        with patch.object(spread_logger.logger, 'info') as mock_info:
            spread_logger.log_creation_attempt(
                user_id=12345,
                far_leg_ticker='GAZP',
                near_leg_ticker='GZZ4'
            )
            
            mock_info.assert_called_once()
            call_args = mock_info.call_args
            
            extra = call_args[1]['extra']
            assert extra['user_id'] == 12345
            assert extra['far_leg_ticker'] == 'GAZP'
            assert extra['near_leg_ticker'] == 'GZZ4'
            assert extra.get('direction') is None
            assert extra.get('price') is None
            assert extra.get('amount') is None

    def test_log_creation_success(self):
        """Test logging successful spread creation."""
        spread_logger = SpreadLogger()
        
        with patch.object(spread_logger.logger, 'info') as mock_info:
            spread_logger.log_creation_success(
                user_id=12345,
                spread_id=67890,
                far_leg_ticker='GAZP',
                near_leg_ticker='GZZ4',
                direction='sell',
                price=200,
                amount=5
            )
            
            mock_info.assert_called_once()
            call_args = mock_info.call_args
            
            # Check log message
            assert 'Spread created successfully' in call_args[0][0]
            
            # Check extra data
            extra = call_args[1]['extra']
            assert extra['user_id'] == 12345
            assert extra['spread_id'] == 67890
            assert extra['far_leg_ticker'] == 'GAZP'
            assert extra['near_leg_ticker'] == 'GZZ4'
            assert extra['direction'] == 'sell'
            assert extra['price'] == 200
            assert extra['amount'] == 5
            assert extra['operation'] == 'spread_creation_success'

    def test_log_creation_error(self):
        """Test logging spread creation error."""
        spread_logger = SpreadLogger()
        
        with patch.object(spread_logger.logger, 'error') as mock_error:
            test_error = Exception("Test error message")
            
            spread_logger.log_creation_error(
                user_id=12345,
                error=test_error,
                far_leg_ticker='GAZP',
                near_leg_ticker='GZZ4',
                context={'step': 'validation'}
            )
            
            mock_error.assert_called_once()
            call_args = mock_error.call_args
            
            # Check log message
            assert 'Spread creation error' in call_args[0][0]
            assert 'Test error message' in call_args[0][0]
            
            # Check extra data
            extra = call_args[1]['extra']
            assert extra['user_id'] == 12345
            assert extra['error_type'] == 'Exception'
            assert extra['error_message'] == 'Test error message'
            assert extra['far_leg_ticker'] == 'GAZP'
            assert extra['near_leg_ticker'] == 'GZZ4'
            assert extra['context'] == {'step': 'validation'}
            assert extra['operation'] == 'spread_creation_error'

    def test_log_user_action(self):
        """Test logging user actions."""
        spread_logger = SpreadLogger()
        
        with patch.object(spread_logger.logger, 'info') as mock_info:
            spread_logger.log_user_action(
                user_id=12345,
                action='direction_selected',
                details={'direction': 'buy', 'step': 'direction_selection'}
            )
            
            mock_info.assert_called_once()
            call_args = mock_info.call_args
            
            # Check log message
            assert 'User action: direction_selected' in call_args[0][0]
            
            # Check extra data
            extra = call_args[1]['extra']
            assert extra['user_id'] == 12345
            assert extra['action'] == 'direction_selected'
            assert extra['details'] == {'direction': 'buy', 'step': 'direction_selection'}
            assert extra['operation'] == 'user_action'

    def test_log_api_call(self):
        """Test logging API calls."""
        spread_logger = SpreadLogger()
        
        with patch.object(spread_logger.logger, 'debug') as mock_debug:
            spread_logger.log_api_call(
                user_id=12345,
                endpoint='validate_ticker',
                method='GET',
                params={'ticker': 'GAZP'},
                response_status=200,
                duration_ms=150
            )
            
            mock_debug.assert_called_once()
            call_args = mock_debug.call_args
            
            # Check log message
            assert 'API call: GET validate_ticker' in call_args[0][0]
            
            # Check extra data
            extra = call_args[1]['extra']
            assert extra['user_id'] == 12345
            assert extra['endpoint'] == 'validate_ticker'
            assert extra['method'] == 'GET'
            assert extra['params'] == {'ticker': 'GAZP'}
            assert extra['response_status'] == 200
            assert extra['duration_ms'] == 150
            assert extra['operation'] == 'api_call'

    def test_log_validation_error(self):
        """Test logging validation errors."""
        spread_logger = SpreadLogger()
        
        with patch.object(spread_logger.logger, 'warning') as mock_warning:
            spread_logger.log_validation_error(
                user_id=12345,
                field='price',
                value='invalid',
                error_message='Price must be a positive integer'
            )
            
            mock_warning.assert_called_once()
            call_args = mock_warning.call_args
            
            # Check log message
            assert 'Validation error for field price' in call_args[0][0]
            
            # Check extra data
            extra = call_args[1]['extra']
            assert extra['user_id'] == 12345
            assert extra['field'] == 'price'
            assert extra['value'] == 'invalid'
            assert extra['error_message'] == 'Price must be a positive integer'
            assert extra['operation'] == 'validation_error'

    def test_log_session_event(self):
        """Test logging session events."""
        spread_logger = SpreadLogger()
        
        with patch.object(spread_logger.logger, 'info') as mock_info:
            spread_logger.log_session_event(
                user_id=12345,
                event='session_started',
                session_data={'far_leg': 'GAZP', 'near_leg': 'GZZ4'}
            )
            
            mock_info.assert_called_once()
            call_args = mock_info.call_args
            
            # Check log message
            assert 'Session event: session_started' in call_args[0][0]
            
            # Check extra data
            extra = call_args[1]['extra']
            assert extra['user_id'] == 12345
            assert extra['event'] == 'session_started'
            assert extra['session_data'] == {'far_leg': 'GAZP', 'near_leg': 'GZZ4'}
            assert extra['operation'] == 'session_event'


class TestLoggingFunctions:
    """Test standalone logging functions."""

    @patch('spread_logging.get_spread_logger')
    def test_log_spread_creation_attempt(self, mock_get_logger):
        """Test log_spread_creation_attempt function."""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        
        log_spread_creation_attempt(
            user_id=12345,
            far_leg_ticker='GAZP',
            near_leg_ticker='GZZ4',
            direction='buy'
        )
        
        mock_logger.log_creation_attempt.assert_called_once_with(
            user_id=12345,
            far_leg_ticker='GAZP',
            near_leg_ticker='GZZ4',
            direction='buy',
            price=None,
            amount=None
        )

    @patch('spread_logging.get_spread_logger')
    def test_log_spread_creation_success(self, mock_get_logger):
        """Test log_spread_creation_success function."""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        
        log_spread_creation_success(
            user_id=12345,
            spread_id=67890,
            far_leg_ticker='GAZP',
            near_leg_ticker='GZZ4'
        )
        
        mock_logger.log_creation_success.assert_called_once_with(
            user_id=12345,
            spread_id=67890,
            far_leg_ticker='GAZP',
            near_leg_ticker='GZZ4',
            direction=None,
            price=None,
            amount=None
        )

    @patch('spread_logging.get_spread_logger')
    def test_log_spread_creation_error(self, mock_get_logger):
        """Test log_spread_creation_error function."""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        
        test_error = Exception("Test error")
        
        log_spread_creation_error(
            user_id=12345,
            error=test_error,
            context={'step': 'validation'}
        )
        
        mock_logger.log_creation_error.assert_called_once_with(
            user_id=12345,
            error=test_error,
            far_leg_ticker=None,
            near_leg_ticker=None,
            context={'step': 'validation'}
        )

    @patch('spread_logging.get_spread_logger')
    def test_log_user_action(self, mock_get_logger):
        """Test log_user_action function."""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        
        log_user_action(
            user_id=12345,
            action='button_clicked',
            details={'button': 'buy_spread'}
        )
        
        mock_logger.log_user_action.assert_called_once_with(
            user_id=12345,
            action='button_clicked',
            details={'button': 'buy_spread'}
        )

    @patch('spread_logging.get_spread_logger')
    def test_log_api_call(self, mock_get_logger):
        """Test log_api_call function."""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        
        log_api_call(
            user_id=12345,
            endpoint='create_spread',
            method='POST',
            response_status=201
        )
        
        mock_logger.log_api_call.assert_called_once_with(
            user_id=12345,
            endpoint='create_spread',
            method='POST',
            params=None,
            response_status=201,
            duration_ms=None
        )

    @patch('spread_logging.get_spread_logger')
    def test_log_validation_error(self, mock_get_logger):
        """Test log_validation_error function."""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        
        log_validation_error(
            user_id=12345,
            field='amount',
            value=-5,
            error_message='Amount must be positive'
        )
        
        mock_logger.log_validation_error.assert_called_once_with(
            user_id=12345,
            field='amount',
            value=-5,
            error_message='Amount must be positive'
        )

    @patch('spread_logging.get_spread_logger')
    def test_log_session_event(self, mock_get_logger):
        """Test log_session_event function."""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        
        log_session_event(
            user_id=12345,
            event='session_timeout',
            session_data={'duration': 1800}
        )
        
        mock_logger.log_session_event.assert_called_once_with(
            user_id=12345,
            event='session_timeout',
            session_data={'duration': 1800}
        )


class TestLoggingConfiguration:
    """Test logging configuration functions."""

    @patch('logging.getLogger')
    def test_configure_spread_logging_basic(self, mock_get_logger):
        """Test basic logging configuration."""
        mock_logger = Mock()
        mock_logger.handlers = []  # No existing handlers
        mock_get_logger.return_value = mock_logger
        
        configure_spread_logging()
        
        # Check logger configuration
        mock_get_logger.assert_called_with('spread_creation')
        mock_logger.setLevel.assert_called_with(logging.INFO)
        
        # Check that addHandler was called (handler creation is internal)
        assert mock_logger.addHandler.called

    @patch('logging.getLogger')
    def test_configure_spread_logging_with_level(self, mock_get_logger):
        """Test logging configuration with custom level."""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        
        configure_spread_logging(level=logging.DEBUG)
        
        mock_logger.setLevel.assert_called_with(logging.DEBUG)

    @patch('logging.getLogger')
    def test_configure_spread_logging_with_format(self, mock_get_logger):
        """Test logging configuration with custom format."""
        mock_logger = Mock()
        mock_logger.handlers = []  # No existing handlers
        mock_get_logger.return_value = mock_logger
        
        custom_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        
        configure_spread_logging(log_format=custom_format)
        
        # Check that logger was configured
        mock_logger.setLevel.assert_called_with(logging.INFO)
        assert mock_logger.addHandler.called


class TestLogMessageFormats:
    """Test log message formats and content."""

    def test_creation_attempt_message_format(self):
        """Test that creation attempt messages have correct format."""
        spread_logger = SpreadLogger()
        
        with patch.object(spread_logger.logger, 'info') as mock_info:
            spread_logger.log_creation_attempt(
                user_id=12345,
                far_leg_ticker='GAZP',
                near_leg_ticker='GZZ4',
                direction='buy',
                price=150,
                amount=10
            )
            
            message = mock_info.call_args[0][0]
            
            # Check message contains key information
            assert 'Spread creation attempt' in message
            assert 'user 12345' in message
            assert 'GAZP/GZZ4' in message
            assert 'buy' in message
            assert '150' in message
            assert '10' in message

    def test_creation_success_message_format(self):
        """Test that creation success messages have correct format."""
        spread_logger = SpreadLogger()
        
        with patch.object(spread_logger.logger, 'info') as mock_info:
            spread_logger.log_creation_success(
                user_id=12345,
                spread_id=67890,
                far_leg_ticker='GAZP',
                near_leg_ticker='GZZ4',
                direction='sell',
                price=200,
                amount=5
            )
            
            message = mock_info.call_args[0][0]
            
            # Check message contains key information
            assert 'Spread created successfully' in message
            assert 'ID 67890' in message
            assert 'user 12345' in message
            assert 'GAZP/GZZ4' in message
            assert 'sell' in message

    def test_creation_error_message_format(self):
        """Test that creation error messages have correct format."""
        spread_logger = SpreadLogger()
        
        with patch.object(spread_logger.logger, 'error') as mock_error:
            test_error = ValueError("Invalid price format")
            
            spread_logger.log_creation_error(
                user_id=12345,
                error=test_error,
                far_leg_ticker='GAZP',
                near_leg_ticker='GZZ4'
            )
            
            message = mock_error.call_args[0][0]
            
            # Check message contains key information
            assert 'Spread creation error' in message
            assert 'user 12345' in message
            assert 'ValueError' in message
            assert 'Invalid price format' in message
            assert 'GAZP/GZZ4' in message

    def test_user_action_message_format(self):
        """Test that user action messages have correct format."""
        spread_logger = SpreadLogger()
        
        with patch.object(spread_logger.logger, 'info') as mock_info:
            spread_logger.log_user_action(
                user_id=12345,
                action='price_entered',
                details={'price': 150, 'method': 'custom'}
            )
            
            message = mock_info.call_args[0][0]
            
            # Check message contains key information
            assert 'User action: price_entered' in message
            assert 'user 12345' in message

    def test_api_call_message_format(self):
        """Test that API call messages have correct format."""
        spread_logger = SpreadLogger()
        
        with patch.object(spread_logger.logger, 'debug') as mock_debug:
            spread_logger.log_api_call(
                user_id=12345,
                endpoint='validate_ticker',
                method='GET',
                response_status=200,
                duration_ms=150
            )
            
            message = mock_debug.call_args[0][0]
            
            # Check message contains key information
            assert 'API call: GET validate_ticker' in message
            assert 'user 12345' in message
            assert '200' in message
            assert '150.0ms' in message

    def test_validation_error_message_format(self):
        """Test that validation error messages have correct format."""
        spread_logger = SpreadLogger()
        
        with patch.object(spread_logger.logger, 'warning') as mock_warning:
            spread_logger.log_validation_error(
                user_id=12345,
                field='amount',
                value='abc',
                error_message='Amount must be numeric'
            )
            
            message = mock_warning.call_args[0][0]
            
            # Check message contains key information
            assert 'Validation error for field amount' in message
            assert 'user 12345' in message
            assert 'abc' in message
            assert 'Amount must be numeric' in message

    def test_session_event_message_format(self):
        """Test that session event messages have correct format."""
        spread_logger = SpreadLogger()
        
        with patch.object(spread_logger.logger, 'info') as mock_info:
            spread_logger.log_session_event(
                user_id=12345,
                event='session_created',
                session_data={'tickers': 'GAZP/GZZ4'}
            )
            
            message = mock_info.call_args[0][0]
            
            # Check message contains key information
            assert 'Session event: session_created' in message
            assert 'user 12345' in message