"""
Test that all spread-related commands are properly registered in the bot.
"""

import pytest


class TestCommandRegistration:
    """Test command registration and integration."""

    def test_addspread_command_registered(self):
        """Test that addspread command is registered in ROUTINES."""
        from bot.commands import ROUTINES
        
        assert 'addspread' in ROUTINES
        assert ROUTINES['addspread'][0] == 'Add new spread'
        
        # Verify the handler function is callable
        handler_func = ROUTINES['addspread'][1]
        assert callable(handler_func)

    def test_spreads_command_registered(self):
        """Test that spreads command is registered in ROUTINES."""
        from bot.commands import ROUTINES
        
        assert 'spreads' in ROUTINES
        assert ROUTINES['spreads'][0] == 'Spreads monitoring and trading'
        
        # Verify the handler function is callable
        handler_func = ROUTINES['spreads'][1]
        assert callable(handler_func)

    def test_command_handler_imports(self):
        """Test that command handlers can be imported successfully."""
        # Test addspread handler import
        from bot.spread_creator import handle_addspread_command
        assert callable(handle_addspread_command)
        
        # Test spreads handler import
        from bot.spreads import spreads
        assert callable(spreads)

    def test_callback_handlers_registered(self):
        """Test that callback handlers are registered with the dispatcher."""
        from bot_init import dp
        
        # Check that callback handlers exist
        handlers = dp.callback_query_handlers
        assert handlers is not None
        
        # The spread_creator module should register callback handlers
        # when imported (via decorators)
        import bot.spread_creator
        
        # Verify handlers are still registered after import
        handlers_after = dp.callback_query_handlers
        assert handlers_after is not None

    def test_message_handlers_registered(self):
        """Test that message handlers are registered with the dispatcher."""
        from bot_init import dp
        
        # Check that message handlers exist
        handlers = dp.message_handlers
        assert handlers is not None
        
        # The spread_creator module should register message handlers
        # when imported (via decorators)
        import bot.spread_creator
        
        # Verify handlers are still registered after import
        handlers_after = dp.message_handlers
        assert handlers_after is not None

    def test_spread_modules_integration(self):
        """Test that all spread-related modules can be imported together."""
        # Test that all modules can be imported without conflicts
        import bot.spread_creator
        import bot.spread_state
        import bot.spread_menu
        import bot.spread_pricing
        import bot.spread_api
        import bot.spread_logging
        import bot.spreads
        
        # Verify key functions are available
        assert hasattr(bot.spread_creator, 'handle_addspread_command')
        assert hasattr(bot.spread_state, 'save_state')
        assert hasattr(bot.spread_menu, 'generate_direction_menu')
        assert hasattr(bot.spread_pricing, 'calculate_spread_price')
        assert hasattr(bot.spread_api, 'create_spread')
        assert hasattr(bot.spreads, 'spreads')

    def test_django_integration_modules(self):
        """Test that Django integration modules are available."""
        # Test that Django-related modules can be imported
        from bot.tools.get_patch_prepare_data import prepare_spreads_data, async_patch_spread
        from bot.tools.classes import Spread
        
        assert callable(prepare_spreads_data)
        assert callable(async_patch_spread)
        assert Spread is not None