import pytest
from unittest.mock import patch
from bot.spread_state import SpreadCreationState, save_state, get_state, clear_state, update_state


class TestSpreadCreationState:
    """Test the SpreadCreationState class."""
    
    def test_init_with_required_params(self):
        """Test initialization with required parameters."""
        state = SpreadCreationState(
            user_id=123,
            far_leg_ticker='GAZP',
            near_leg_ticker='GZZ4'
        )
        
        assert state.user_id == 123
        assert state.far_leg_ticker == 'GAZP'
        assert state.near_leg_ticker == 'GZZ4'
        assert state.far_leg_data is None
        assert state.near_leg_data is None
        assert state.direction is None
        assert state.custom_price is None
        assert state.amount is None
        assert state.current_step == 'ticker_validation'
    
    def test_init_with_all_params(self):
        """Test initialization with all parameters."""
        far_leg_data = {'figi': 'test_figi', 'ticker': 'GAZP'}
        near_leg_data = {'figi': 'test_figi2', 'ticker': 'GZZ4'}
        
        state = SpreadCreationState(
            user_id=456,
            far_leg_ticker='GAZP',
            near_leg_ticker='GZZ4',
            far_leg_data=far_leg_data,
            near_leg_data=near_leg_data,
            direction='buy',
            custom_price=100,
            amount=10,
            current_step='confirmation'
        )
        
        assert state.user_id == 456
        assert state.far_leg_ticker == 'GAZP'
        assert state.near_leg_ticker == 'GZZ4'
        assert state.far_leg_data == far_leg_data
        assert state.near_leg_data == near_leg_data
        assert state.direction == 'buy'
        assert state.custom_price == 100
        assert state.amount == 10
        assert state.current_step == 'confirmation'
    
    def test_to_dict(self):
        """Test conversion to dictionary."""
        state = SpreadCreationState(
            user_id=789,
            far_leg_ticker='SBER',
            near_leg_ticker='SRZ4',
            direction='sell',
            custom_price=200,
            amount=5
        )
        
        result = state.to_dict()
        expected = {
            'user_id': 789,
            'far_leg_ticker': 'SBER',
            'near_leg_ticker': 'SRZ4',
            'far_leg_data': None,
            'near_leg_data': None,
            'direction': 'sell',
            'custom_price': 200,
            'amount': 5,
            'current_step': 'ticker_validation'
        }
        
        assert result == expected
    
    def test_from_dict(self):
        """Test creation from dictionary."""
        data = {
            'user_id': 999,
            'far_leg_ticker': 'LKOH',
            'near_leg_ticker': 'LKZ4',
            'far_leg_data': {'figi': 'test'},
            'near_leg_data': {'figi': 'test2'},
            'direction': 'buy',
            'custom_price': 150,
            'amount': 20,
            'current_step': 'price_input'
        }
        
        state = SpreadCreationState.from_dict(data)
        
        assert state.user_id == 999
        assert state.far_leg_ticker == 'LKOH'
        assert state.near_leg_ticker == 'LKZ4'
        assert state.far_leg_data == {'figi': 'test'}
        assert state.near_leg_data == {'figi': 'test2'}
        assert state.direction == 'buy'
        assert state.custom_price == 150
        assert state.amount == 20
        assert state.current_step == 'price_input'


class TestStateManagement:
    """Test state management functions."""
    
    def setup_method(self):
        """Clear state storage before each test."""
        # Clear the in-memory storage
        from bot.spread_state import _state_storage
        _state_storage.clear()
    
    def test_save_and_get_state(self):
        """Test saving and retrieving state."""
        user_id = 123
        state_data = {
            'user_id': user_id,
            'far_leg_ticker': 'GAZP',
            'near_leg_ticker': 'GZZ4',
            'direction': 'buy',
            'current_step': 'direction_selection'
        }
        
        # Save state
        save_state(user_id, state_data)
        
        # Retrieve state
        retrieved_state = get_state(user_id)
        
        assert retrieved_state == state_data
    
    def test_get_nonexistent_state(self):
        """Test retrieving non-existent state returns None."""
        result = get_state(999)
        assert result is None
    
    def test_clear_state(self):
        """Test clearing state."""
        user_id = 456
        state_data = {
            'user_id': user_id,
            'far_leg_ticker': 'SBER',
            'near_leg_ticker': 'SRZ4'
        }
        
        # Save state
        save_state(user_id, state_data)
        assert get_state(user_id) == state_data
        
        # Clear state
        clear_state(user_id)
        assert get_state(user_id) is None
    
    def test_update_state(self):
        """Test updating existing state."""
        user_id = 789
        initial_state = {
            'user_id': user_id,
            'far_leg_ticker': 'LKOH',
            'near_leg_ticker': 'LKZ4',
            'direction': None,
            'current_step': 'ticker_validation'
        }
        
        # Save initial state
        save_state(user_id, initial_state)
        
        # Update state
        updates = {
            'direction': 'sell',
            'current_step': 'direction_selection'
        }
        update_state(user_id, updates)
        
        # Verify updates
        updated_state = get_state(user_id)
        assert updated_state['direction'] == 'sell'
        assert updated_state['current_step'] == 'direction_selection'
        assert updated_state['far_leg_ticker'] == 'LKOH'  # Unchanged
        assert updated_state['near_leg_ticker'] == 'LKZ4'  # Unchanged
    
    def test_update_nonexistent_state(self):
        """Test updating non-existent state creates new state."""
        user_id = 999
        updates = {
            'direction': 'buy',
            'current_step': 'direction_selection'
        }
        
        update_state(user_id, updates)
        
        # Should create new state with updates
        state = get_state(user_id)
        assert state == updates
    
    def test_multiple_users_state_isolation(self):
        """Test that different users have isolated states."""
        user1_id = 111
        user2_id = 222
        
        state1 = {
            'user_id': user1_id,
            'far_leg_ticker': 'GAZP',
            'direction': 'buy'
        }
        
        state2 = {
            'user_id': user2_id,
            'far_leg_ticker': 'SBER',
            'direction': 'sell'
        }
        
        # Save states for different users
        save_state(user1_id, state1)
        save_state(user2_id, state2)
        
        # Verify isolation
        retrieved_state1 = get_state(user1_id)
        retrieved_state2 = get_state(user2_id)
        
        assert retrieved_state1 == state1
        assert retrieved_state2 == state2
        assert retrieved_state1 != retrieved_state2
    
    @patch('bot.spread_state.time.time')
    def test_state_with_timestamp(self, mock_time):
        """Test that states are saved with timestamps."""
        mock_time.return_value = 1234567890.0
        
        user_id = 333
        state_data = {
            'user_id': user_id,
            'far_leg_ticker': 'VTBR'
        }
        
        save_state(user_id, state_data)
        
        # Check internal storage includes timestamp
        from bot.spread_state import _state_storage
        stored_data = _state_storage[user_id]
        
        assert 'timestamp' in stored_data
        assert stored_data['timestamp'] == 1234567890.0
        assert stored_data['state'] == state_data