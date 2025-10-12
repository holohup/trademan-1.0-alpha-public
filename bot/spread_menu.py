"""
Spread menu generation module.

This module provides inline keyboard menu generators for each step
of the spread creation process in the Telegram bot.
"""

from typing import Dict, Any, Optional
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def generate_direction_menu(state: Dict[str, Any]) -> InlineKeyboardMarkup:
    """
    Generate inline keyboard for spread direction selection.
    
    Creates a menu with Buy Spread and Sell Spread options, along with
    navigation buttons.
    
    Args:
        state: Current spread creation state
        
    Returns:
        InlineKeyboardMarkup with direction selection options
    """
    keyboard = InlineKeyboardMarkup(row_width=2)
    
    # Main direction buttons
    buy_button = InlineKeyboardButton(
        text="📈 Buy Spread",
        callback_data="direction:buy"
    )
    sell_button = InlineKeyboardButton(
        text="📉 Sell Spread", 
        callback_data="direction:sell"
    )
    
    keyboard.row(buy_button, sell_button)
    
    # Navigation buttons
    cancel_button = InlineKeyboardButton(
        text="❌ Cancel",
        callback_data="action:cancel"
    )
    
    keyboard.row(cancel_button)
    
    return keyboard


def generate_price_menu(state: Dict[str, Any]) -> InlineKeyboardMarkup:
    """
    Generate inline keyboard for price selection.
    
    Shows market-neutral prices and allows custom price input.
    
    Args:
        state: Current spread creation state
        
    Returns:
        InlineKeyboardMarkup with price selection options
    """
    keyboard = InlineKeyboardMarkup(row_width=1)
    
    direction = state.get('direction', 'buy')
    
    # Market-neutral price buttons
    if direction == 'buy':
        market_price = state.get('market_neutral_buy_price')
        if market_price is not None:
            market_button = InlineKeyboardButton(
                text=f"💰 Use Market Price: {market_price}",
                callback_data=f"price:market:{market_price}"
            )
            keyboard.row(market_button)
    else:  # sell
        market_price = state.get('market_neutral_sell_price')
        if market_price is not None:
            market_button = InlineKeyboardButton(
                text=f"💰 Use Market Price: {market_price}",
                callback_data=f"price:market:{market_price}"
            )
            keyboard.row(market_button)
    
    # Custom price input button
    custom_button = InlineKeyboardButton(
        text="✏️ Enter Custom Price",
        callback_data="price:custom"
    )
    keyboard.row(custom_button)
    
    # Navigation buttons
    back_button = InlineKeyboardButton(
        text="⬅️ Back",
        callback_data="action:back"
    )
    cancel_button = InlineKeyboardButton(
        text="❌ Cancel",
        callback_data="action:cancel"
    )
    
    keyboard.row(back_button, cancel_button)
    
    return keyboard


def generate_amount_menu(state: Dict[str, Any]) -> InlineKeyboardMarkup:
    """
    Generate inline keyboard for amount selection.
    
    Shows lot size information and allows amount input.
    
    Args:
        state: Current spread creation state
        
    Returns:
        InlineKeyboardMarkup with amount selection options
    """
    keyboard = InlineKeyboardMarkup(row_width=1)
    
    # Get lot size information
    far_leg_data = state.get('far_leg_data', {})
    near_leg_data = state.get('near_leg_data', {})
    
    far_lot = far_leg_data.get('lot', 1)
    near_lot = near_leg_data.get('lot', 1)
    
    # Show minimum lot information
    min_lot = max(far_lot, near_lot)
    lot_info_button = InlineKeyboardButton(
        text=f"ℹ️ Minimum lot: {min_lot}",
        callback_data="info:lot"
    )
    keyboard.row(lot_info_button)
    
    # Amount input button
    amount_button = InlineKeyboardButton(
        text="🔢 Enter Amount",
        callback_data="amount:input"
    )
    keyboard.row(amount_button)
    
    # Navigation buttons
    back_button = InlineKeyboardButton(
        text="⬅️ Back",
        callback_data="action:back"
    )
    cancel_button = InlineKeyboardButton(
        text="❌ Cancel",
        callback_data="action:cancel"
    )
    
    keyboard.row(back_button, cancel_button)
    
    return keyboard


def generate_confirmation_menu(state: Dict[str, Any]) -> InlineKeyboardMarkup:
    """
    Generate inline keyboard for final confirmation.
    
    Shows confirm and cancel options for spread creation.
    
    Args:
        state: Current spread creation state
        
    Returns:
        InlineKeyboardMarkup with confirmation options
    """
    keyboard = InlineKeyboardMarkup(row_width=2)
    
    # Main confirmation buttons
    confirm_button = InlineKeyboardButton(
        text="✅ Confirm & Create",
        callback_data="confirm:create"
    )
    back_button = InlineKeyboardButton(
        text="⬅️ Back to Edit",
        callback_data="action:back"
    )
    
    keyboard.row(confirm_button)
    keyboard.row(back_button)
    
    # Cancel button
    cancel_button = InlineKeyboardButton(
        text="❌ Cancel",
        callback_data="action:cancel"
    )
    keyboard.row(cancel_button)
    
    return keyboard


def format_spread_summary(state: Dict[str, Any]) -> str:
    """
    Format spread summary text for confirmation display.
    
    Args:
        state: Current spread creation state
        
    Returns:
        Formatted summary string
    """
    far_leg = state.get('far_leg_ticker', 'N/A')
    near_leg = state.get('near_leg_ticker', 'N/A')
    direction = state.get('direction', 'N/A')
    price = state.get('custom_price', 'N/A')
    amount = state.get('amount', 'N/A')
    
    far_leg_data = state.get('far_leg_data', {})
    near_leg_data = state.get('near_leg_data', {})
    
    far_name = far_leg_data.get('name', far_leg)
    near_name = near_leg_data.get('name', near_leg)
    
    ratio = state.get('calculated_ratio', 1)
    
    summary = f"📋 **Spread Summary**\n\n"
    summary += f"**Far Leg:** {far_leg} ({far_name})\n"
    summary += f"**Near Leg:** {near_leg} ({near_name})\n"
    summary += f"**Direction:** {direction.title()} Spread\n"
    summary += f"**Price:** {price}\n"
    summary += f"**Amount:** {amount}\n"
    summary += f"**Ratio:** 1:{ratio}\n\n"
    
    # Add market-neutral explanation
    if direction == 'buy':
        summary += f"**Action:** Buy {amount} of {far_leg}, Sell {amount * ratio} of {near_leg}\n"
    else:
        summary += f"**Action:** Sell {amount} of {far_leg}, Buy {amount * ratio} of {near_leg}\n"
    
    summary += "\n⚠️ This will create a market-neutral position."
    
    return summary


def format_direction_message(state: Dict[str, Any]) -> str:
    """
    Format message text for direction selection step.
    
    Args:
        state: Current spread creation state
        
    Returns:
        Formatted message string
    """
    far_leg = state.get('far_leg_ticker', 'N/A')
    near_leg = state.get('near_leg_ticker', 'N/A')
    
    far_leg_data = state.get('far_leg_data', {})
    near_leg_data = state.get('near_leg_data', {})
    
    message = f"🎯 **Spread Direction Selection**\n\n"
    message += f"**Far Leg:** {far_leg}"
    if far_leg_data.get('name'):
        message += f" ({far_leg_data['name']})"
    message += "\n"
    
    message += f"**Near Leg:** {near_leg}"
    if near_leg_data.get('name'):
        message += f" ({near_leg_data['name']})"
    message += "\n\n"
    
    message += "Choose your spread direction:\n"
    message += "• **Buy Spread**: Buy far leg, sell near leg\n"
    message += "• **Sell Spread**: Sell far leg, buy near leg"
    
    return message


def format_price_message(state: Dict[str, Any]) -> str:
    """
    Format message text for price selection step.
    
    Args:
        state: Current spread creation state
        
    Returns:
        Formatted message string
    """
    direction = state.get('direction', 'buy')
    far_leg = state.get('far_leg_ticker', 'N/A')
    near_leg = state.get('near_leg_ticker', 'N/A')
    
    message = f"💰 **Price Selection**\n\n"
    message += f"**Spread:** {far_leg} / {near_leg}\n"
    message += f"**Direction:** {direction.title()} Spread\n\n"
    
    # Show current market prices if available
    if direction == 'buy':
        market_price = state.get('market_neutral_buy_price')
        if market_price is not None:
            message += f"**Current Market-Neutral Buy Price:** {market_price}\n\n"
    else:
        market_price = state.get('market_neutral_sell_price')
        if market_price is not None:
            message += f"**Current Market-Neutral Sell Price:** {market_price}\n\n"
    
    message += "Choose your price option:"
    
    return message


def format_amount_message(state: Dict[str, Any]) -> str:
    """
    Format message text for amount selection step.
    
    Args:
        state: Current spread creation state
        
    Returns:
        Formatted message string
    """
    direction = state.get('direction', 'buy')
    price = state.get('custom_price', 'N/A')
    far_leg = state.get('far_leg_ticker', 'N/A')
    near_leg = state.get('near_leg_ticker', 'N/A')
    
    far_leg_data = state.get('far_leg_data', {})
    near_leg_data = state.get('near_leg_data', {})
    
    message = f"🔢 **Amount Selection**\n\n"
    message += f"**Spread:** {far_leg} / {near_leg}\n"
    message += f"**Direction:** {direction.title()} Spread\n"
    message += f"**Price:** {price}\n\n"
    
    # Show lot size requirements
    far_lot = far_leg_data.get('lot', 1)
    near_lot = near_leg_data.get('lot', 1)
    
    message += f"**Lot Sizes:**\n"
    message += f"• {far_leg}: {far_lot}\n"
    message += f"• {near_leg}: {near_lot}\n\n"
    
    min_lot = max(far_lot, near_lot)
    message += f"**Minimum amount:** {min_lot}\n\n"
    message += "Enter the amount you want to trade:"
    
    return message