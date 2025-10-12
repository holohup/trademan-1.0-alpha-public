"""
Tests for spread creation callback query handlers.

This module tests the callback query handling and state transitions
in the spread creation process.
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from aiogram.types import CallbackQuery, User, Chat, Message

# Import the module we're testing
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../bot'))

from spread_creator import (
    handle_spread_callback,
    process_direction_callback,
    process_price_callback,
    process_amount_callback,
    process_confirmation_callback,
    process_navigation_callback
)


class TestHandleSpreadCallback:
    """Test main callback query handler."""
    
    @pytest.fixture
    def mock_callback_query(self):
        """Create a mock callback query."""
        user = Mock(spec=User)
        user.id = 12345
        
        chat = Mock(spec=Chat)
        chat.id = 67890
        
        message = Mock(spec=Message)
        message.chat = chat
        message.message_id = 100
        
        callback = Mock(spec=CallbackQuery)
        callback.from_user = user
        callback.message = message
        callback.data = "direction:buy"
        callback.answer = AsyncMock()
        
        return callback
    
    @pytest.mark.asyncio
    async def test_routes_direction_callback(self, mock_callback_query):
        """Test that direction callbacks are routed correctly."""
        mock_callback_query.data = "direction:buy"
        
        with patch('spread_creator.process_direction_callback') as mock_process:
            mock_process.return_value = AsyncMock()
            await handle_spread_callback(mock_callback_query)
            mock_process.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_routes_price_callback(self, mock_callback_query):
        """Test that price callbacks are routed correctly."""
        mock_callback_query.data = "price:market:150"
        
        with patch('spread_creator.process_price_callback') as mock_process:
            mock_process.return_value = AsyncMock()
            await handle_spread_callback(mock_callback_query)
            mock_process.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_routes_amount_callback(self, mock_callback_query):
        """Test that amount callbacks are routed correctly."""
        mock_callback_query.data = "amount:input"
        
        with patch('spread_creator.process_amount_callback') as mock_process:
            mock_process.return_value = AsyncMock()
            await handle_spread_callback(mock_callback_query)
            mock_process.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_routes_confirmation_callback(self, mock_callback_query):
        """Test that confirmation callbacks are routed correctly."""
        mock_callback_query.data = "confirm:create"
        
        with patch('spread_creator.process_confirmation_callback') as mock_process:
            mock_process.return_value = AsyncMock()
            await handle_spread_callback(mock_callback_query)
            mock_process.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_routes_navigation_callback(self, mock_callback_query):
        """Test that navigation callbacks are routed correctly."""
        mock_callback_query.data = "action:back"
        
        with patch('spread_creator.process_navigation_callback') as mock_process:
            mock_process.return_value = AsyncMock()
            await handle_spread_callback(mock_callback_query)
            mock_process.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_handles_invalid_callback_data(self, mock_callback_query):
        """Test handling of invalid callback data."""
        mock_callback_query.data = "invalid:data:format"
        
        with patch('spread_creator.get_state') as mock_get_state:
            mock_get_state.return_value = {'current_step': 'direction_selection'}
            
            # Should not raise exception
            await handle_spread_callback(mock_callback_query)
            mock_callback_query.answer.assert_called()


class TestProcessDirectionCallback:
    """Test direction selection callback processing."""
    
    @pytest.fixture
    def mock_state(self):
        """Create a mock state."""
        return {
            'user_id': 12345,
            'far_leg_ticker': 'GAZP',
            'near_leg_ticker': 'GZZ4',
            'current_step': 'direction_selection'
        }
    
    @pytest.mark.asyncio
    async def test_processes_buy_direction(self, mock_state):
        """Test processing buy direction selection."""
        callback_query = Mock()
        callback_query.from_user.id = 12345
        callback_query.data = "direction:buy"
        callback_query.answer = AsyncMock()
        callback_query.message.edit_text = AsyncMock()
        callback_query.message.edit_reply_markup = AsyncMock()
        
        with patch('spread_creator.get_state', return_value=mock_state), \
             patch('spread_creator.update_state') as mock_update, \
             patch('spread_creator.calculate_spread_price') as mock_calc:
            
            mock_calc.return_value = (150, 145)  # buy_price, sell_price
            
            await process_direction_callback(callback_query, "buy")
            
            # Should update state with direction and prices
            mock_update.assert_called()
            call_args = mock_update.call_args[0]
            assert call_args[0] == 12345  # user_id
            assert 'direction' in call_args[1]
            assert call_args[1]['direction'] == 'buy'
    
    @pytest.mark.asyncio
    async def test_processes_sell_direction(self, mock_state):
        """Test processing sell direction selection."""
        callback_query = Mock()
        callback_query.from_user.id = 12345
        callback_query.data = "direction:sell"
        callback_query.answer = AsyncMock()
        callback_query.message.edit_text = AsyncMock()
        callback_query.message.edit_reply_markup = AsyncMock()
        
        with patch('spread_creator.get_state', return_value=mock_state), \
             patch('spread_creator.update_state') as mock_update, \
             patch('spread_creator.calculate_spread_price') as mock_calc:
            
            mock_calc.return_value = (150, 145)  # buy_price, sell_price
            
            await process_direction_callback(callback_query, "sell")
            
            # Should update state with direction
            mock_update.assert_called()
            call_args = mock_update.call_args[0]
            assert call_args[1]['direction'] == 'sell'
    
    @pytest.mark.asyncio
    async def test_handles_missing_state(self):
        """Test handling when user state is missing."""
        callback_query = Mock()
        callback_query.from_user.id = 12345
        callback_query.answer = AsyncMock()
        callback_query.message.edit_text = AsyncMock()
        
        with patch('spread_creator.get_state', return_value=None):
            await process_direction_callback(callback_query, "buy")
            
            # Should send error message
            callback_query.message.edit_text.assert_called()
            call_args = callback_query.message.edit_text.call_args[0]
            assert 'expired' in call_args[0].lower() or 'error' in call_args[0].lower()


class TestProcessPriceCallback:
    """Test price selection callback processing."""
    
    @pytest.fixture
    def mock_state_with_direction(self):
        """Create a mock state with direction selected."""
        return {
            'user_id': 12345,
            'far_leg_ticker': 'GAZP',
            'near_leg_ticker': 'GZZ4',
            'direction': 'buy',
            'market_neutral_buy_price': 150,
            'market_neutral_sell_price': 145,
            'current_step': 'price_input'
        }
    
    @pytest.mark.asyncio
    async def test_processes_market_price_selection(self, mock_state_with_direction):
        """Test processing market price selection."""
        callback_query = Mock()
        callback_query.from_user.id = 12345
        callback_query.data = "price:market:150"
        callback_query.answer = AsyncMock()
        callback_query.message.edit_text = AsyncMock()
        callback_query.message.edit_reply_markup = AsyncMock()
        
        with patch('spread_creator.get_state', return_value=mock_state_with_direction), \
             patch('spread_creator.update_state') as mock_update:
            
            await process_price_callback(callback_query, "market", "150")
            
            # Should update state with custom price
            mock_update.assert_called()
            call_args = mock_update.call_args[0]
            assert 'custom_price' in call_args[1]
            assert call_args[1]['custom_price'] == 150
    
    @pytest.mark.asyncio
    async def test_processes_custom_price_request(self, mock_state_with_direction):
        """Test processing custom price input request."""
        callback_query = Mock()
        callback_query.from_user.id = 12345
        callback_query.data = "price:custom"
        callback_query.answer = AsyncMock()
        callback_query.message.edit_text = AsyncMock()
        
        with patch('spread_creator.get_state', return_value=mock_state_with_direction), \
             patch('spread_creator.update_state') as mock_update:
            
            await process_price_callback(callback_query, "custom", None)
            
            # Should update state to wait for custom input
            mock_update.assert_called()
            call_args = mock_update.call_args[0]
            assert 'current_step' in call_args[1]
            assert call_args[1]['current_step'] == 'custom_price_input'


class TestProcessAmountCallback:
    """Test amount selection callback processing."""
    
    @pytest.fixture
    def mock_state_with_price(self):
        """Create a mock state with price selected."""
        return {
            'user_id': 12345,
            'far_leg_ticker': 'GAZP',
            'near_leg_ticker': 'GZZ4',
            'direction': 'buy',
            'custom_price': 150,
            'current_step': 'amount_input'
        }
    
    @pytest.mark.asyncio
    async def test_processes_amount_input_request(self, mock_state_with_price):
        """Test processing amount input request."""
        callback_query = Mock()
        callback_query.from_user.id = 12345
        callback_query.data = "amount:input"
        callback_query.answer = AsyncMock()
        callback_query.message.edit_text = AsyncMock()
        
        with patch('spread_creator.get_state', return_value=mock_state_with_price), \
             patch('spread_creator.update_state') as mock_update:
            
            await process_amount_callback(callback_query, "input", None)
            
            # Should update state to wait for amount input
            mock_update.assert_called()
            call_args = mock_update.call_args[0]
            assert 'current_step' in call_args[1]
            assert call_args[1]['current_step'] == 'custom_amount_input'


class TestProcessConfirmationCallback:
    """Test confirmation callback processing."""
    
    @pytest.fixture
    def mock_complete_state(self):
        """Create a mock state ready for confirmation."""
        return {
            'user_id': 12345,
            'far_leg_ticker': 'GAZP',
            'near_leg_ticker': 'GZZ4',
            'far_leg_data': {'figi': 'BBG004730N88'},
            'near_leg_data': {'figi': 'BBG004730N89'},
            'direction': 'buy',
            'custom_price': 150,
            'amount': 5,
            'current_step': 'confirmation'
        }
    
    @pytest.mark.asyncio
    async def test_processes_spread_creation(self, mock_complete_state):
        """Test processing spread creation confirmation."""
        callback_query = Mock()
        callback_query.from_user.id = 12345
        callback_query.data = "confirm:create"
        callback_query.answer = AsyncMock()
        callback_query.message.edit_text = AsyncMock()
        
        with patch('spread_creator.get_state', return_value=mock_complete_state), \
             patch('spread_creator.create_spread_in_database') as mock_create, \
             patch('spread_creator.clear_state') as mock_clear:
            
            mock_create.return_value = {'id': 123, 'success': True}
            
            await process_confirmation_callback(callback_query, "create", None)
            
            # Should create spread and clear state
            mock_create.assert_called_once()
            mock_clear.assert_called_once_with(12345)


class TestProcessNavigationCallback:
    """Test navigation callback processing."""
    
    @pytest.mark.asyncio
    async def test_processes_back_navigation(self):
        """Test processing back navigation."""
        callback_query = Mock()
        callback_query.from_user.id = 12345
        callback_query.data = "action:back"
        callback_query.answer = AsyncMock()
        callback_query.message.edit_text = AsyncMock()
        
        state = {
            'current_step': 'price_input',
            'direction': 'buy'
        }
        
        with patch('spread_creator.get_state', return_value=state), \
             patch('spread_creator.update_state') as mock_update:
            
            await process_navigation_callback(callback_query, "back", None)
            
            # Should update to previous step
            mock_update.assert_called()
    
    @pytest.mark.asyncio
    async def test_processes_cancel_navigation(self):
        """Test processing cancel navigation."""
        callback_query = Mock()
        callback_query.from_user.id = 12345
        callback_query.data = "action:cancel"
        callback_query.answer = AsyncMock()
        callback_query.message.edit_text = AsyncMock()
        
        with patch('spread_creator.clear_state') as mock_clear:
            await process_navigation_callback(callback_query, "cancel", None)
            
            # Should clear state
            mock_clear.assert_called_once_with(12345)