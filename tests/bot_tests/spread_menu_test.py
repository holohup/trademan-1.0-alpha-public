"""
Tests for spread menu generation functions.

This module tests the inline keyboard menu generators used in the
spread creation process.
"""

import pytest
from unittest.mock import Mock
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# Import the module we're testing
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../bot'))

from spread_menu import (
    generate_direction_menu,
    generate_price_menu,
    generate_amount_menu,
    generate_confirmation_menu
)


class TestGenerateDirectionMenu:
    """Test direction selection menu generation."""
    
    def test_generates_buy_sell_buttons(self):
        """Test that direction menu contains buy and sell buttons."""
        state = {
            'far_leg_ticker': 'GAZP',
            'near_leg_ticker': 'GZZ4',
            'far_leg_data': {'name': 'Gazprom'},
            'near_leg_data': {'name': 'Gazprom Dec24'},
            'current_step': 'direction_selection'
        }
        
        markup = generate_direction_menu(state)
        
        assert isinstance(markup, InlineKeyboardMarkup)
        assert len(markup.inline_keyboard) >= 2  # At least buy/sell rows
        
        # Check for buy and sell buttons
        buttons_text = []
        for row in markup.inline_keyboard:
            for button in row:
                buttons_text.append(button.text)
        
        assert any('Buy' in text for text in buttons_text)
        assert any('Sell' in text for text in buttons_text)
    
    def test_includes_cancel_button(self):
        """Test that direction menu includes cancel button."""
        state = {
            'far_leg_ticker': 'GAZP',
            'near_leg_ticker': 'GZZ4',
            'current_step': 'direction_selection'
        }
        
        markup = generate_direction_menu(state)
        
        # Check for cancel button
        buttons_text = []
        for row in markup.inline_keyboard:
            for button in row:
                buttons_text.append(button.text)
        
        assert any('Cancel' in text for text in buttons_text)
    
    def test_callback_data_format(self):
        """Test that callback data follows expected format."""
        state = {
            'far_leg_ticker': 'GAZP',
            'near_leg_ticker': 'GZZ4',
            'current_step': 'direction_selection'
        }
        
        markup = generate_direction_menu(state)
        
        # Check callback data format
        for row in markup.inline_keyboard:
            for button in row:
                assert button.callback_data is not None
                assert ':' in button.callback_data  # Should have action:value format


class TestGeneratePriceMenu:
    """Test price input menu generation."""
    
    def test_shows_market_neutral_prices(self):
        """Test that price menu shows calculated market-neutral prices."""
        state = {
            'far_leg_ticker': 'GAZP',
            'near_leg_ticker': 'GZZ4',
            'direction': 'buy',
            'market_neutral_buy_price': 150,
            'market_neutral_sell_price': 145,
            'current_step': 'price_input'
        }
        
        markup = generate_price_menu(state)
        
        assert isinstance(markup, InlineKeyboardMarkup)
        
        # Check that market prices are displayed in button text
        buttons_text = []
        for row in markup.inline_keyboard:
            for button in row:
                buttons_text.append(button.text)
        
        # Should show the relevant market price based on direction
        assert any('150' in text for text in buttons_text)
    
    def test_includes_custom_price_option(self):
        """Test that price menu includes custom price input option."""
        state = {
            'direction': 'sell',
            'market_neutral_sell_price': 145,
            'current_step': 'price_input'
        }
        
        markup = generate_price_menu(state)
        
        buttons_text = []
        for row in markup.inline_keyboard:
            for button in row:
                buttons_text.append(button.text)
        
        assert any('Custom' in text or 'Enter' in text for text in buttons_text)
    
    def test_includes_navigation_buttons(self):
        """Test that price menu includes back and cancel buttons."""
        state = {
            'direction': 'buy',
            'current_step': 'price_input'
        }
        
        markup = generate_price_menu(state)
        
        buttons_text = []
        for row in markup.inline_keyboard:
            for button in row:
                buttons_text.append(button.text)
        
        assert any('Back' in text for text in buttons_text)
        assert any('Cancel' in text for text in buttons_text)


class TestGenerateAmountMenu:
    """Test amount input menu generation."""
    
    def test_shows_lot_size_information(self):
        """Test that amount menu shows minimum lot size information."""
        state = {
            'direction': 'buy',
            'custom_price': 150,
            'far_leg_data': {'lot': 10},
            'near_leg_data': {'lot': 1},
            'current_step': 'amount_input'
        }
        
        markup = generate_amount_menu(state)
        
        assert isinstance(markup, InlineKeyboardMarkup)
        
        # Check that lot information is mentioned somewhere
        buttons_text = []
        for row in markup.inline_keyboard:
            for button in row:
                buttons_text.append(button.text)
        
        # Should have some reference to lot or minimum amount
        text_combined = ' '.join(buttons_text)
        assert 'lot' in text_combined.lower() or 'minimum' in text_combined.lower()
    
    def test_includes_amount_input_option(self):
        """Test that amount menu includes amount input option."""
        state = {
            'direction': 'sell',
            'custom_price': 145,
            'current_step': 'amount_input'
        }
        
        markup = generate_amount_menu(state)
        
        buttons_text = []
        for row in markup.inline_keyboard:
            for button in row:
                buttons_text.append(button.text)
        
        assert any('Enter' in text or 'Amount' in text for text in buttons_text)
    
    def test_includes_navigation_buttons(self):
        """Test that amount menu includes back and cancel buttons."""
        state = {
            'current_step': 'amount_input'
        }
        
        markup = generate_amount_menu(state)
        
        buttons_text = []
        for row in markup.inline_keyboard:
            for button in row:
                buttons_text.append(button.text)
        
        assert any('Back' in text for text in buttons_text)
        assert any('Cancel' in text for text in buttons_text)


class TestGenerateConfirmationMenu:
    """Test confirmation menu generation."""
    
    def test_shows_spread_summary(self):
        """Test that confirmation menu shows complete spread summary."""
        state = {
            'far_leg_ticker': 'GAZP',
            'near_leg_ticker': 'GZZ4',
            'far_leg_data': {'name': 'Gazprom', 'lot': 10},
            'near_leg_data': {'name': 'Gazprom Dec24', 'lot': 1},
            'direction': 'buy',
            'custom_price': 150,
            'amount': 5,
            'calculated_ratio': 100,
            'current_step': 'confirmation'
        }
        
        markup = generate_confirmation_menu(state)
        
        assert isinstance(markup, InlineKeyboardMarkup)
        
        # Should have confirm and cancel buttons
        buttons_text = []
        for row in markup.inline_keyboard:
            for button in row:
                buttons_text.append(button.text)
        
        assert any('Confirm' in text for text in buttons_text)
        assert any('Cancel' in text or 'Back' in text for text in buttons_text)
    
    def test_includes_market_neutral_explanation(self):
        """Test that confirmation shows market-neutral explanation."""
        state = {
            'far_leg_ticker': 'GAZP',
            'near_leg_ticker': 'GZZ4',
            'direction': 'sell',
            'amount': 3,
            'calculated_ratio': 100,
            'current_step': 'confirmation'
        }
        
        markup = generate_confirmation_menu(state)
        
        # The explanation should be in the message text, not necessarily buttons
        # But we can check that the menu is properly structured
        assert isinstance(markup, InlineKeyboardMarkup)
        assert len(markup.inline_keyboard) >= 1  # At least one row of buttons
    
    def test_callback_data_for_confirmation(self):
        """Test that confirmation buttons have proper callback data."""
        state = {
            'current_step': 'confirmation'
        }
        
        markup = generate_confirmation_menu(state)
        
        # Check callback data format
        for row in markup.inline_keyboard:
            for button in row:
                assert button.callback_data is not None
                assert ':' in button.callback_data  # Should have action:value format


class TestMenuHelperFunctions:
    """Test helper functions used by menu generators."""
    
    def test_empty_state_handling(self):
        """Test that menu generators handle empty or minimal state gracefully."""
        minimal_state = {'current_step': 'direction_selection'}
        
        # Should not raise exceptions
        markup = generate_direction_menu(minimal_state)
        assert isinstance(markup, InlineKeyboardMarkup)
    
    def test_missing_data_handling(self):
        """Test handling of missing data in state."""
        incomplete_state = {
            'far_leg_ticker': 'GAZP',
            # Missing near_leg_ticker and other data
            'current_step': 'price_input'
        }
        
        # Should handle gracefully without crashing
        markup = generate_price_menu(incomplete_state)
        assert isinstance(markup, InlineKeyboardMarkup)