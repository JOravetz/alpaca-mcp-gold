"""
Test configuration and fixtures following gold standard patterns.
Provides state management and test utilities.
"""

import pytest
import asyncio
from unittest.mock import MagicMock, AsyncMock
from src.mcp_server.models.schemas import StateManager
from src.mcp_server.models.alpaca_clients import AlpacaClientManager

@pytest.fixture(autouse=True)
def clear_state():
    """
    ESSENTIAL: Clear state between tests.
    Automatically runs before and after each test to ensure clean state.
    """
    StateManager.clear_all()
    yield
    StateManager.clear_all()

@pytest.fixture
def mock_trading_client():
    """Mock Alpaca trading client for testing."""
    mock_client = MagicMock()
    
    # Mock account data
    mock_account = MagicMock()
    mock_account.id = "test_account_123"
    mock_account.status = "ACTIVE"
    mock_account.currency = "USD"
    mock_account.buying_power = 10000.0
    mock_account.cash = 5000.0
    mock_account.portfolio_value = 15000.0
    mock_account.equity = 15000.0
    mock_account.long_market_value = 10000.0
    mock_account.short_market_value = 0.0
    mock_account.pattern_day_trader = False
    mock_account.daytrade_count = 0
    
    mock_client.get_account.return_value = mock_account
    
    # Mock position data
    mock_position = MagicMock()
    mock_position.symbol = "AAPL"
    mock_position.qty = 100.0
    mock_position.market_value = 15000.0
    mock_position.avg_entry_price = 145.0
    mock_position.current_price = 150.0
    mock_position.unrealized_pl = 500.0
    mock_position.unrealized_plpc = 0.0345
    
    mock_client.get_all_positions.return_value = [mock_position]
    mock_client.get_open_position.return_value = mock_position
    
    # Mock order data
    mock_order = MagicMock()
    mock_order.id = "order_123"
    mock_order.symbol = "AAPL"
    mock_order.side = "buy"
    mock_order.order_type = "market"
    mock_order.qty = 10.0
    mock_order.status = "filled"
    mock_order.time_in_force = "day"
    mock_order.submitted_at = None
    mock_order.filled_at = None
    mock_order.filled_qty = 10.0
    mock_order.filled_avg_price = 150.0
    
    mock_client.submit_order.return_value = mock_order
    mock_client.get_orders.return_value = [mock_order]
    
    return mock_client

@pytest.fixture
def mock_stock_data_client():
    """Mock Alpaca stock data client for testing."""
    mock_client = MagicMock()
    
    # Mock quote data
    mock_quote = MagicMock()
    mock_quote.bid_price = 149.50
    mock_quote.ask_price = 149.52
    mock_quote.bid_size = 100
    mock_quote.ask_size = 200
    mock_quote.timestamp = asyncio.get_event_loop().time()
    
    mock_client.get_stock_latest_quote.return_value = {"AAPL": mock_quote}
    
    # Mock trade data
    mock_trade = MagicMock()
    mock_trade.price = 149.51
    mock_trade.size = 150
    mock_trade.timestamp = asyncio.get_event_loop().time()
    mock_trade.exchange = "NASDAQ"
    mock_trade.conditions = []
    
    mock_client.get_stock_latest_trade.return_value = {"AAPL": mock_trade}
    
    # Mock snapshot data
    mock_snapshot = MagicMock()
    mock_snapshot.latest_quote = mock_quote
    mock_snapshot.latest_trade = mock_trade
    
    # Mock daily bar
    mock_daily_bar = MagicMock()
    mock_daily_bar.open = 148.0
    mock_daily_bar.high = 151.0
    mock_daily_bar.low = 147.5
    mock_daily_bar.close = 150.0
    mock_daily_bar.volume = 50000000
    mock_daily_bar.timestamp = asyncio.get_event_loop().time()
    
    mock_snapshot.daily_bar = mock_daily_bar
    mock_snapshot.prev_daily_bar = mock_daily_bar
    
    mock_client.get_stock_snapshot.return_value = {"AAPL": mock_snapshot}
    
    # Mock historical bars
    mock_bars = [mock_daily_bar] * 10  # 10 bars of historical data
    mock_client.get_stock_bars.return_value = {"AAPL": mock_bars}
    
    return mock_client

@pytest.fixture
def mock_options_data_client():
    """Mock Alpaca options data client for testing."""
    mock_client = MagicMock()
    return mock_client

@pytest.fixture
def mock_alpaca_clients(mock_trading_client, mock_stock_data_client, mock_options_data_client):
    """Mock all Alpaca clients."""
    # Patch the AlpacaClientManager methods
    AlpacaClientManager._trading_client = mock_trading_client
    AlpacaClientManager._stock_data_client = mock_stock_data_client
    AlpacaClientManager._options_data_client = mock_options_data_client
    
    yield {
        "trading": mock_trading_client,
        "stock_data": mock_stock_data_client,
        "options_data": mock_options_data_client
    }
    
    # Reset clients after test
    AlpacaClientManager._trading_client = None
    AlpacaClientManager._stock_data_client = None
    AlpacaClientManager._options_data_client = None

@pytest.fixture
def sample_portfolio_data():
    """Sample portfolio data for testing."""
    return {
        "buying_power": "10000.00",
        "portfolio_value": "15000.00", 
        "equity": "15000.00",
        "cash": "5000.00"
    }

@pytest.fixture
def sample_position_data():
    """Sample position data for testing."""
    return {
        "symbol": "AAPL",
        "qty": "100.0",
        "market_value": "15000.0",
        "avg_entry_price": "145.0",
        "current_price": "150.0",
        "unrealized_pl": "500.0",
        "unrealized_plpc": "0.0345"
    }

@pytest.fixture
def sample_stock_data():
    """Sample stock data for testing."""
    return {
        "price_change_percent": 2.5,
        "volume": 50000000,
        "high": 151.0,
        "low": 147.5,
        "volatility": 2.0
    }

# Async test utilities
@pytest.fixture
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

# Test data validation helpers
def assert_success_response(response: dict):
    """Assert that a response indicates success."""
    assert response["status"] == "success"
    assert "data" in response
    assert "metadata" in response

def assert_error_response(response: dict):
    """Assert that a response indicates an error."""
    assert response["status"] == "error"
    assert "message" in response
    assert "error_type" in response

def assert_resource_response(response: dict):
    """Assert that a resource response is valid."""
    assert "resource_data" in response or "error" in response

# Memory usage testing helpers
def get_memory_snapshot():
    """Get current memory usage snapshot."""
    return StateManager.get_memory_usage()

def assert_memory_increased(before: dict, after: dict):
    """Assert that memory usage increased."""
    assert after["portfolios_count"] >= before["portfolios_count"]
    assert after["symbols_count"] >= before["symbols_count"]

def assert_memory_cleared(memory_usage: dict):
    """Assert that memory has been cleared."""
    assert memory_usage["portfolios_count"] == 0
    assert memory_usage["symbols_count"] == 0
    assert memory_usage["total_entities"] == 0