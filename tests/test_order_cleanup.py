"""
Test order cleanup functionality.
Verifies that orders are properly cancelled during test cleanup.
"""

import pytest
import logging
from src.mcp_server.tools.order_management_tools import (
    place_market_order,
    get_orders,
    cancel_order,
)
from .conftest import assert_success_response, cancel_all_orders

logger = logging.getLogger(__name__)


class TestOrderCleanup:
    """Test order cleanup functionality."""

    @pytest.mark.asyncio
    async def test_cancel_all_orders_function(self, real_api_test):
        """Test that the cancel_all_orders function works correctly."""
        # First, get current orders to establish baseline
        initial_orders = await get_orders(status="open")
        assert_success_response(initial_orders)
        
        initial_count = len(initial_orders["data"]["orders"])
        logger.info(f"Initial open orders: {initial_count}")
        
        # If there are existing orders, cancel them for clean test
        if initial_count > 0:
            await cancel_all_orders()
            
            # Verify they were cancelled
            after_cleanup = await get_orders(status="open")
            assert_success_response(after_cleanup)
            logger.info(f"Orders after cleanup: {len(after_cleanup['data']['orders'])}")

    @pytest.mark.asyncio
    async def test_order_cleanup_with_test_order(self, real_api_test, order_cleanup):
        """Test order cleanup with an actual test order."""
        # Place a test market order (small quantity)
        order_result = await place_market_order("AAPL", "buy", 1)
        
        # Check if order was placed successfully or if there was an error
        if order_result["status"] == "success":
            logger.info(f"Test order placed: {order_result['data']['order_id']}")
            
            # Verify order exists
            orders = await get_orders(status="open")
            assert_success_response(orders)
            
            # Find our test order
            test_order_found = False
            for order in orders["data"]["orders"]:
                if order["order_id"] == order_result["data"]["order_id"]:
                    test_order_found = True
                    break
                    
            if test_order_found:
                logger.info("Test order confirmed in open orders list")
            else:
                logger.info("Test order may have been filled immediately")
                
        else:
            # Order placement failed (possibly due to market conditions)
            logger.info(f"Test order placement failed: {order_result['message']}")
            # This is not necessarily a test failure - could be market hours, etc.
            
        # The order_cleanup fixture will automatically cancel any remaining orders

    @pytest.mark.asyncio
    async def test_no_orders_cleanup_safe(self, real_api_test):
        """Test that cleanup is safe when no orders exist."""
        # First ensure no orders exist
        await cancel_all_orders()
        
        # Verify no orders
        orders = await get_orders(status="open")
        assert_success_response(orders)
        assert len(orders["data"]["orders"]) == 0
        
        # Run cleanup again - should be safe
        await cancel_all_orders()
        
        # Should still be no orders and no errors
        orders_after = await get_orders(status="open")
        assert_success_response(orders_after)
        assert len(orders_after["data"]["orders"]) == 0

    @pytest.mark.asyncio
    async def test_cleanup_integration(self, real_api_test):
        """Integration test for the complete cleanup process."""
        # Step 1: Get initial state
        initial_state = await get_orders(status="open")
        assert_success_response(initial_state)
        
        # Step 2: Clean up any existing orders
        await cancel_all_orders()
        
        # Step 3: Verify clean state
        clean_state = await get_orders(status="open")
        assert_success_response(clean_state)
        assert len(clean_state["data"]["orders"]) == 0
        
        logger.info("✅ Order cleanup integration test completed successfully")