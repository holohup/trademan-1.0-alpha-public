"""
Spread creation state management module.

This module provides state management for tracking spread creation sessions
across multiple user interactions in the Telegram bot.
"""

import time
from typing import Dict, Optional, Any


class SpreadCreationState:
    """
    Represents the state of a spread creation session.
    
    Tracks all necessary information for creating a spread through
    the interactive menu system.
    """
    
    def __init__(
        self,
        user_id: int,
        far_leg_ticker: str,
        near_leg_ticker: str,
        far_leg_data: Optional[Dict[str, Any]] = None,
        near_leg_data: Optional[Dict[str, Any]] = None,
        direction: Optional[str] = None,
        custom_price: Optional[int] = None,
        amount: Optional[int] = None,
        current_step: str = 'ticker_validation'
    ):
        """
        Initialize spread creation state.
        
        Args:
            user_id: Telegram user ID
            far_leg_ticker: Ticker symbol for far leg
            near_leg_ticker: Ticker symbol for near leg
            far_leg_data: Validated ticker data for far leg
            near_leg_data: Validated ticker data for near leg
            direction: 'buy' or 'sell' spread direction
            custom_price: Custom spread price in integer format
            amount: Trade amount
            current_step: Current step in creation process
        """
        self.user_id = user_id
        self.far_leg_ticker = far_leg_ticker
        self.near_leg_ticker = near_leg_ticker
        self.far_leg_data = far_leg_data
        self.near_leg_data = near_leg_data
        self.direction = direction
        self.custom_price = custom_price
        self.amount = amount
        self.current_step = current_step
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert state to dictionary for storage.
        
        Returns:
            Dictionary representation of the state
        """
        return {
            'user_id': self.user_id,
            'far_leg_ticker': self.far_leg_ticker,
            'near_leg_ticker': self.near_leg_ticker,
            'far_leg_data': self.far_leg_data,
            'near_leg_data': self.near_leg_data,
            'direction': self.direction,
            'custom_price': self.custom_price,
            'amount': self.amount,
            'current_step': self.current_step
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SpreadCreationState':
        """
        Create state instance from dictionary.
        
        Args:
            data: Dictionary containing state data
            
        Returns:
            SpreadCreationState instance
        """
        return cls(
            user_id=data['user_id'],
            far_leg_ticker=data['far_leg_ticker'],
            near_leg_ticker=data['near_leg_ticker'],
            far_leg_data=data.get('far_leg_data'),
            near_leg_data=data.get('near_leg_data'),
            direction=data.get('direction'),
            custom_price=data.get('custom_price'),
            amount=data.get('amount'),
            current_step=data.get('current_step', 'ticker_validation')
        )


# In-memory state storage with timestamps for cleanup
# Format: {user_id: {'state': state_dict, 'timestamp': float}}
_state_storage: Dict[int, Dict[str, Any]] = {}


def save_state(user_id: int, state_data: Dict[str, Any]) -> None:
    """
    Save spread creation state for a user.
    
    Args:
        user_id: Telegram user ID
        state_data: State data dictionary
    """
    _state_storage[user_id] = {
        'state': state_data,
        'timestamp': time.time()
    }


def get_state(user_id: int) -> Optional[Dict[str, Any]]:
    """
    Retrieve spread creation state for a user.
    
    Args:
        user_id: Telegram user ID
        
    Returns:
        State data dictionary or None if not found
    """
    stored_data = _state_storage.get(user_id)
    if stored_data:
        return stored_data['state']
    return None


def clear_state(user_id: int) -> None:
    """
    Clear spread creation state for a user.
    
    Args:
        user_id: Telegram user ID
    """
    _state_storage.pop(user_id, None)


def update_state(user_id: int, updates: Dict[str, Any]) -> None:
    """
    Update specific fields in user's spread creation state.
    
    Args:
        user_id: Telegram user ID
        updates: Dictionary of fields to update
    """
    current_state = get_state(user_id)
    if current_state:
        current_state.update(updates)
        save_state(user_id, current_state)
    else:
        # Create new state if none exists
        save_state(user_id, updates)


def cleanup_stale_sessions(max_age_seconds: int = 1800) -> int:
    """
    Clean up stale spread creation sessions.
    
    Args:
        max_age_seconds: Maximum age in seconds (default: 30 minutes)
        
    Returns:
        Number of sessions cleaned up
    """
    current_time = time.time()
    stale_users = []
    
    for user_id, stored_data in _state_storage.items():
        if current_time - stored_data['timestamp'] > max_age_seconds:
            stale_users.append(user_id)
    
    for user_id in stale_users:
        clear_state(user_id)
    
    return len(stale_users)


def get_active_sessions_count() -> int:
    """
    Get the number of active spread creation sessions.
    
    Returns:
        Number of active sessions
    """
    return len(_state_storage)