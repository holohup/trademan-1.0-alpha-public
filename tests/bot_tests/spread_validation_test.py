"""
Tests for spread validation module.

This module tests all validation functions with edge cases and error scenarios
to ensure robust input validation for the spread creation process.
"""

import pytest
from decimal import Decimal
from bot.spread_validation import (
    validate_price_input,
    validate_amount_input,
    validate_ticker_format,
    validate_ticker_pair,
    validate_spread_direction,
    validate_lot_requirements,
    validate_price_reasonableness,
    validate_session_completeness,
    get_validation_error_message,
    PriceValidationError,
    AmountValidationError,
    TickerValidationError,
    ValidationError,
)


class TestValidatePriceInput:
    """Test price input validation."""

    def test_valid_price_input(self):
        """Test validation with valid price input."""
        assert validate_price_input("150") == 150
        assert validate_price_input("1") == 1
        assert validate_price_input("999999") == 999999

    def test_valid_price_with_whitespace(self):
        """Test validation with whitespace around price."""
        assert validate_price_input("  150  ") == 150
        assert validate_price_input("\t100\n") == 100

    def test_empty_price_input(self):
        """Test validation with empty price input."""
        with pytest.raises(PriceValidationError, match="Price cannot be empty"):
            validate_price_input("")

        with pytest.raises(PriceValidationError, match="Price cannot be empty"):
            validate_price_input("   ")

        with pytest.raises(PriceValidationError, match="Price cannot be empty"):
            validate_price_input(None)

    def test_invalid_price_format(self):
        """Test validation with invalid price formats."""
        with pytest.raises(PriceValidationError, match="Price must be a valid integer"):
            validate_price_input("abc")

        with pytest.raises(PriceValidationError, match="Price must be a valid integer"):
            validate_price_input("12.5")

        with pytest.raises(PriceValidationError, match="Price must be a valid integer"):
            validate_price_input("12,5")

        with pytest.raises(PriceValidationError, match="Price must be a valid integer"):
            validate_price_input("12.0")

    def test_negative_price(self):
        """Test validation with negative price."""
        with pytest.raises(PriceValidationError, match="Price must be a positive integer"):
            validate_price_input("-10")

    def test_zero_price(self):
        """Test validation with zero price."""
        with pytest.raises(PriceValidationError, match="Price must be a positive integer"):
            validate_price_input("0")

    def test_price_with_min_constraint(self):
        """Test validation with minimum price constraint."""
        assert validate_price_input("100", min_price=50) == 100

        with pytest.raises(PriceValidationError, match="Price must be at least 100"):
            validate_price_input("50", min_price=100)

    def test_price_with_max_constraint(self):
        """Test validation with maximum price constraint."""
        assert validate_price_input("100", max_price=200) == 100

        with pytest.raises(PriceValidationError, match="Price cannot exceed 100"):
            validate_price_input("150", max_price=100)

    def test_price_with_increment_constraint(self):
        """Test validation with price increment constraint."""
        # Test with 0.01 increment (1 kopeck)
        increment = Decimal("0.01")
        assert validate_price_input("100", min_price_increment=increment) == 100

        # Test with 0.1 increment (10 kopecks)
        increment = Decimal("0.1")
        assert validate_price_input("100", min_price_increment=increment) == 100

        with pytest.raises(PriceValidationError, match="Price must be a multiple of"):
            validate_price_input("105", min_price_increment=Decimal("0.1"))

    def test_price_with_all_constraints(self):
        """Test validation with all constraints combined."""
        result = validate_price_input(
            "100",
            min_price=50,
            max_price=200,
            min_price_increment=Decimal("0.1")
        )
        assert result == 100


class TestValidateAmountInput:
    """Test amount input validation."""

    def test_valid_amount_input(self):
        """Test validation with valid amount input."""
        assert validate_amount_input("5") == 5
        assert validate_amount_input("1") == 1
        assert validate_amount_input("1000") == 1000

    def test_valid_amount_with_whitespace(self):
        """Test validation with whitespace around amount."""
        assert validate_amount_input("  10  ") == 10
        assert validate_amount_input("\t5\n") == 5

    def test_empty_amount_input(self):
        """Test validation with empty amount input."""
        with pytest.raises(AmountValidationError, match="Amount cannot be empty"):
            validate_amount_input("")

        with pytest.raises(AmountValidationError, match="Amount cannot be empty"):
            validate_amount_input("   ")

        with pytest.raises(AmountValidationError, match="Amount cannot be empty"):
            validate_amount_input(None)

    def test_invalid_amount_format(self):
        """Test validation with invalid amount formats."""
        with pytest.raises(AmountValidationError, match="Amount must be a valid integer"):
            validate_amount_input("abc")

        with pytest.raises(AmountValidationError, match="Amount must be a valid integer"):
            validate_amount_input("5.5")

        with pytest.raises(AmountValidationError, match="Amount must be a valid integer"):
            validate_amount_input("5,0")

    def test_negative_amount(self):
        """Test validation with negative amount."""
        with pytest.raises(AmountValidationError, match="Amount must be a positive integer"):
            validate_amount_input("-5")

    def test_zero_amount(self):
        """Test validation with zero amount."""
        with pytest.raises(AmountValidationError, match="Amount must be a positive integer"):
            validate_amount_input("0")

    def test_amount_with_min_lot_constraint(self):
        """Test validation with minimum lot constraint."""
        assert validate_amount_input("10", min_lot=5) == 10

        with pytest.raises(AmountValidationError, match="Amount must be at least 10"):
            validate_amount_input("5", min_lot=10)

    def test_amount_with_max_constraint(self):
        """Test validation with maximum amount constraint."""
        assert validate_amount_input("50", max_amount=100) == 50

        with pytest.raises(AmountValidationError, match="Amount cannot exceed 50"):
            validate_amount_input("100", max_amount=50)


class TestValidateTickerFormat:
    """Test ticker format validation."""

    def test_valid_ticker_formats(self):
        """Test validation with valid ticker formats."""
        assert validate_ticker_format("GAZP") == "GAZP"
        assert validate_ticker_format("GZZ4") == "GZZ4"
        assert validate_ticker_format("SBER") == "SBER"
        assert validate_ticker_format("AB") == "AB"  # Minimum length
        assert validate_ticker_format("ABCDEFGHIJKL") == "ABCDEFGHIJKL"  # Maximum length

    def test_ticker_case_normalization(self):
        """Test ticker case normalization."""
        assert validate_ticker_format("gazp") == "GAZP"
        assert validate_ticker_format("GaZp") == "GAZP"
        assert validate_ticker_format("gzz4") == "GZZ4"

    def test_ticker_whitespace_handling(self):
        """Test ticker whitespace handling."""
        assert validate_ticker_format("  GAZP  ") == "GAZP"
        assert validate_ticker_format("\tSBER\n") == "SBER"

    def test_empty_ticker_input(self):
        """Test validation with empty ticker input."""
        with pytest.raises(TickerValidationError, match="Ticker cannot be empty"):
            validate_ticker_format("")

        with pytest.raises(TickerValidationError, match="Ticker cannot be empty"):
            validate_ticker_format("   ")

        with pytest.raises(TickerValidationError, match="Ticker cannot be empty"):
            validate_ticker_format(None)

    def test_invalid_ticker_characters(self):
        """Test validation with invalid ticker characters."""
        with pytest.raises(TickerValidationError, match="Ticker must contain only letters and numbers"):
            validate_ticker_format("GAZ-P")

        with pytest.raises(TickerValidationError, match="Ticker must contain only letters and numbers"):
            validate_ticker_format("GAZ P")

        with pytest.raises(TickerValidationError, match="Ticker must contain only letters and numbers"):
            validate_ticker_format("GAZ.P")

        with pytest.raises(TickerValidationError, match="Ticker must contain only letters and numbers"):
            validate_ticker_format("GAZ_P")

    def test_ticker_length_constraints(self):
        """Test ticker length constraints."""
        with pytest.raises(TickerValidationError, match="Ticker must be at least 2 characters long"):
            validate_ticker_format("A")

        with pytest.raises(TickerValidationError, match="Ticker cannot be longer than 12 characters"):
            validate_ticker_format("ABCDEFGHIJKLM")


class TestValidateTickerPair:
    """Test ticker pair validation."""

    def test_valid_ticker_pair(self):
        """Test validation with valid ticker pair."""
        far, near = validate_ticker_pair("GAZP", "GZZ4")
        assert far == "GAZP"
        assert near == "GZZ4"

    def test_ticker_pair_case_normalization(self):
        """Test ticker pair case normalization."""
        far, near = validate_ticker_pair("gazp", "gzz4")
        assert far == "GAZP"
        assert near == "GZZ4"

    def test_identical_tickers(self):
        """Test validation with identical tickers."""
        with pytest.raises(TickerValidationError, match="Far leg and near leg tickers must be different"):
            validate_ticker_pair("GAZP", "GAZP")

    def test_case_insensitive_identical_tickers(self):
        """Test validation with case-insensitive identical tickers."""
        with pytest.raises(TickerValidationError, match="Far leg and near leg tickers must be different"):
            validate_ticker_pair("GAZP", "gazp")

    def test_invalid_ticker_in_pair(self):
        """Test validation with invalid ticker in pair."""
        with pytest.raises(TickerValidationError):
            validate_ticker_pair("GAZ-P", "GZZ4")

        with pytest.raises(TickerValidationError):
            validate_ticker_pair("GAZP", "")


class TestValidateSpreadDirection:
    """Test spread direction validation."""

    def test_valid_directions(self):
        """Test validation with valid directions."""
        assert validate_spread_direction("buy") == "buy"
        assert validate_spread_direction("sell") == "sell"

    def test_direction_case_normalization(self):
        """Test direction case normalization."""
        assert validate_spread_direction("BUY") == "buy"
        assert validate_spread_direction("SELL") == "sell"
        assert validate_spread_direction("Buy") == "buy"

    def test_direction_whitespace_handling(self):
        """Test direction whitespace handling."""
        assert validate_spread_direction("  buy  ") == "buy"
        assert validate_spread_direction("\tsell\n") == "sell"

    def test_invalid_directions(self):
        """Test validation with invalid directions."""
        with pytest.raises(ValidationError, match="Direction must be 'buy' or 'sell'"):
            validate_spread_direction("long")

        with pytest.raises(ValidationError, match="Direction must be 'buy' or 'sell'"):
            validate_spread_direction("short")

        with pytest.raises(ValidationError, match="Direction must be 'buy' or 'sell'"):
            validate_spread_direction("invalid")

    def test_empty_direction(self):
        """Test validation with empty direction."""
        with pytest.raises(ValidationError, match="Direction cannot be empty"):
            validate_spread_direction("")

        with pytest.raises(ValidationError, match="Direction cannot be empty"):
            validate_spread_direction(None)


class TestValidateLotRequirements:
    """Test lot requirements validation."""

    def test_valid_lot_requirements(self):
        """Test validation with valid lot requirements."""
        far_leg_data = {'ticker': 'GAZP', 'lot': 10}
        near_leg_data = {'ticker': 'GZZ4', 'lot': 1}

        assert validate_lot_requirements(10, far_leg_data, near_leg_data) is True

    def test_amount_not_multiple_of_far_lot(self):
        """Test validation when amount is not multiple of far leg lot."""
        far_leg_data = {'ticker': 'GAZP', 'lot': 10}
        near_leg_data = {'ticker': 'GZZ4', 'lot': 1}

        with pytest.raises(AmountValidationError, match="Amount must be a multiple of 10"):
            validate_lot_requirements(15, far_leg_data, near_leg_data)

    def test_amount_not_multiple_of_near_lot(self):
        """Test validation when amount is not multiple of near leg lot."""
        far_leg_data = {'ticker': 'GAZP', 'lot': 1}
        near_leg_data = {'ticker': 'GZZ4', 'lot': 10}

        with pytest.raises(AmountValidationError, match="Amount must be a multiple of 10"):
            validate_lot_requirements(15, far_leg_data, near_leg_data)

    def test_missing_lot_data(self):
        """Test validation with missing lot data (defaults to 1)."""
        far_leg_data = {'ticker': 'GAZP'}  # No lot field
        near_leg_data = {'ticker': 'GZZ4'}  # No lot field

        assert validate_lot_requirements(5, far_leg_data, near_leg_data) is True

    def test_complex_lot_requirements(self):
        """Test validation with complex lot requirements."""
        far_leg_data = {'ticker': 'GAZP', 'lot': 100}
        near_leg_data = {'ticker': 'GZZ4', 'lot': 50}

        # Amount must be multiple of both 100 and 50 (LCM = 100)
        assert validate_lot_requirements(100, far_leg_data, near_leg_data) is True

        with pytest.raises(AmountValidationError):
            validate_lot_requirements(50, far_leg_data, near_leg_data)


class TestValidatePriceReasonableness:
    """Test price reasonableness validation."""

    def test_reasonable_price(self):
        """Test validation with reasonable price."""
        assert validate_price_reasonableness(100, 100) is True  # Exact match
        assert validate_price_reasonableness(120, 100) is True  # 20% deviation
        assert validate_price_reasonableness(80, 100) is True   # 20% deviation

    def test_unreasonable_price(self):
        """Test validation with unreasonable price."""
        with pytest.raises(PriceValidationError, match="Price deviates"):
            validate_price_reasonableness(200, 100)  # 100% deviation

        with pytest.raises(PriceValidationError, match="Price deviates"):
            validate_price_reasonableness(10, 100)   # 90% deviation

    def test_custom_tolerance(self):
        """Test validation with custom tolerance."""
        # 10% tolerance
        assert validate_price_reasonableness(110, 100, tolerance_percent=10.0) is True

        with pytest.raises(PriceValidationError):
            validate_price_reasonableness(120, 100, tolerance_percent=10.0)

    def test_no_market_price(self):
        """Test validation without market price."""
        assert validate_price_reasonableness(100, None) is True

    def test_invalid_market_price(self):
        """Test validation with invalid market price."""
        assert validate_price_reasonableness(100, 0) is True
        assert validate_price_reasonableness(100, -10) is True


class TestValidateSessionCompleteness:
    """Test session completeness validation."""

    def test_complete_session(self):
        """Test validation with complete session."""
        state = {
            'far_leg_data': {'ticker': 'GAZP', 'figi': 'BBG004730N88'},
            'near_leg_data': {'ticker': 'GZZ4', 'figi': 'BBG00Y91R9T3'},
            'direction': 'buy',
            'custom_price': 150,
            'amount': 10
        }

        missing = validate_session_completeness(state)
        assert missing == []

    def test_missing_far_leg_data(self):
        """Test validation with missing far leg data."""
        state = {
            'near_leg_data': {'ticker': 'GZZ4', 'figi': 'BBG00Y91R9T3'},
            'direction': 'buy',
            'custom_price': 150,
            'amount': 10
        }

        missing = validate_session_completeness(state)
        assert 'far_leg_data' in missing

    def test_missing_multiple_fields(self):
        """Test validation with multiple missing fields."""
        state = {
            'far_leg_data': {'ticker': 'GAZP', 'figi': 'BBG004730N88'},
        }

        missing = validate_session_completeness(state)
        assert 'near_leg_data' in missing
        assert 'direction' in missing
        assert 'custom_price' in missing
        assert 'amount' in missing

    def test_zero_price_treated_as_missing(self):
        """Test that None price is treated as missing."""
        state = {
            'far_leg_data': {'ticker': 'GAZP', 'figi': 'BBG004730N88'},
            'near_leg_data': {'ticker': 'GZZ4', 'figi': 'BBG00Y91R9T3'},
            'direction': 'buy',
            'custom_price': None,
            'amount': 10
        }

        missing = validate_session_completeness(state)
        assert 'custom_price' in missing


class TestGetValidationErrorMessage:
    """Test validation error message generation."""

    def test_price_validation_error_messages(self):
        """Test price validation error message formatting."""
        error = PriceValidationError("Price cannot be empty")
        message = get_validation_error_message(error)
        assert "❌" in message
        assert "💡" in message
        assert "whole number" in message

        error = PriceValidationError("Price must be a valid integer")
        message = get_validation_error_message(error)
        assert "numbers without decimals" in message

    def test_amount_validation_error_messages(self):
        """Test amount validation error message formatting."""
        error = AmountValidationError("Amount cannot be empty")
        message = get_validation_error_message(error)
        assert "❌" in message
        assert "💡" in message
        assert "whole number" in message

        error = AmountValidationError("Amount must be at least 10 (minimum lot requirement)")
        message = get_validation_error_message(error)
        assert "lot size requirements" in message

    def test_ticker_validation_error_messages(self):
        """Test ticker validation error message formatting."""
        error = TickerValidationError("Ticker cannot be empty")
        message = get_validation_error_message(error)
        assert "❌" in message
        assert "💡" in message
        assert "ticker symbol" in message

        error = TickerValidationError("Far leg and near leg tickers must be different")
        message = get_validation_error_message(error)
        assert "two different instruments" in message

    def test_generic_validation_error_message(self):
        """Test generic validation error message formatting."""
        error = ValidationError("Generic error")
        message = get_validation_error_message(error)
        assert "❌ Generic error" == message


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_very_large_numbers(self):
        """Test validation with very large numbers."""
        # Test maximum integer values
        large_price = str(2**31 - 1)  # Max 32-bit signed integer
        assert validate_price_input(large_price) == 2**31 - 1

        large_amount = str(2**31 - 1)
        assert validate_amount_input(large_amount) == 2**31 - 1

    def test_unicode_input(self):
        """Test validation with unicode characters."""
        with pytest.raises(TickerValidationError):
            validate_ticker_format("ГАЗП")  # Cyrillic characters

        with pytest.raises(PriceValidationError):
            validate_price_input("15€")  # Numbers with currency symbol

    def test_special_whitespace_characters(self):
        """Test validation with special whitespace characters."""
        # Non-breaking space
        with pytest.raises(TickerValidationError):
            validate_ticker_format("GAZ\u00A0P")

        # Tab and newline handling
        assert validate_ticker_format("\t\nGAZP\r\n") == "GAZP"

    def test_boundary_ticker_lengths(self):
        """Test ticker validation at length boundaries."""
        # Exactly 2 characters (minimum)
        assert validate_ticker_format("AB") == "AB"

        # Exactly 12 characters (maximum)
        assert validate_ticker_format("ABCDEFGHIJKL") == "ABCDEFGHIJKL"

        # Just over maximum
        with pytest.raises(TickerValidationError):
            validate_ticker_format("ABCDEFGHIJKLM")