"""
Tests for spread pricing integration with Tinkoff API.

Tests cover price fetching, bid/ask data integration, and error handling
scenarios for the spread pricing system.
"""

import pytest
from decimal import Decimal
from unittest.mock import AsyncMock, Mock, patch

from bot.spread_pricing import (
    get_spread_prices_with_market_data,
    SpreadPriceCalculationError
)


class TestGetSpreadPricesWithMarketData:
    """Test integration with Tinkoff API for spread price calculations."""

    @pytest.mark.asyncio
    async def test_successful_price_fetch_with_order_book(self):
        """Test successful price fetching with bid/ask data."""
        far_leg_data = {
            'figi': 'FIGI1',
            'ticker': 'SBER-6.24',
            'asset_type': 'F',
            'basic_asset_size': 100
        }
        near_leg_data = {
            'figi': 'FIGI2',
            'ticker': 'SBER',
            'asset_type': 'S',
            'basic_asset_size': None
        }
        
        # Mock Tinkoff API responses
        mock_last_prices_response = Mock()
        mock_last_prices_response.last_prices = [
            Mock(figi='FIGI1', price=Mock()),
            Mock(figi='FIGI2', price=Mock())
        ]
        
        mock_order_book_1 = Mock()
        mock_order_book_1.bids = [Mock(price=Mock())]
        mock_order_book_1.asks = [Mock(price=Mock())]
        
        mock_order_book_2 = Mock()
        mock_order_book_2.bids = [Mock(price=Mock())]
        mock_order_book_2.asks = [Mock(price=Mock())]
        
        with patch('bot.spread_pricing.AsyncRetryingClient') as mock_client, \
             patch('bot.spread_pricing.quotation_to_decimal') as mock_quotation_to_decimal:
            
            # Setup quotation conversion
            mock_quotation_to_decimal.side_effect = [
                Decimal('250.50'),  # FIGI1 last price
                Decimal('250.00'),  # FIGI2 last price
                Decimal('250.40'),  # FIGI1 bid
                Decimal('250.60'),  # FIGI1 ask
                Decimal('249.90'),  # FIGI2 bid
                Decimal('250.10'),  # FIGI2 ask
            ]
            
            # Setup client mock
            mock_client_instance = AsyncMock()
            mock_client_instance.market_data.get_last_prices = AsyncMock(
                return_value=mock_last_prices_response
            )
            mock_client_instance.market_data.get_order_book = AsyncMock(
                side_effect=[mock_order_book_1, mock_order_book_2]
            )
            mock_client.return_value.__aenter__.return_value = mock_client_instance
            
            # Test the function
            result = await get_spread_prices_with_market_data(
                far_leg_data, near_leg_data
            )
            
            # Verify results
            assert 'buy' in result
            assert 'sell' in result
            
            # Buy spread: sell far at bid (250.40 * 100), buy near at ask (250.10)
            # = 25040 - 250.10 = 24789.90
            assert result['buy']['spread_price'] == Decimal('24789.90')
            assert result['buy']['ratio'] == 100
            
            # Sell spread: buy far at ask (250.60 * 100), sell near at bid (249.90)
            # = 25060 - 249.90 = 24810.10
            assert result['sell']['spread_price'] == Decimal('24810.10')
            assert result['sell']['ratio'] == 100

    @pytest.mark.asyncio
    async def test_fallback_to_last_prices_when_no_order_book(self):
        """Test fallback to last prices when order book is unavailable."""
        far_leg_data = {
            'figi': 'FIGI1',
            'ticker': 'SBER-6.24',
            'asset_type': 'F',
            'basic_asset_size': 100
        }
        near_leg_data = {
            'figi': 'FIGI2',
            'ticker': 'SBER',
            'asset_type': 'S',
            'basic_asset_size': None
        }
        
        # Mock Tinkoff API responses
        mock_last_prices_response = Mock()
        mock_last_prices_response.last_prices = [
            Mock(figi='FIGI1', price=Mock()),
            Mock(figi='FIGI2', price=Mock())
        ]
        
        # Order book with no bids/asks
        mock_empty_order_book = Mock()
        mock_empty_order_book.bids = []
        mock_empty_order_book.asks = []
        
        with patch('bot.spread_pricing.AsyncRetryingClient') as mock_client, \
             patch('bot.spread_pricing.quotation_to_decimal') as mock_quotation_to_decimal:
            
            # Setup quotation conversion
            mock_quotation_to_decimal.side_effect = [
                Decimal('250.50'),  # FIGI1 last price
                Decimal('250.00'),  # FIGI2 last price
            ]
            
            # Setup client mock
            mock_client_instance = AsyncMock()
            mock_client_instance.market_data.get_last_prices = AsyncMock(
                return_value=mock_last_prices_response
            )
            mock_client_instance.market_data.get_order_book = AsyncMock(
                return_value=mock_empty_order_book
            )
            mock_client.return_value.__aenter__.return_value = mock_client_instance
            
            # Test the function
            result = await get_spread_prices_with_market_data(
                far_leg_data, near_leg_data
            )
            
            # Should use last prices for both buy and sell
            # Buy/Sell spread: 250.50 * 100 - 250.00 = 25050 - 250.00 = 24800.00
            assert result['buy']['spread_price'] == Decimal('24800.00')
            assert result['sell']['spread_price'] == Decimal('24800.00')

    @pytest.mark.asyncio
    async def test_no_price_data_available(self):
        """Test error handling when no price data is available."""
        far_leg_data = {
            'figi': 'FIGI1',
            'ticker': 'SBER-6.24',
            'asset_type': 'F',
            'basic_asset_size': 100
        }
        near_leg_data = {
            'figi': 'FIGI2',
            'ticker': 'SBER',
            'asset_type': 'S',
            'basic_asset_size': None
        }
        
        # Mock empty response
        mock_last_prices_response = Mock()
        mock_last_prices_response.last_prices = []
        
        with patch('bot.spread_pricing.AsyncRetryingClient') as mock_client:
            mock_client_instance = AsyncMock()
            mock_client_instance.market_data.get_last_prices = AsyncMock(
                return_value=mock_last_prices_response
            )
            mock_client.return_value.__aenter__.return_value = mock_client_instance
            
            with pytest.raises(SpreadPriceCalculationError, match="No price data available"):
                await get_spread_prices_with_market_data(far_leg_data, near_leg_data)

    @pytest.mark.asyncio
    async def test_partial_price_data_missing(self):
        """Test error handling when price data is missing for one leg."""
        far_leg_data = {
            'figi': 'FIGI1',
            'ticker': 'SBER-6.24',
            'asset_type': 'F',
            'basic_asset_size': 100
        }
        near_leg_data = {
            'figi': 'FIGI2',
            'ticker': 'SBER',
            'asset_type': 'S',
            'basic_asset_size': None
        }
        
        # Mock response with only one price
        mock_last_prices_response = Mock()
        mock_last_prices_response.last_prices = [
            Mock(figi='FIGI1', price=Mock())
            # FIGI2 missing
        ]
        
        with patch('bot.spread_pricing.AsyncRetryingClient') as mock_client, \
             patch('bot.spread_pricing.quotation_to_decimal') as mock_quotation_to_decimal:
            
            mock_quotation_to_decimal.return_value = Decimal('250.50')
            
            mock_client_instance = AsyncMock()
            mock_client_instance.market_data.get_last_prices = AsyncMock(
                return_value=mock_last_prices_response
            )
            mock_client.return_value.__aenter__.return_value = mock_client_instance
            
            with pytest.raises(SpreadPriceCalculationError, match="Price data unavailable for: SBER"):
                await get_spread_prices_with_market_data(far_leg_data, near_leg_data)

    @pytest.mark.asyncio
    async def test_api_connection_error(self):
        """Test error handling for API connection failures."""
        far_leg_data = {
            'figi': 'FIGI1',
            'ticker': 'SBER-6.24',
            'asset_type': 'F',
            'basic_asset_size': 100
        }
        near_leg_data = {
            'figi': 'FIGI2',
            'ticker': 'SBER',
            'asset_type': 'S',
            'basic_asset_size': None
        }
        
        with patch('bot.spread_pricing.AsyncRetryingClient') as mock_client:
            mock_client_instance = AsyncMock()
            mock_client_instance.market_data.get_last_prices = AsyncMock(
                side_effect=Exception("Connection failed")
            )
            mock_client.return_value.__aenter__.return_value = mock_client_instance
            
            with pytest.raises(SpreadPriceCalculationError, match="Unable to fetch prices"):
                await get_spread_prices_with_market_data(far_leg_data, near_leg_data)

    @pytest.mark.asyncio
    async def test_order_book_fetch_failure_graceful_fallback(self):
        """Test graceful fallback when order book fetch fails."""
        far_leg_data = {
            'figi': 'FIGI1',
            'ticker': 'SBER-6.24',
            'asset_type': 'F',
            'basic_asset_size': 100
        }
        near_leg_data = {
            'figi': 'FIGI2',
            'ticker': 'SBER',
            'asset_type': 'S',
            'basic_asset_size': None
        }
        
        # Mock Tinkoff API responses
        mock_last_prices_response = Mock()
        mock_last_prices_response.last_prices = [
            Mock(figi='FIGI1', price=Mock()),
            Mock(figi='FIGI2', price=Mock())
        ]
        
        with patch('bot.spread_pricing.AsyncRetryingClient') as mock_client, \
             patch('bot.spread_pricing.quotation_to_decimal') as mock_quotation_to_decimal:
            
            mock_quotation_to_decimal.side_effect = [
                Decimal('250.50'),  # FIGI1 last price
                Decimal('250.00'),  # FIGI2 last price
            ]
            
            # Setup client mock with order book failure
            mock_client_instance = AsyncMock()
            mock_client_instance.market_data.get_last_prices = AsyncMock(
                return_value=mock_last_prices_response
            )
            mock_client_instance.market_data.get_order_book = AsyncMock(
                side_effect=Exception("Order book unavailable")
            )
            mock_client.return_value.__aenter__.return_value = mock_client_instance
            
            # Should not raise exception, should fallback to last prices
            result = await get_spread_prices_with_market_data(
                far_leg_data, near_leg_data
            )
            
            # Should use last prices for both buy and sell
            assert result['buy']['spread_price'] == Decimal('24800.00')
            assert result['sell']['spread_price'] == Decimal('24800.00')

    @pytest.mark.asyncio
    async def test_future_future_spread_integration(self):
        """Test integration with future-future spread."""
        far_leg_data = {
            'figi': 'FIGI1',
            'ticker': 'SBER-9.24',
            'asset_type': 'F',
            'basic_asset_size': 100
        }
        near_leg_data = {
            'figi': 'FIGI2',
            'ticker': 'SBER-6.24',
            'asset_type': 'F',
            'basic_asset_size': 100
        }
        
        # Mock Tinkoff API responses
        mock_last_prices_response = Mock()
        mock_last_prices_response.last_prices = [
            Mock(figi='FIGI1', price=Mock()),
            Mock(figi='FIGI2', price=Mock())
        ]
        
        mock_order_book_1 = Mock()
        mock_order_book_1.bids = [Mock(price=Mock())]
        mock_order_book_1.asks = [Mock(price=Mock())]
        
        mock_order_book_2 = Mock()
        mock_order_book_2.bids = [Mock(price=Mock())]
        mock_order_book_2.asks = [Mock(price=Mock())]
        
        with patch('bot.spread_pricing.AsyncRetryingClient') as mock_client, \
             patch('bot.spread_pricing.quotation_to_decimal') as mock_quotation_to_decimal:
            
            # Setup quotation conversion
            mock_quotation_to_decimal.side_effect = [
                Decimal('255.00'),  # FIGI1 last price
                Decimal('250.50'),  # FIGI2 last price
                Decimal('254.90'),  # FIGI1 bid
                Decimal('255.10'),  # FIGI1 ask
                Decimal('250.40'),  # FIGI2 bid
                Decimal('250.60'),  # FIGI2 ask
            ]
            
            # Setup client mock
            mock_client_instance = AsyncMock()
            mock_client_instance.market_data.get_last_prices = AsyncMock(
                return_value=mock_last_prices_response
            )
            mock_client_instance.market_data.get_order_book = AsyncMock(
                side_effect=[mock_order_book_1, mock_order_book_2]
            )
            mock_client.return_value.__aenter__.return_value = mock_client_instance
            
            # Test the function
            result = await get_spread_prices_with_market_data(
                far_leg_data, near_leg_data
            )
            
            # Future-future spread should have 1:1 ratio
            assert result['buy']['ratio'] == 1
            assert result['sell']['ratio'] == 1
            
            # Buy spread: sell far at bid (254.90), buy near at ask (250.60)
            # = 254.90 - 250.60 = 4.30
            assert result['buy']['spread_price'] == Decimal('4.30')
            
            # Sell spread: buy far at ask (255.10), sell near at bid (250.40)
            # = 255.10 - 250.40 = 4.70
            assert result['sell']['spread_price'] == Decimal('4.70')