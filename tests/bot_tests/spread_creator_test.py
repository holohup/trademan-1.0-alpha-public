import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from aiogram import types
from bot.spread_creator import handle_addspread_command, parse_addspread_command, validate_command_format


class TestParseAddspreadCommand:
    """Test command parsing functionality."""
    
    def test_parse_valid_command_with_two_tickers(self):
        """Test parsing valid command with two tickers."""
        result = parse_addspread_command("GAZP GZZ4")
        assert result == ("GAZP", "GZZ4")
    
    def test_parse_valid_command_with_extra_spaces(self):
        """Test parsing command with extra spaces."""
        result = parse_addspread_command("  SBER   SRZ4  ")
        assert result == ("SBER", "SRZ4")
    
    def test_parse_command_with_one_ticker(self):
        """Test parsing command with only one ticker."""
        result = parse_addspread_command("GAZP")
        assert result is None
    
    def test_parse_command_with_three_tickers(self):
        """Test parsing command with three tickers."""
        result = parse_addspread_command("GAZP GZZ4 EXTRA")
        assert result is None
    
    def test_parse_empty_command(self):
        """Test parsing empty command."""
        result = parse_addspread_command("")
        assert result is None
    
    def test_parse_command_with_only_spaces(self):
        """Test parsing command with only spaces."""
        result = parse_addspread_command("   ")
        assert result is None


class TestValidateCommandFormat:
    """Test command format validation."""
    
    def test_validate_valid_tickers(self):
        """Test validation with valid ticker format."""
        assert validate_command_format("GAZP", "GZZ4") is True
    
    def test_validate_empty_far_leg(self):
        """Test validation with empty far leg ticker."""
        assert validate_command_format("", "GZZ4") is False
    
    def test_validate_empty_near_leg(self):
        """Test validation with empty near leg ticker."""
        assert validate_command_format("GAZP", "") is False
    
    def test_validate_both_empty(self):
        """Test validation with both tickers empty."""
        assert validate_command_format("", "") is False
    
    def test_validate_none_tickers(self):
        """Test validation with None values."""
        assert validate_command_format(None, "GZZ4") is False
        assert validate_command_format("GAZP", None) is False
        assert validate_command_format(None, None) is False
    
    def test_validate_same_tickers(self):
        """Test validation with identical tickers."""
        assert validate_command_format("GAZP", "GAZP") is False
    
    def test_validate_case_insensitive_same_tickers(self):
        """Test validation with same tickers in different cases."""
        assert validate_command_format("GAZP", "gazp") is False
        assert validate_command_format("gazp", "GAZP") is False


class TestHandleAddspreadCommand:
    """Test the main command handler."""
    
    @pytest.fixture
    def mock_message(self):
        """Create a mock Telegram message."""
        message = MagicMock(spec=types.Message)
        message.from_user.id = 123456
        message.get_args.return_value = "GAZP GZZ4"
        message.answer = AsyncMock()
        return message
    
    @pytest.fixture
    def mock_message_invalid_format(self):
        """Create a mock message with invalid format."""
        message = MagicMock(spec=types.Message)
        message.from_user.id = 123456
        message.get_args.return_value = "GAZP"
        message.answer = AsyncMock()
        return message
    
    @pytest.fixture
    def mock_message_empty_args(self):
        """Create a mock message with empty args."""
        message = MagicMock(spec=types.Message)
        message.from_user.id = 123456
        message.get_args.return_value = ""
        message.answer = AsyncMock()
        return message
    
    @patch('bot.spread_creator.save_state')
    @pytest.mark.asyncio
    async def test_handle_valid_command(self, mock_save_state, mock_message):
        """Test handling valid addspread command."""
        await handle_addspread_command(mock_message)
        
        # Verify state was saved
        mock_save_state.assert_called_once()
        call_args = mock_save_state.call_args
        user_id, state_data = call_args[0]
        
        assert user_id == 123456
        assert state_data['far_leg_ticker'] == 'GAZP'
        assert state_data['near_leg_ticker'] == 'GZZ4'
        assert state_data['current_step'] == 'ticker_validation'
        
        # Verify response message
        mock_message.answer.assert_called_once()
        response_text = mock_message.answer.call_args[0][0]
        assert "Starting spread creation" in response_text
        assert "GAZP" in response_text
        assert "GZZ4" in response_text
    
    @pytest.mark.asyncio
    async def test_handle_invalid_format_one_ticker(self, mock_message_invalid_format):
        """Test handling command with invalid format (one ticker)."""
        await handle_addspread_command(mock_message_invalid_format)
        
        # Verify error message
        mock_message_invalid_format.answer.assert_called_once()
        response_text = mock_message_invalid_format.answer.call_args[0][0]
        assert "Usage:" in response_text
        assert "/addspread <far_leg_ticker> <near_leg_ticker>" in response_text
    
    @pytest.mark.asyncio
    async def test_handle_empty_args(self, mock_message_empty_args):
        """Test handling command with empty arguments."""
        await handle_addspread_command(mock_message_empty_args)
        
        # Verify error message
        mock_message_empty_args.answer.assert_called_once()
        response_text = mock_message_empty_args.answer.call_args[0][0]
        assert "Usage:" in response_text
        assert "/addspread <far_leg_ticker> <near_leg_ticker>" in response_text
    
    @patch('bot.spread_creator.save_state')
    @pytest.mark.asyncio
    async def test_handle_same_tickers(self, mock_save_state, mock_message):
        """Test handling command with identical tickers."""
        mock_message.get_args.return_value = "GAZP GAZP"
        
        await handle_addspread_command(mock_message)
        
        # Verify no state was saved
        mock_save_state.assert_not_called()
        
        # Verify error message
        mock_message.answer.assert_called_once()
        response_text = mock_message.answer.call_args[0][0]
        assert "Usage:" in response_text
    
    @patch('bot.spread_creator.get_state')
    @patch('bot.spread_creator.save_state')
    @pytest.mark.asyncio
    async def test_handle_existing_session(self, mock_save_state, mock_get_state, mock_message):
        """Test handling command when user already has active session."""
        # Mock existing state
        mock_get_state.return_value = {
            'user_id': 123456,
            'far_leg_ticker': 'SBER',
            'near_leg_ticker': 'SRZ4',
            'current_step': 'direction_selection'
        }
        
        await handle_addspread_command(mock_message)
        
        # Verify existing state was replaced
        mock_save_state.assert_called_once()
        call_args = mock_save_state.call_args
        user_id, state_data = call_args[0]
        
        assert user_id == 123456
        assert state_data['far_leg_ticker'] == 'GAZP'  # New tickers
        assert state_data['near_leg_ticker'] == 'GZZ4'
        
        # Verify response mentions session restart
        mock_message.answer.assert_called_once()
        response_text = mock_message.answer.call_args[0][0]
        assert "Starting spread creation" in response_text
    
    @patch('bot.spread_creator.save_state')
    @pytest.mark.asyncio
    async def test_handle_uppercase_conversion(self, mock_save_state, mock_message):
        """Test that tickers are converted to uppercase."""
        mock_message.get_args.return_value = "gazp gzz4"
        
        await handle_addspread_command(mock_message)
        
        # Verify tickers were converted to uppercase
        call_args = mock_save_state.call_args
        user_id, state_data = call_args[0]
        
        assert state_data['far_leg_ticker'] == 'GAZP'
        assert state_data['near_leg_ticker'] == 'GZZ4'