"""
Test configuration and fixtures for real Alpaca API testing.
Uses real API calls to Alpaca paper trading environment.
"""

import pytest
import asyncio
import logging
from src.mcp_server.models.schemas import StateManager

logger = logging.getLogger(__name__)


async def cancel_all_orders():
    """
    Cancel all pending orders for test cleanup.
    Ensures no orders are left hanging after test runs.
    """
    try:
        from src.mcp_server.tools.order_management_tools import get_orders, cancel_order
        
        # Get all open orders
        orders_result = await get_orders(status="open")
        
        if orders_result["status"] == "success" and orders_result["data"]["orders"]:
            order_ids = [order["order_id"] for order in orders_result["data"]["orders"]]
            
            logger.info(f"Cancelling {len(order_ids)} pending orders during test cleanup")
            
            # Cancel each order
            for order_id in order_ids:
                cancel_result = await cancel_order(order_id)
                if cancel_result["status"] == "success":
                    logger.info(f"Successfully cancelled order {order_id}")
                else:
                    logger.warning(f"Failed to cancel order {order_id}: {cancel_result.get('message', 'Unknown error')}")
        else:
            logger.info("No pending orders found during cleanup")
            
    except Exception as e:
        logger.warning(f"Error during order cleanup: {e}")


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
def sample_portfolio_data():
    """Sample portfolio data for testing."""
    return {
        "buying_power": "10000.00",
        "portfolio_value": "15000.00",
        "equity": "15000.00",
        "cash": "5000.00",
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
        "unrealized_plpc": "0.0345",
    }


@pytest.fixture
def sample_stock_data():
    """Sample stock data for testing."""
    return {
        "price_change_percent": 2.5,
        "volume": 50000000,
        "high": 151.0,
        "low": 147.5,
        "volatility": 2.0,
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


# Real API testing helpers
def skip_if_no_credentials():
    """Skip test if no valid Alpaca credentials are available."""
    try:
        from src.mcp_server.config.simple_settings import settings

        if not settings.alpaca_api_key or not settings.alpaca_secret_key:
            pytest.skip("No Alpaca API credentials configured")
        if settings.alpaca_api_key in ["demo_key_please_replace", "test_key"]:
            pytest.skip(
                "Demo/test credentials detected - real API calls require valid credentials"
            )
        if settings.alpaca_secret_key in ["demo_secret_please_replace", "test_secret"]:
            pytest.skip(
                "Demo/test credentials detected - real API calls require valid credentials"
            )
    except Exception as e:
        pytest.skip(f"Configuration error: {e}")


@pytest.fixture(autouse=True)
def ensure_paper_trading():
    """Ensure we're using paper trading environment for safety."""
    from src.mcp_server.config.simple_settings import settings

    if not settings.alpaca_paper_trade:
        pytest.skip("Tests must run in paper trading mode for safety")


@pytest.fixture
def real_api_test():
    """Fixture that ensures real API credentials and skips if not available."""
    skip_if_no_credentials()
    return True


@pytest.fixture(scope="session", autouse=True)
def cleanup_orders_after_all_tests():
    """
    Session-scoped fixture to clean up orders after all tests complete.
    Automatically cancels any pending orders at the end of the test session.
    """
    yield  # Let all tests run first
    
    # After all tests are done, clean up any remaining orders
    try:
        # Run the cleanup in an event loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(cancel_all_orders())
        loop.close()
        logger.info("✅ Order cleanup completed after test session")
    except Exception as e:
        logger.error(f"❌ Error during final order cleanup: {e}")


@pytest.fixture(scope="function")
def order_cleanup():
    """
    Function-scoped fixture for tests that create orders.
    Provides immediate cleanup after individual tests.
    """
    yield
    # Clean up any orders created during this specific test
    try:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(cancel_all_orders())
    except Exception as e:
        logger.warning(f"Error during test-specific order cleanup: {e}")
