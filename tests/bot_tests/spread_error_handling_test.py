"""
Tests for spread error handling module.

This module tests error handling scenarios and message generation
to ensure robust error handling for the spread creation process.
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from aiogram import types
from bot.spread_error_handling import (
    get_user_friendly_error_message,
    log_spread_operation,
    create_error_recovery_suggestions,
    SessionTimeoutError,
    SpreadCreationError,
)


class TestGetUserFriendlyErrorMessage:
    """Test user-friendly error message generation."""

    def test_session_timeout_error_message(self):
        """Test message generation for session timeout errors."""
        error = SessionTimeoutError("Session expired")
        message = get_user_friendly_error_message(error)
        
        assert "⏰" in message
        assert "Session Expired" in message
        assert "security reasons" in message

    def test_spread_creation_error_message(self):
        """Test message generation for spread creation errors."""
        error = SpreadCreationError("Duplicate spread")
        message = get_user_friendly_error_message(error)
        
        assert "❌" in message
        assert "Spread Creation Failed" in message
        assert "Duplicate spread" in message

    def test_unexpected_error_message(self):
        """Test message generation for unexpected errors."""
        error = ValueError("Unexpected error")
        message = get_user_friendly_error_message(error)
        
        assert "❌" in message
        assert "Unexpected Error" in message
        assert "Unexpected error" in message

    def test_error_message_with_context(self):
        """Test error message generation with context."""
        error = ValueError("Test error")
        context = {'ticker': 'GAZP', 'operation': 'validation'}
        message = get_user_friendly_error_message(error, context)
        
        assert "❌" in message
        assert "Test error" in message


class TestLogSpreadOperation:
    """Test spread operation logging."""

    @patch('bot.spread_error_handling.logger')
    def test_successful_operation_logging(self, mock_logger):
        """Test logging of successful operations."""
        log_spread_operation(
            operation="ticker_validation",
            user_id=123456,
            success=True,
            details={'ticker': 'GAZP'}
        )
        
        mock_logger.info.assert_called_once()
        call_args = mock_logger.info.call_args
        
        assert "ticker_validation" in call_args[0][0]
        assert "succeeded" in call_args[0][0]
        assert call_args[1]['extra']['user_id'] == 123456
        assert call_args[1]['extra']['success'] is True
        assert call_args[1]['extra']['ticker'] == 'GAZP'

    @patch('bot.spread_error_handling.logger')
    def test_failed_operation_logging(self, mock_logger):
        """Test logging of failed operations."""
        error = ValueError("Test error")
        
        log_spread_operation(
            operation="price_validation",
            user_id=123456,
            success=False,
            error=error
        )
        
        mock_logger.error.assert_called_once()
        call_args = mock_logger.error.call_args
        
        assert "price_validation" in call_args[0][0]
        assert "failed" in call_args[0][0]
        assert call_args[1]['extra']['user_id'] == 123456
        assert call_args[1]['extra']['success'] is False
        assert call_args[1]['extra']['error_type'] == 'ValueError'
        assert call_args[1]['extra']['error_message'] == 'Test error'

    @patch('bot.spread_error_handling.logger')
    def test_logging_without_error_details(self, mock_logger):
        """Test logging when no error details are provided."""
        log_spread_operation(
            operation="test_operation",
            user_id=123456,
            success=False
        )
        
        mock_logger.error.assert_called_once()
        call_args = mock_logger.error.call_args
        
        assert call_args[1]['extra']['error_type'] == 'Unknown'
        assert call_args[1]['extra']['error_message'] == 'Unknown error'


class TestCreateErrorRecoverySuggestions:
    """Test error recovery suggestions generation."""

    def test_ticker_validation_suggestions(self):
        """Test suggestions for ticker validation errors."""
        suggestions = create_error_recovery_suggestions('ticker_validation', {})
        
        assert "💡" in suggestions
        assert "Suggestions" in suggestions
        assert "ticker symbol spelling" in suggestions
        assert "MOEX" in suggestions

    def test_price_fetch_suggestions(self):
        """Test suggestions for price fetch errors."""
        suggestions = create_error_recovery_suggestions('price_fetch', {})
        
        assert "💡" in suggestions
        assert "market hours" in suggestions
        assert "actively traded" in suggestions

    def test_api_connection_suggestions(self):
        """Test suggestions for API connection errors."""
        suggestions = create_error_recovery_suggestions('api_connection', {})
        
        assert "💡" in suggestions
        assert "internet connection" in suggestions
        assert "trading system" in suggestions

    def test_validation_suggestions(self):
        """Test suggestions for validation errors."""
        suggestions = create_error_recovery_suggestions('validation', {})
        
        assert "💡" in suggestions
        assert "input format" in suggestions
        assert "required fields" in suggestions

    def test_session_timeout_suggestions(self):
        """Test suggestions for session timeout errors."""
        suggestions = create_error_recovery_suggestions('session_timeout', {})
        
        assert "💡" in suggestions
        assert "/addspread" in suggestions
        assert "quickly" in suggestions

    def test_unknown_error_suggestions(self):
        """Test suggestions for unknown error types."""
        suggestions = create_error_recovery_suggestions('unknown_error', {})
        
        assert "💡" in suggestions
        assert "Try the operation again" in suggestions
        assert "Contact support" in suggestions


class TestSessionTimeoutError:
    """Test SessionTimeoutError exception."""

    def test_session_timeout_error_creation(self):
        """Test creating SessionTimeoutError."""
        error = SessionTimeoutError("Session expired")
        assert str(error) == "Session expired"
        assert isinstance(error, Exception)

    def test_session_timeout_error_inheritance(self):
        """Test SessionTimeoutError inheritance."""
        error = SessionTimeoutError("Test")
        assert isinstance(error, Exception)


class TestSpreadCreationError:
    """Test SpreadCreationError exception."""

    def test_spread_creation_error_creation(self):
        """Test creating SpreadCreationError."""
        error = SpreadCreationError("Creation failed")
        assert str(error) == "Creation failed"
        assert isinstance(error, Exception)

    def test_spread_creation_error_inheritance(self):
        """Test SpreadCreationError inheritance."""
        error = SpreadCreationError("Test")
        assert isinstance(error, Exception)


class TestErrorHandlingIntegration:
    """Test integration of error handling components."""

    def test_error_message_formatting_consistency(self):
        """Test that all error messages follow consistent formatting."""
        errors = [
            SessionTimeoutError("Session expired"),
            SpreadCreationError("Creation failed"),
            ValueError("Unexpected error")
        ]
        
        for error in errors:
            message = get_user_friendly_error_message(error)
            
            # All messages should start with an emoji
            assert message.startswith(("❌", "⏰"))
            
            # All messages should have suggestions
            assert "💡" in message
            
            # Check specific error types have appropriate content
            if isinstance(error, SessionTimeoutError):
                assert "Session Expired" in message
            elif isinstance(error, SpreadCreationError):
                assert str(error) in message
            else:
                assert str(error) in message

    def test_logging_and_error_message_integration(self):
        """Test that logging and error messages work together."""
        with patch('bot.spread_error_handling.logger') as mock_logger:
            # Log an error
            error = ValueError("Test integration error")
            log_spread_operation(
                operation="test_operation",
                user_id=123456,
                success=False,
                error=error
            )
            
            # Generate user message
            user_message = get_user_friendly_error_message(error)
            
            # Verify both work correctly
            mock_logger.error.assert_called_once()
            assert "❌" in user_message
            assert "Test integration error" in user_message

    def test_recovery_suggestions_context_sensitivity(self):
        """Test that recovery suggestions are context-sensitive."""
        contexts = [
            'ticker_validation',
            'price_fetch',
            'api_connection',
            'validation',
            'session_timeout'
        ]
        
        suggestions_list = []
        for context in contexts:
            suggestions = create_error_recovery_suggestions(context, {})
            suggestions_list.append(suggestions)
            
            # Each context should have different suggestions
            assert "💡" in suggestions
            assert "Suggestions" in suggestions
        
        # Verify that different contexts produce different suggestions
        unique_suggestions = set(suggestions_list)
        assert len(unique_suggestions) == len(contexts)


class TestErrorHandlingEdgeCases:
    """Test edge cases in error handling."""

    def test_empty_error_message(self):
        """Test handling of errors with empty messages."""
        error = ValueError("")
        message = get_user_friendly_error_message(error)
        
        assert "❌" in message
        assert "Unexpected Error" in message

    def test_none_context(self):
        """Test error message generation with None context."""
        error = ValueError("Test error")
        message = get_user_friendly_error_message(error, None)
        
        assert "❌" in message
        assert "Test error" in message

    def test_empty_context(self):
        """Test error message generation with empty context."""
        error = ValueError("Test error")
        message = get_user_friendly_error_message(error, {})
        
        assert "❌" in message
        assert "Test error" in message

    def test_logging_with_none_error(self):
        """Test logging when error is None."""
        with patch('bot.spread_error_handling.logger') as mock_logger:
            log_spread_operation(
                operation="test_operation",
                user_id=123456,
                success=False,
                error=None
            )
            
            mock_logger.error.assert_called_once()
            call_args = mock_logger.error.call_args
            
            assert call_args[1]['extra']['error_type'] == 'Unknown'
            assert call_args[1]['extra']['error_message'] == 'Unknown error'

    def test_recovery_suggestions_unknown_type(self):
        """Test recovery suggestions for unknown error types."""
        suggestions = create_error_recovery_suggestions('unknown_type', {})
        
        assert "💡" in suggestions
        assert "Try the operation again" in suggestions
        assert "Contact support" in suggestions