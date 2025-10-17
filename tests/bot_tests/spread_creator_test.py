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


class TestCreateSpreadInDatabase:
    """Test spread creation in database functionality."""
    
    @pytest.mark.asyncio
    async def test_create_spread_payload_generation(self):
        """Test correct payload generation for spread creation."""
        state = {
            'user_id': 12345,
            'far_leg_data': {'figi': 'BBG004730N88'},
            'near_leg_data': {'figi': 'BBG00475KKY8'},
            'direction': 'sell',
            'custom_price': 150,
            'amount': 10
        }
        
        with patch('bot.spread_creator.create_spread') as mock_create:
            mock_create.return_value = 123
            
            from bot.spread_creator import create_spread_in_database
            result = await create_spread_in_database(state)
            
            # Verify API was called with correct payload
            mock_create.assert_called_once()
            call_args = mock_create.call_args[0][0]
            
            assert call_args['far_leg_figi'] == 'BBG004730N88'
            assert call_args['near_leg_figi'] == 'BBG00475KKY8'
            assert call_args['sell'] is True
            assert call_args['price'] == 150
            assert call_args['amount'] == 10
            assert 'editable_ratio' not in call_args
            
            # Verify return format
            assert result['success'] is True
            assert result['id'] == 123
    
    @pytest.mark.asyncio
    async def test_create_spread_with_custom_ratio(self):
        """Test spread creation with custom ratio."""
        state = {
            'user_id': 12345,
            'far_leg_data': {'figi': 'BBG004730N88'},
            'near_leg_data': {'figi': 'BBG00475KKY8'},
            'direction': 'buy',
            'custom_price': 200,
            'amount': 5,
            'calculated_ratio': 150
        }
        
        with patch('bot.spread_creator.create_spread') as mock_create:
            mock_create.return_value = 124
            
            from bot.spread_creator import create_spread_in_database
            result = await create_spread_in_database(state)
            
            # Verify API was called with ratio
            call_args = mock_create.call_args[0][0]
            assert call_args['editable_ratio'] == 150
            assert call_args['sell'] is False  # buy direction
            
            assert result['success'] is True
            assert result['id'] == 124
    
    @pytest.mark.asyncio
    async def test_create_spread_api_error(self):
        """Test handling of API errors during spread creation."""
        state = {
            'user_id': 12345,
            'far_leg_data': {'figi': 'BBG004730N88'},
            'near_leg_data': {'figi': 'BBG00475KKY8'},
            'direction': 'sell',
            'custom_price': 150,
            'amount': 10
        }
        
        with patch('bot.spread_creator.create_spread') as mock_create:
            mock_create.side_effect = Exception("API connection failed")
            
            from bot.spread_creator import create_spread_in_database
            result = await create_spread_in_database(state)
            
            # Verify error handling
            assert result['success'] is False
            assert "API connection failed" in result['error']
    
    @pytest.mark.asyncio
    async def test_create_spread_missing_data(self):
        """Test handling of missing data in state."""
        state = {
            'far_leg_data': {'figi': 'BBG004730N88'},
            # Missing near_leg_data
            'direction': 'sell',
            'custom_price': 150,
            'amount': 10
        }
        
        from bot.spread_creator import create_spread_in_database
        result = await create_spread_in_database(state)
        
        # Verify error handling for missing data
        assert result['success'] is False
        assert 'error' in result


class TestSpreadActivationAndConfirmation:
    """Test spread activation and confirmation flow."""
    
    @pytest.fixture
    def mock_callback_query(self):
        """Create a mock callback query."""
        callback = MagicMock(spec=types.CallbackQuery)
        callback.from_user.id = 123456
        callback.data = "confirm:create"
        callback.answer = AsyncMock()
        callback.message.edit_text = AsyncMock()
        return callback
    
    @pytest.fixture
    def complete_state(self):
        """Create a complete spread creation state."""
        return {
            'user_id': 123456,
            'far_leg_ticker': 'GAZP',
            'near_leg_ticker': 'GZZ4',
            'far_leg_data': {'figi': 'BBG004730N88'},
            'near_leg_data': {'figi': 'BBG00475KKY8'},
            'direction': 'sell',
            'custom_price': 150,
            'amount': 10,
            'current_step': 'confirmation'
        }
    
    @patch('bot.spread_creator.get_state')
    @patch('bot.spread_creator.clear_state')
    @patch('bot.spread_creator.create_spread_in_database')
    @pytest.mark.asyncio
    async def test_successful_spread_creation_and_activation(
        self, mock_create_spread, mock_clear_state, mock_get_state, 
        mock_callback_query, complete_state
    ):
        """Test successful spread creation with activation and confirmation."""
        # Mock successful creation
        mock_get_state.return_value = complete_state
        mock_create_spread.return_value = {'success': True, 'id': 123}
        
        from bot.spread_creator import process_confirmation_callback
        await process_confirmation_callback(mock_callback_query, 'create', None)
        
        # Verify spread creation was called
        mock_create_spread.assert_called_once_with(complete_state)
        
        # Verify success message
        mock_callback_query.message.edit_text.assert_called_once()
        call_args = mock_callback_query.message.edit_text.call_args
        # Handle both positional and keyword arguments
        if call_args[1] and 'text' in call_args[1]:
            success_message = call_args[1]['text']
        else:
            success_message = call_args[0][0]
        
        assert "✅ **Spread Created Successfully!**" in success_message
        assert "**Spread ID:** 123" in success_message
        assert "**Far Leg:** GAZP" in success_message
        assert "**Near Leg:** GZZ4" in success_message
        assert "**Direction:** Sell" in success_message
        assert "**Price:** 150" in success_message
        assert "**Amount:** 10" in success_message
        assert "The spread is now active and available for trading" in success_message
        
        # Verify session was cleared
        mock_clear_state.assert_called_once_with(123456)
    
    @patch('bot.spread_creator.get_state')
    @patch('bot.spread_creator.create_spread_in_database')
    @pytest.mark.asyncio
    async def test_spread_creation_failure(
        self, mock_create_spread, mock_get_state, 
        mock_callback_query, complete_state
    ):
        """Test handling of spread creation failure."""
        # Mock failed creation
        mock_get_state.return_value = complete_state
        mock_create_spread.return_value = {
            'success': False, 
            'error': 'Database connection failed'
        }
        
        from bot.spread_creator import process_confirmation_callback
        await process_confirmation_callback(mock_callback_query, 'create', None)
        
        # Verify error message
        mock_callback_query.message.edit_text.assert_called_once()
        call_args = mock_callback_query.message.edit_text.call_args
        # Handle both positional and keyword arguments
        if call_args[1] and 'text' in call_args[1]:
            error_message = call_args[1]['text']
        else:
            error_message = call_args[0][0]
        
        assert "❌ **Failed to Create Spread**" in error_message
        assert "Database connection failed" in error_message
        assert "Please try again with /addspread" in error_message
    
    @patch('bot.spread_creator.get_state')
    @patch('bot.spread_creator.create_spread_in_database')
    @pytest.mark.asyncio
    async def test_spread_creation_exception(
        self, mock_create_spread, mock_get_state, 
        mock_callback_query, complete_state
    ):
        """Test handling of exceptions during spread creation."""
        # Mock exception during creation
        mock_get_state.return_value = complete_state
        mock_create_spread.side_effect = Exception("Unexpected error")
        
        from bot.spread_creator import process_confirmation_callback
        await process_confirmation_callback(mock_callback_query, 'create', None)
        
        # Verify error message
        mock_callback_query.message.edit_text.assert_called_once()
        call_args = mock_callback_query.message.edit_text.call_args
        # Handle both positional and keyword arguments
        if call_args[1] and 'text' in call_args[1]:
            error_message = call_args[1]['text']
        else:
            error_message = call_args[0][0]
        
        assert "❌ **Error Creating Spread**" in error_message
        assert "Unexpected error" in error_message
        assert "Please try again with /addspread" in error_message
    
    @patch('bot.spread_creator.get_state')
    @pytest.mark.asyncio
    async def test_confirmation_with_expired_session(
        self, mock_get_state, mock_callback_query
    ):
        """Test confirmation callback with expired session."""
        # Mock expired session
        mock_get_state.return_value = None
        
        from bot.spread_creator import process_confirmation_callback
        await process_confirmation_callback(mock_callback_query, 'create', None)
        
        # Verify session expired message
        mock_callback_query.message.edit_text.assert_called_once()
        error_message = mock_callback_query.message.edit_text.call_args[0][0]
        
        assert "❌ Session expired" in error_message
        assert "Please start over with /addspread" in error_message
    
    @patch('bot.spread_creator.get_state')
    @patch('bot.spread_creator.clear_state')
    @patch('bot.spread_creator.create_spread_in_database')
    @pytest.mark.asyncio
    async def test_spread_activation_by_default(
        self, mock_create_spread, mock_clear_state, mock_get_state, 
        mock_callback_query, complete_state
    ):
        """Test that spreads are activated by default (active=True)."""
        # Mock successful creation
        mock_get_state.return_value = complete_state
        mock_create_spread.return_value = {'success': True, 'id': 456}
        
        from bot.spread_creator import process_confirmation_callback
        await process_confirmation_callback(mock_callback_query, 'create', None)
        
        # Verify the spread data sent to API includes active=True by default
        # This is handled by the Django backend, but we verify the flow works
        mock_create_spread.assert_called_once_with(complete_state)
        
        # Verify success message indicates activation
        call_args = mock_callback_query.message.edit_text.call_args
        # Handle both positional and keyword arguments
        if call_args[1] and 'text' in call_args[1]:
            success_message = call_args[1]['text']
        else:
            success_message = call_args[0][0]
        assert "The spread is now active and available for trading" in success_message
        
        # Verify session cleanup
        mock_clear_state.assert_called_once_with(123456)