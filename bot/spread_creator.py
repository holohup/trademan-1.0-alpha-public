"""
Spread creator module for handling /addspread command.

This module provides the main command handler for initiating spread creation
through the Telegram bot interface.
"""

from typing import Optional, Tuple
from aiogram import types
from spread_state import SpreadCreationState, save_state, get_state


def parse_addspread_command(args: str) -> Optional[Tuple[str, str]]:
    """
    Parse the addspread command arguments.
    
    Args:
        args: Command arguments string
        
    Returns:
        Tuple of (far_leg_ticker, near_leg_ticker) or None if invalid
    """
    if not args or not args.strip():
        return None
    
    # Split and clean up arguments
    tickers = args.strip().split()
    
    # Must have exactly 2 tickers
    if len(tickers) != 2:
        return None
    
    far_leg, near_leg = tickers[0].upper(), tickers[1].upper()
    return (far_leg, near_leg)


def validate_command_format(
    far_leg: Optional[str], near_leg: Optional[str]
) -> bool:
    """
    Validate the command format and ticker values.
    
    Args:
        far_leg: Far leg ticker symbol
        near_leg: Near leg ticker symbol
        
    Returns:
        True if valid, False otherwise
    """
    # Check for None or empty values
    if not far_leg or not near_leg:
        return False
    
    # Check for empty strings after stripping
    if not far_leg.strip() or not near_leg.strip():
        return False
    
    # Check that tickers are different (case insensitive)
    if far_leg.upper() == near_leg.upper():
        return False
    
    return True


async def handle_addspread_command(message: types.Message) -> None:
    """
    Handle the /addspread command.
    
    Parses the command arguments, validates the format, and initiates
    the spread creation process by saving initial state.
    
    Args:
        message: Telegram message containing the command
    """
    user_id = message.from_user.id
    args = message.get_args()
    
    # Parse command arguments
    parsed_tickers = parse_addspread_command(args)
    
    if not parsed_tickers:
        await message.answer(
            "Usage: /addspread <far_leg_ticker> <near_leg_ticker>\n"
            "Example: /addspread GAZP GZZ4"
        )
        return
    
    far_leg_ticker, near_leg_ticker = parsed_tickers
    
    # Validate ticker format
    if not validate_command_format(far_leg_ticker, near_leg_ticker):
        await message.answer(
            "Usage: /addspread <far_leg_ticker> <near_leg_ticker>\n"
            "Example: /addspread GAZP GZZ4\n"
            "Note: Tickers must be different"
        )
        return
    
    # Check if user already has an active session
    existing_state = get_state(user_id)
    if existing_state:
        # Replace existing session with new one
        pass  # Will be overwritten below
    
    # Create initial state
    initial_state = SpreadCreationState(
        user_id=user_id,
        far_leg_ticker=far_leg_ticker,
        near_leg_ticker=near_leg_ticker,
        current_step='ticker_validation'
    )
    
    # Save state
    save_state(user_id, initial_state.to_dict())
    
    # Send confirmation message
    await message.answer(
        f"Starting spread creation process:\n"
        f"Far leg: {far_leg_ticker}\n"
        f"Near leg: {near_leg_ticker}\n\n"
        f"Validating tickers..."
    )