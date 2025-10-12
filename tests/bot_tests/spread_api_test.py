import pytest
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock, patch
import aiohttp
from bot.spread_api import (
    validate_ticker,
    get_current_prices,
    APIError,
    TickerNotFoundError,
    PriceUnavailableError
)


class TestValidateTicker:
    """Test ticker validation functionality."""

    @pytest.mark.asyncio
    async def test_validate_ticker_success(self):
        """Test successful ticker validation."""
        mock_response_data = {
            'id': 1,
            'figi': 'BBG004730N88',
            'ticker': 'SBER',
            'name': 'Сбер Банк',
            'lot': 10,
            'min_price_increment': '0.0100000000',
            'asset_type': 'S',
            'api_trading_available': True,
            'short_enabled': True,
            'buy_enabled': True,
            'sell_enabled': True,
            'basic_asset_size': None,
            'basic_asset': None,
            'morning_trading': False,
            'evening_trading': False
        }
        
        with patch('aiohttp.ClientSession.get') as mock_get:
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.json = AsyncMock(return_value=mock_response_data)
            mock_get.return_value.__aenter__.return_value = mock_response
            
            result = await validate_ticker('SBER')
            
            assert result['ticker'] == 'SBER'
            assert result['figi'] == 'BBG004730N88'
            assert result['api_trading_available'] is True
            assert result['asset_type'] == 'S'
            assert result['lot'] == 10

    @pytest.mark.asyncio
    async def test_validate_ticker_not_found(self):
        """Test ticker not found scenario."""
        with patch('aiohttp.ClientSession.get') as mock_get:
            mock_response = AsyncMock()
            mock_response.status = 404
            mock_get.return_value.__aenter__.return_value = mock_response
            
            with pytest.raises(TickerNotFoundError, match="Ticker INVALID not found"):
                await validate_ticker('INVALID')

    @pytest.mark.asyncio
    async def test_validate_ticker_api_trading_disabled(self):
        """Test ticker with API trading disabled."""
        mock_response_data = {
            'id': 1,
            'figi': 'BBG004730N88',
            'ticker': 'SBER',
            'name': 'Сбер Банк',
            'lot': 10,
            'min_price_increment': '0.0100000000',
            'asset_type': 'S',
            'api_trading_available': False,
            'short_enabled': True,
            'buy_enabled': True,
            'sell_enabled': True,
            'basic_asset_size': None,
            'basic_asset': None
        }
        
        with patch('aiohttp.ClientSession.get') as mock_get:
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.json = AsyncMock(return_value=mock_response_data)
            mock_get.return_value.__aenter__.return_value = mock_response
            
            with pytest.raises(APIError, match="API trading not available for SBER"):
                await validate_ticker('SBER')

    @pytest.mark.asyncio
    async def test_validate_ticker_connection_error(self):
        """Test connection error handling."""
        with patch('aiohttp.ClientSession.get') as mock_get:
            mock_get.side_effect = aiohttp.ClientError("Connection failed")
            
            with pytest.raises(APIError, match="Unable to connect to trading system"):
                await validate_ticker('SBER')

    @pytest.mark.asyncio
    async def test_validate_ticker_server_error(self):
        """Test server error handling."""
        with patch('aiohttp.ClientSession.get') as mock_get:
            mock_response = AsyncMock()
            mock_response.status = 500
            mock_get.return_value.__aenter__.return_value = mock_response
            
            with pytest.raises(APIError, match="Server error"):
                await validate_ticker('SBER')


class TestGetCurrentPrices:
    """Test price fetching functionality."""

    @pytest.mark.asyncio
    async def test_get_current_prices_success(self):
        """Test successful price fetching."""
        figis = ['BBG004730N88', 'BBG00475KKY8']
        
        mock_last_prices = [
            MagicMock(figi='BBG004730N88', price=MagicMock()),
            MagicMock(figi='BBG00475KKY8', price=MagicMock())
        ]
        mock_response = MagicMock(last_prices=mock_last_prices)
        
        with patch('bot.spread_api.quotation_to_decimal') as mock_quotation:
            mock_quotation.side_effect = [Decimal('250.50'), Decimal('1500.00')]
            
            with patch('bot.spread_api.AsyncRetryingClient') as mock_client:
                mock_client_instance = AsyncMock()
                mock_client_instance.market_data.get_last_prices = AsyncMock(return_value=mock_response)
                mock_client.return_value.__aenter__.return_value = mock_client_instance
                
                result = await get_current_prices(figis)
                
                assert len(result) == 2
                assert result['BBG004730N88']['last_price'] == Decimal('250.50')
                assert result['BBG00475KKY8']['last_price'] == Decimal('1500.00')

    @pytest.mark.asyncio
    async def test_get_current_prices_with_order_book(self):
        """Test price fetching with order book data."""
        figis = ['BBG004730N88']
        
        # Mock last prices response
        mock_last_prices = [MagicMock(figi='BBG004730N88', price=MagicMock())]
        mock_last_prices_response = MagicMock(last_prices=mock_last_prices)
        
        # Mock order book response
        mock_bid = MagicMock(price=MagicMock())
        mock_ask = MagicMock(price=MagicMock())
        mock_order_book = MagicMock(bids=[mock_bid], asks=[mock_ask])
        
        with patch('bot.spread_api.quotation_to_decimal') as mock_quotation:
            mock_quotation.side_effect = [Decimal('250.50'), Decimal('250.40'), Decimal('250.60')]
            
            with patch('bot.spread_api.AsyncRetryingClient') as mock_client:
                mock_client_instance = AsyncMock()
                mock_client_instance.market_data.get_last_prices = AsyncMock(return_value=mock_last_prices_response)
                mock_client_instance.market_data.get_order_book = AsyncMock(return_value=mock_order_book)
                mock_client.return_value.__aenter__.return_value = mock_client_instance
                
                result = await get_current_prices(figis, include_order_book=True)
                
                assert result['BBG004730N88']['last_price'] == Decimal('250.50')
                assert result['BBG004730N88']['bid_price'] == Decimal('250.40')
                assert result['BBG004730N88']['ask_price'] == Decimal('250.60')

    @pytest.mark.asyncio
    async def test_get_current_prices_empty_response(self):
        """Test handling of empty price response."""
        figis = ['BBG004730N88']
        
        mock_response = MagicMock(last_prices=[])
        
        with patch('bot.spread_api.AsyncRetryingClient') as mock_client:
            mock_client_instance = AsyncMock()
            mock_client_instance.market_data.get_last_prices = AsyncMock(return_value=mock_response)
            mock_client.return_value.__aenter__.return_value = mock_client_instance
            
            with pytest.raises(PriceUnavailableError, match="No price data available"):
                await get_current_prices(figis)

    @pytest.mark.asyncio
    async def test_get_current_prices_partial_data(self):
        """Test handling of partial price data."""
        figis = ['BBG004730N88', 'BBG00475KKY8']
        
        # Only one price returned
        mock_last_prices = [MagicMock(figi='BBG004730N88', price=MagicMock())]
        mock_response = MagicMock(last_prices=mock_last_prices)
        
        with patch('bot.spread_api.quotation_to_decimal') as mock_quotation:
            mock_quotation.return_value = Decimal('250.50')
            
            with patch('bot.spread_api.AsyncRetryingClient') as mock_client:
                mock_client_instance = AsyncMock()
                mock_client_instance.market_data.get_last_prices = AsyncMock(return_value=mock_response)
                mock_client.return_value.__aenter__.return_value = mock_client_instance
                
                result = await get_current_prices(figis)
                
                assert len(result) == 1
                assert 'BBG004730N88' in result
                assert 'BBG00475KKY8' not in result

    @pytest.mark.asyncio
    async def test_get_current_prices_connection_error(self):
        """Test connection error handling in price fetching."""
        figis = ['BBG004730N88']
        
        with patch('bot.spread_api.AsyncRetryingClient') as mock_client:
            mock_client.side_effect = Exception("Connection failed")
            
            with pytest.raises(APIError, match="Unable to fetch prices"):
                await get_current_prices(figis)

    @pytest.mark.asyncio
    async def test_get_current_prices_order_book_no_bids_asks(self):
        """Test order book with no bids or asks."""
        figis = ['BBG004730N88']
        
        # Mock last prices response
        mock_last_prices = [MagicMock(figi='BBG004730N88', price=MagicMock())]
        mock_last_prices_response = MagicMock(last_prices=mock_last_prices)
        
        # Mock order book with no bids/asks
        mock_order_book = MagicMock(bids=[], asks=[])
        
        with patch('bot.spread_api.quotation_to_decimal') as mock_quotation:
            mock_quotation.return_value = Decimal('250.50')
            
            with patch('bot.spread_api.AsyncRetryingClient') as mock_client:
                mock_client_instance = AsyncMock()
                mock_client_instance.market_data.get_last_prices = AsyncMock(return_value=mock_last_prices_response)
                mock_client_instance.market_data.get_order_book = AsyncMock(return_value=mock_order_book)
                mock_client.return_value.__aenter__.return_value = mock_client_instance
                
                result = await get_current_prices(figis, include_order_book=True)
                
                # Should still return last price, but no bid/ask
                assert result['BBG004730N88']['last_price'] == Decimal('250.50')
                assert 'bid_price' not in result['BBG004730N88']
                assert 'ask_price' not in result['BBG004730N88']


class TestCreateSpread:
    """Test spread creation functionality."""

    @pytest.mark.asyncio
    async def test_create_spread_success(self):
        """Test successful spread creation."""
        spread_data = {
            'far_leg_figi': 'BBG004730N88',
            'near_leg_figi': 'BBG00475KKY8',
            'sell': True,
            'price': 100,
            'amount': 10
        }
        
        mock_response_data = {'id': 123}
        
        with patch('aiohttp.ClientSession.post') as mock_post:
            mock_response = AsyncMock()
            mock_response.status = 201
            mock_response.json = AsyncMock(return_value=mock_response_data)
            mock_post.return_value.__aenter__.return_value = mock_response
            
            from bot.spread_api import create_spread
            result = await create_spread(spread_data)
            
            assert result == 123
            mock_post.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_spread_server_error(self):
        """Test spread creation server error."""
        spread_data = {
            'far_leg_figi': 'BBG004730N88',
            'near_leg_figi': 'BBG00475KKY8',
            'sell': True,
            'price': 100,
            'amount': 10
        }
        
        with patch('aiohttp.ClientSession.post') as mock_post:
            mock_response = AsyncMock()
            mock_response.status = 400
            mock_response.text = AsyncMock(return_value='Bad request')
            mock_post.return_value.__aenter__.return_value = mock_response
            
            from bot.spread_api import create_spread
            with pytest.raises(APIError, match="Error creating spread"):
                await create_spread(spread_data)

    @pytest.mark.asyncio
    async def test_create_spread_connection_error(self):
        """Test spread creation connection error."""
        spread_data = {
            'far_leg_figi': 'BBG004730N88',
            'near_leg_figi': 'BBG00475KKY8',
            'sell': True,
            'price': 100,
            'amount': 10
        }
        
        with patch('aiohttp.ClientSession.post') as mock_post:
            mock_post.side_effect = aiohttp.ClientError("Connection failed")
            
            from bot.spread_api import create_spread
            with pytest.raises(APIError, match="Unable to connect to trading system"):
                await create_spread(spread_data)


class TestCheckDuplicateSpread:
    """Test duplicate spread detection functionality."""

    @pytest.mark.asyncio
    async def test_check_duplicate_spread_found(self):
        """Test duplicate spread detection when duplicate exists."""
        mock_spreads_data = [
            {
                'id': 1,
                'far_leg': {'ticker': 'RIH4', 'figi': 'BBG004730N88'},
                'near_leg': {'ticker': 'SBER', 'figi': 'BBG00475KKY8'},
                'sell': True,
                'price': 100,
                'amount': 10
            }
        ]
        
        with patch('aiohttp.ClientSession.get') as mock_get:
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.json = AsyncMock(return_value=mock_spreads_data)
            mock_get.return_value.__aenter__.return_value = mock_response
            
            from bot.spread_api import check_duplicate_spread
            result = await check_duplicate_spread('BBG004730N88', 'BBG00475KKY8')
            
            assert result == 1

    @pytest.mark.asyncio
    async def test_check_duplicate_spread_not_found(self):
        """Test duplicate spread detection when no duplicate exists."""
        mock_spreads_data = [
            {
                'id': 1,
                'far_leg': {'ticker': 'RIH4', 'figi': 'BBG004730N88'},
                'near_leg': {'ticker': 'GAZP', 'figi': 'BBG004730RP0'},
                'sell': True,
                'price': 100,
                'amount': 10
            }
        ]
        
        with patch('aiohttp.ClientSession.get') as mock_get:
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.json = AsyncMock(return_value=mock_spreads_data)
            mock_get.return_value.__aenter__.return_value = mock_response
            
            from bot.spread_api import check_duplicate_spread
            result = await check_duplicate_spread('BBG004730N88', 'BBG00475KKY8')
            
            assert result is None

    @pytest.mark.asyncio
    async def test_check_duplicate_spread_empty_response(self):
        """Test duplicate spread detection with empty spreads list."""
        with patch('aiohttp.ClientSession.get') as mock_get:
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.json = AsyncMock(return_value=[])
            mock_get.return_value.__aenter__.return_value = mock_response
            
            from bot.spread_api import check_duplicate_spread
            result = await check_duplicate_spread('BBG004730N88', 'BBG00475KKY8')
            
            assert result is None

    @pytest.mark.asyncio
    async def test_check_duplicate_spread_connection_error(self):
        """Test duplicate spread detection connection error."""
        with patch('aiohttp.ClientSession.get') as mock_get:
            mock_get.side_effect = aiohttp.ClientError("Connection failed")
            
            from bot.spread_api import check_duplicate_spread
            with pytest.raises(APIError, match="Unable to connect to trading system"):
                await check_duplicate_spread('BBG004730N88', 'BBG00475KKY8')

    @pytest.mark.asyncio
    async def test_check_duplicate_spread_server_error(self):
        """Test duplicate spread detection server error."""
        with patch('aiohttp.ClientSession.get') as mock_get:
            mock_response = AsyncMock()
            mock_response.status = 500
            mock_get.return_value.__aenter__.return_value = mock_response
            
            from bot.spread_api import check_duplicate_spread
            with pytest.raises(APIError, match="Server error"):
                await check_duplicate_spread('BBG004730N88', 'BBG00475KKY8')