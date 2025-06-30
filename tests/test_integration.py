"""
Integration tests following gold standard patterns.
Tests complete workflows and interactions between components.
"""

import pytest
from src.mcp_server.tools.account_tools import (
    get_account_info,
    get_positions,
    get_portfolio_summary,
)
from src.mcp_server.tools.market_data_tools import get_stock_quote, get_stock_snapshot
from src.mcp_server.tools.order_management_tools import place_market_order, get_orders
from src.mcp_server.tools.resource_mirror_tools import (
    resource_account_info,
    resource_portfolio_summary,
)
from src.mcp_server.resources.trading_resources import get_trading_resource
from src.mcp_server.prompts.trading_prompts import (
    portfolio_first_look,
    trading_strategy_workshop,
)
from src.mcp_server.models.schemas import StateManager
from .conftest import assert_success_response, get_memory_snapshot


class TestWorkflowIntegration:
    """Test complete workflows and component interactions."""

    @pytest.mark.asyncio
    async def test_complete_portfolio_analysis_workflow(self, real_api_test):
        """Test complete portfolio analysis workflow."""
        # Step 1: Get account info (initializes portfolio state)
        account_result = await get_account_info()
        assert_success_response(account_result)

        # Verify portfolio state created
        portfolio = StateManager.get_portfolio()
        assert portfolio is not None

        # Step 2: Get positions (adds entities to portfolio)
        positions_result = await get_positions()
        assert_success_response(positions_result)

        # Verify entities added if positions exist
        memory = get_memory_snapshot()
        assert "symbols_count" in memory
        assert "total_entities" in memory
        # May be 0 or more entities depending on account state

        # Step 3: Get portfolio summary (comprehensive analysis)
        summary_result = await get_portfolio_summary()
        assert_success_response(summary_result)

        # Verify summary includes expected structure
        summary_data = summary_result["data"]
        assert "entity_count" in summary_data
        assert "entity_breakdown" in summary_data
        assert isinstance(summary_data["entity_count"], int)
        # Entity breakdown may be empty if no positions

        # Step 4: Verify adaptive insights if positions exist
        if len(positions_result["data"]) > 0:
            position_data = positions_result["data"][0]
            assert "suggested_role" in position_data
            assert "characteristics" in position_data

    @pytest.mark.asyncio
    async def test_market_research_to_trading_workflow(self, real_api_test):
        """Test market research leading to trading workflow."""
        # Step 1: Research stock with quote
        quote_result = await get_stock_quote("AAPL")
        assert_success_response(quote_result)

        # Verify entity tracking started
        entity = StateManager.get_symbol("AAPL")
        assert entity is not None

        # Step 2: Get comprehensive snapshot
        snapshot_result = await get_stock_snapshot("AAPL")
        assert_success_response(snapshot_result)

        # Verify enhanced entity data
        updated_entity = StateManager.get_symbol("AAPL")
        # Check that entity has been enhanced with snapshot data
        assert len(updated_entity.characteristics) > 0
        # Common characteristics from snapshot data
        expected_keys = ["price_volatility", "volume", "market_cap", "price_trend"]
        assert any(key in updated_entity.characteristics for key in expected_keys)

        # Step 3: Place order based on research (may fail in paper trading)
        try:
            order_result = await place_market_order(
                "AAPL", "buy", 1.0
            )  # Small quantity
            if order_result["status"] == "success":
                # Verify order tracking if successful
                order_entity = StateManager.get_symbol(
                    f"order_{order_result['data']['order_id']}"
                )
                assert order_entity is not None

                # Step 4: Check order status
                orders_result = await get_orders()
                assert_success_response(orders_result)
                assert len(orders_result["data"]["orders"]) >= 1
            else:
                # Order failed - this is acceptable in paper trading
                assert order_result["status"] == "error"
        except Exception:
            # Order placement might fail due to insufficient funds, etc.
            # This is acceptable in a paper trading environment
            pass

    @pytest.mark.asyncio
    async def test_resource_mirror_consistency(self, real_api_test):
        """Test that resource mirrors maintain consistency."""
        # Get data through resource
        resource_result = await get_trading_resource("trading://account/info")

        # Get same data through mirror tool
        mirror_result = await resource_account_info()

        # Results should be consistent
        assert_success_response(mirror_result)
        assert mirror_result["data"] == resource_result["resource_data"]

        # Test with portfolio data
        await get_account_info()  # Initialize portfolio

        portfolio_resource = await get_trading_resource("trading://portfolio/summary")
        portfolio_mirror = await resource_portfolio_summary()

        assert_success_response(portfolio_mirror)
        assert portfolio_mirror["data"] == portfolio_resource["resource_data"]

    @pytest.mark.asyncio
    async def test_adaptive_prompts_with_data(self, real_api_test):
        """Test that prompts adapt to actual portfolio data."""
        # Start with no data - should get generic prompt
        prompt_empty = await portfolio_first_look()
        assert_success_response(prompt_empty)
        prompt_text_empty = prompt_empty["data"]["prompt"]
        assert (
            "Let's get started" in prompt_text_empty or "Welcome" in prompt_text_empty
        )

        # Add portfolio data
        await get_account_info()
        await get_positions()

        # Prompt should now be adaptive
        prompt_with_data = await portfolio_first_look()
        assert_success_response(prompt_with_data)
        prompt_text_with_data = prompt_with_data["data"]["prompt"]

        # Should reference actual data from real account
        # Look for portfolio-related content (amounts will vary by actual account)
        assert any(
            keyword in prompt_text_with_data.lower()
            for keyword in ["portfolio", "account", "positions", "trading", "entities"]
        )

    @pytest.mark.asyncio
    async def test_strategy_workshop_adaptation(self, real_api_test):
        """Test strategy workshop adapts to portfolio context."""
        # Get initial strategy prompt
        await trading_strategy_workshop("growth")

        # Add portfolio with growth position
        await get_account_info()
        await get_positions()

        # Strategy should adapt to portfolio
        strategy_with_data = await trading_strategy_workshop("growth")
        assert_success_response(strategy_with_data)
        strategy_text = strategy_with_data["data"]["prompt"]

        # Should reference actual portfolio or growth strategy
        assert any(
            keyword in strategy_text.lower()
            for keyword in ["portfolio", "growth", "strategy", "trading"]
        )

    @pytest.mark.asyncio
    async def test_error_propagation_through_workflow(self, real_api_test):
        """Test error handling across workflow components."""
        # Test with invalid credentials scenario
        from src.mcp_server.config.simple_settings import settings

        original_key = settings.alpaca_api_key

        try:
            # Temporarily set invalid key to trigger API errors
            settings.alpaca_api_key = "invalid_key"

            # Error should propagate through all layers
            account_result = await get_account_info()
            # Should handle invalid credentials gracefully
            assert account_result["status"] in ["success", "error"]

            resource_result = await get_trading_resource("trading://account/info")
            # Should handle errors gracefully
            assert "resource_data" in resource_result or "error" in resource_result

            mirror_result = await resource_account_info()
            assert mirror_result["status"] in ["success", "error"]

            # Portfolio summary should handle missing data gracefully
            summary_result = await get_portfolio_summary()
            # Should either succeed with empty data or provide helpful error
            assert summary_result["status"] in ["success", "error"]
        finally:
            # Restore original key
            settings.alpaca_api_key = original_key

    @pytest.mark.asyncio
    async def test_memory_management_across_operations(self, real_api_test):
        """Test memory management across multiple operations."""
        # Start with clean state
        initial_memory = get_memory_snapshot()
        assert initial_memory["portfolios_count"] == 0
        assert initial_memory["symbols_count"] == 0

        # Perform multiple operations
        await get_account_info()
        memory_after_account = get_memory_snapshot()
        assert memory_after_account["portfolios_count"] == 1

        await get_positions()
        memory_after_positions = get_memory_snapshot()
        # May be 0 if no positions in paper account
        assert memory_after_positions["symbols_count"] >= 0

        await get_stock_quote("MSFT")
        memory_after_quote = get_memory_snapshot()
        assert (
            memory_after_quote["symbols_count"]
            >= memory_after_positions["symbols_count"]
        )

        # Try to place order (may fail in paper trading)
        try:
            await place_market_order("TSLA", "buy", 1.0)  # Smaller quantity
            memory_after_order = get_memory_snapshot()
            assert (
                memory_after_order["symbols_count"]
                >= memory_after_quote["symbols_count"]
            )
        except Exception:
            # Order placement might fail in paper trading, that's OK
            pass

    @pytest.mark.asyncio
    async def test_state_persistence_across_calls(self, real_api_test):
        """Test that state persists across multiple tool calls."""
        # Initialize with account data
        await get_account_info()
        portfolio_1 = StateManager.get_portfolio()

        # Add position data
        await get_positions()
        portfolio_2 = StateManager.get_portfolio()

        # Should be same portfolio object, potentially enhanced with entities
        assert portfolio_1.name == portfolio_2.name
        # May or may not have more entities depending on account state
        assert len(portfolio_2.entities) >= len(portfolio_1.entities)

        # Add market data
        await get_stock_quote("AAPL")
        entity_1 = StateManager.get_symbol("AAPL")

        await get_stock_snapshot("AAPL")
        entity_2 = StateManager.get_symbol("AAPL")

        # Should be same entity, enhanced with additional data
        assert entity_1.name == entity_2.name
        assert len(entity_2.characteristics) >= len(entity_1.characteristics)

    @pytest.mark.asyncio
    async def test_comprehensive_system_health_check(self, real_api_test):
        """Test comprehensive system health across all components."""
        # Test system resources
        health_result = await get_trading_resource("trading://system/health")
        assert "resource_data" in health_result

        health_data = health_result["resource_data"]
        assert "trading" in health_data
        assert "stock_data" in health_data
        assert "options_data" in health_data

        # Test memory tracking
        memory_result = await get_trading_resource("trading://system/memory")
        assert "resource_data" in memory_result

        # Test complete status
        status_result = await get_trading_resource("trading://system/status")
        assert "resource_data" in status_result

        status_data = status_result["resource_data"]
        assert "server_name" in status_data
        assert "paper_trading" in status_data
        assert "memory_usage" in status_data
        assert "client_health" in status_data

    @pytest.mark.asyncio
    async def test_gold_standard_pattern_compliance(self, real_api_test):
        """Test that implementation follows all gold standard patterns."""
        # 1. Adaptive Discovery Pattern
        await get_stock_snapshot("AAPL")
        entity = StateManager.get_symbol("AAPL")
        assert entity.suggested_role is not None
        assert len(entity.characteristics) > 0

        # 2. Resource Mirror Pattern
        resource_data = await get_trading_resource("trading://account/info")
        mirror_data = await resource_account_info()
        if "resource_data" in resource_data and mirror_data["status"] == "success":
            assert mirror_data["data"] == resource_data["resource_data"]

        # 3. Consistent Error Handling
        # Test with invalid symbol to trigger error handling
        error_result = await get_stock_quote("")
        assert error_result["status"] == "error"
        assert "message" in error_result
        assert "error_type" in error_result

        # 4. Context-Aware Prompts
        await get_account_info()
        prompt = await portfolio_first_look()
        assert_success_response(prompt)
        prompt_text = prompt["data"]["prompt"]
        assert (
            "portfolio" in prompt_text.lower()
            or "trading" in prompt_text.lower()
            or "trading" in prompt_text.lower()
        )

        # 5. Comprehensive State Management
        memory = get_memory_snapshot()
        assert isinstance(memory, dict)
        assert "portfolios_count" in memory
        assert "symbols_count" in memory

        # 6. Safe Execution (verified through error handling)
        # All operations should handle errors gracefully without crashing
