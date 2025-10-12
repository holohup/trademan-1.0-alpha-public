"""
Tests for spread pricing calculation module.

Tests cover price calculations, ratio calculations, and market-neutral
explanations for different asset type combinations.
"""

import pytest
from decimal import Decimal
from unittest.mock import Mock

from bot.spread_pricing import (
    calculate_spread_price,
    calculate_ratio,
    get_market_neutral_explanation,
    SpreadPriceCalculationError
)


class TestCalculateRatio:
    """Test ratio calculations for different asset combinations."""

    def test_stock_future_ratio(self):
        """Test ratio calculation for stock-future spread."""
        # Stock as near leg, future as far leg
        stock_data = {
            'asset_type': 'S',
            'lot': 1,
            'basic_asset_size': None
        }
        future_data = {
            'asset_type': 'F',
            'lot': 1,
            'basic_asset_size': 100  # 1 future = 100 stocks
        }
        
        ratio = calculate_ratio(future_data, stock_data)
        assert ratio == 100

    def test_future_future_ratio(self):
        """Test ratio calculation for future-future spread."""
        # Both legs are futures
        far_future_data = {
            'asset_type': 'F',
            'lot': 1,
            'basic_asset_size': 100
        }
        near_future_data = {
            'asset_type': 'F',
            'lot': 1,
            'basic_asset_size': 100
        }
        
        ratio = calculate_ratio(far_future_data, near_future_data)
        assert ratio == 1

    def test_different_basic_asset_sizes(self):
        """Test ratio with different basic asset sizes."""
        far_future_data = {
            'asset_type': 'F',
            'lot': 1,
            'basic_asset_size': 1000  # Large contract
        }
        near_future_data = {
            'asset_type': 'F',
            'lot': 1,
            'basic_asset_size': 100   # Small contract
        }
        
        ratio = calculate_ratio(far_future_data, near_future_data)
        assert ratio == 10  # 1000 / 100

    def test_stock_stock_ratio(self):
        """Test ratio calculation for stock-stock spread (should be 1:1)."""
        stock1_data = {
            'asset_type': 'S',
            'lot': 10,
            'basic_asset_size': None
        }
        stock2_data = {
            'asset_type': 'S',
            'lot': 1,
            'basic_asset_size': None
        }
        
        ratio = calculate_ratio(stock1_data, stock2_data)
        assert ratio == 1

    def test_missing_basic_asset_size_for_future(self):
        """Test error handling when future lacks basic_asset_size."""
        future_data = {
            'asset_type': 'F',
            'lot': 1,
            'basic_asset_size': None  # Missing required field
        }
        stock_data = {
            'asset_type': 'S',
            'lot': 1,
            'basic_asset_size': None
        }
        
        with pytest.raises(SpreadPriceCalculationError):
            calculate_ratio(future_data, stock_data)


class TestCalculateSpreadPrice:
    """Test spread price calculations for different scenarios."""

    def test_buy_spread_calculation(self):
        """Test buying spread price calculation."""
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
        
        # Mock price data
        price_data = {
            'FIGI1': {
                'last_price': Decimal('250.50'),
                'bid_price': Decimal('250.40'),
                'ask_price': Decimal('250.60')
            },
            'FIGI2': {
                'last_price': Decimal('250.00'),
                'bid_price': Decimal('249.90'),
                'ask_price': Decimal('250.10')
            }
        }
        
        # Buy spread: sell far leg at bid, buy near leg at ask
        # Price = (250.40 * 100) - 250.10 = 25040 - 250.10 = 24789.90
        result = calculate_spread_price(
            far_leg_data, near_leg_data, price_data, 'buy'
        )
        
        expected_price = Decimal('24789.90')
        assert result['spread_price'] == expected_price
        assert result['ratio'] == 100
        assert result['far_leg_price'] == Decimal('250.40')
        assert result['near_leg_price'] == Decimal('250.10')

    def test_sell_spread_calculation(self):
        """Test selling spread price calculation."""
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
        
        # Mock price data
        price_data = {
            'FIGI1': {
                'last_price': Decimal('250.50'),
                'bid_price': Decimal('250.40'),
                'ask_price': Decimal('250.60')
            },
            'FIGI2': {
                'last_price': Decimal('250.00'),
                'bid_price': Decimal('249.90'),
                'ask_price': Decimal('250.10')
            }
        }
        
        # Sell spread: buy far leg at ask, sell near leg at bid
        # Price = (250.60 * 100) - 249.90 = 25060 - 249.90 = 24810.10
        result = calculate_spread_price(
            far_leg_data, near_leg_data, price_data, 'sell'
        )
        
        expected_price = Decimal('24810.10')
        assert result['spread_price'] == expected_price
        assert result['ratio'] == 100
        assert result['far_leg_price'] == Decimal('250.60')
        assert result['near_leg_price'] == Decimal('249.90')

    def test_future_future_spread_calculation(self):
        """Test future-future spread calculation."""
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
        
        # Mock price data
        price_data = {
            'FIGI1': {
                'last_price': Decimal('255.00'),
                'bid_price': Decimal('254.90'),
                'ask_price': Decimal('255.10')
            },
            'FIGI2': {
                'last_price': Decimal('250.50'),
                'bid_price': Decimal('250.40'),
                'ask_price': Decimal('250.60')
            }
        }
        
        # Buy spread: sell far leg at bid, buy near leg at ask
        # Price = 254.90 - 250.60 = 4.30
        result = calculate_spread_price(
            far_leg_data, near_leg_data, price_data, 'buy'
        )
        
        expected_price = Decimal('4.30')
        assert result['spread_price'] == expected_price
        assert result['ratio'] == 1

    def test_missing_price_data(self):
        """Test error handling when price data is missing."""
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
        
        # Missing price data for one FIGI
        price_data = {
            'FIGI1': {
                'last_price': Decimal('250.50'),
                'bid_price': Decimal('250.40'),
                'ask_price': Decimal('250.60')
            }
            # FIGI2 missing
        }
        
        with pytest.raises(SpreadPriceCalculationError):
            calculate_spread_price(
                far_leg_data, near_leg_data, price_data, 'buy'
            )

    def test_missing_bid_ask_prices(self):
        """Test fallback to last price when bid/ask unavailable."""
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
        
        # Price data without bid/ask
        price_data = {
            'FIGI1': {
                'last_price': Decimal('250.50')
                # No bid/ask prices
            },
            'FIGI2': {
                'last_price': Decimal('250.00')
                # No bid/ask prices
            }
        }
        
        result = calculate_spread_price(
            far_leg_data, near_leg_data, price_data, 'buy'
        )
        
        # Should use last prices for both legs
        expected_price = Decimal('250.50') * 100 - Decimal('250.00')
        assert result['spread_price'] == expected_price
        assert result['far_leg_price'] == Decimal('250.50')
        assert result['near_leg_price'] == Decimal('250.00')

    def test_invalid_direction(self):
        """Test error handling for invalid direction."""
        far_leg_data = {'figi': 'FIGI1', 'asset_type': 'F', 'basic_asset_size': 100}
        near_leg_data = {'figi': 'FIGI2', 'asset_type': 'S', 'basic_asset_size': None}
        price_data = {
            'FIGI1': {'last_price': Decimal('250.50')},
            'FIGI2': {'last_price': Decimal('250.00')}
        }
        
        with pytest.raises(SpreadPriceCalculationError):
            calculate_spread_price(
                far_leg_data, near_leg_data, price_data, 'invalid'
            )


class TestGetMarketNeutralExplanation:
    """Test market-neutral explanation generation."""

    def test_buy_stock_future_explanation(self):
        """Test explanation for buying stock-future spread."""
        far_leg_data = {
            'ticker': 'SBER-6.24',
            'asset_type': 'F',
            'basic_asset_size': 100
        }
        near_leg_data = {
            'ticker': 'SBER',
            'asset_type': 'S',
            'basic_asset_size': None
        }
        
        explanation = get_market_neutral_explanation(
            far_leg_data, near_leg_data, 'buy', 100
        )
        
        expected = (
            "Покупка спреда (market-neutral позиция):\n"
            "• Продать 1 SBER-6.24 (фьючерс)\n"
            "• Купить 100 SBER (акции)\n"
            "Соотношение: 1:100"
        )
        assert explanation == expected

    def test_sell_stock_future_explanation(self):
        """Test explanation for selling stock-future spread."""
        far_leg_data = {
            'ticker': 'SBER-6.24',
            'asset_type': 'F',
            'basic_asset_size': 100
        }
        near_leg_data = {
            'ticker': 'SBER',
            'asset_type': 'S',
            'basic_asset_size': None
        }
        
        explanation = get_market_neutral_explanation(
            far_leg_data, near_leg_data, 'sell', 100
        )
        
        expected = (
            "Продажа спреда (market-neutral позиция):\n"
            "• Купить 1 SBER-6.24 (фьючерс)\n"
            "• Продать 100 SBER (акции)\n"
            "Соотношение: 1:100"
        )
        assert explanation == expected

    def test_buy_future_future_explanation(self):
        """Test explanation for buying future-future spread."""
        far_leg_data = {
            'ticker': 'SBER-9.24',
            'asset_type': 'F',
            'basic_asset_size': 100
        }
        near_leg_data = {
            'ticker': 'SBER-6.24',
            'asset_type': 'F',
            'basic_asset_size': 100
        }
        
        explanation = get_market_neutral_explanation(
            far_leg_data, near_leg_data, 'buy', 1
        )
        
        expected = (
            "Покупка спреда (market-neutral позиция):\n"
            "• Продать 1 SBER-9.24 (фьючерс)\n"
            "• Купить 1 SBER-6.24 (фьючерс)\n"
            "Соотношение: 1:1"
        )
        assert explanation == expected

    def test_sell_future_future_explanation(self):
        """Test explanation for selling future-future spread."""
        far_leg_data = {
            'ticker': 'SBER-9.24',
            'asset_type': 'F',
            'basic_asset_size': 100
        }
        near_leg_data = {
            'ticker': 'SBER-6.24',
            'asset_type': 'F',
            'basic_asset_size': 100
        }
        
        explanation = get_market_neutral_explanation(
            far_leg_data, near_leg_data, 'sell', 1
        )
        
        expected = (
            "Продажа спреда (market-neutral позиция):\n"
            "• Купить 1 SBER-9.24 (фьючерс)\n"
            "• Продать 1 SBER-6.24 (фьючерс)\n"
            "Соотношение: 1:1"
        )
        assert explanation == expected

    def test_different_ratios_explanation(self):
        """Test explanation with different ratios."""
        far_leg_data = {
            'ticker': 'GAZP-6.24',
            'asset_type': 'F',
            'basic_asset_size': 1000  # Large contract
        }
        near_leg_data = {
            'ticker': 'GAZP',
            'asset_type': 'S',
            'basic_asset_size': None
        }
        
        explanation = get_market_neutral_explanation(
            far_leg_data, near_leg_data, 'buy', 1000
        )
        
        expected = (
            "Покупка спреда (market-neutral позиция):\n"
            "• Продать 1 GAZP-6.24 (фьючерс)\n"
            "• Купить 1000 GAZP (акции)\n"
            "Соотношение: 1:1000"
        )
        assert explanation == expected