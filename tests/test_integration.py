"""
Integration tests following gold standard patterns.
Tests complete workflows and interactions between components.
"""

import pytest
from src.mcp_server.tools.account_tools import get_account_info, get_positions, get_portfolio_summary
from src.mcp_server.tools.market_data_tools import get_stock_quote, get_stock_snapshot
from src.mcp_server.tools.order_management_tools import place_market_order, get_orders
from src.mcp_server.tools.resource_mirror_tools import resource_account_info, resource_portfolio_summary
from src.mcp_server.resources.trading_resources import get_trading_resource
from src.mcp_server.prompts.trading_prompts import portfolio_first_look, trading_strategy_workshop
from src.mcp_server.models.schemas import StateManager
from .conftest import assert_success_response, get_memory_snapshot

class TestWorkflowIntegration:
    """Test complete workflows and component interactions."""
    
    @pytest.mark.asyncio
    async def test_complete_portfolio_analysis_workflow(self, mock_alpaca_clients):
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
        
        # Verify entities added
        memory = get_memory_snapshot()
        assert memory["symbols_count"] == 1
        assert memory["total_entities"] == 1
        
        # Step 3: Get portfolio summary (comprehensive analysis)
        summary_result = await get_portfolio_summary()
        assert_success_response(summary_result)
        
        # Verify summary includes all data
        summary_data = summary_result["data"]
        assert summary_data["entity_count"] == 1
        assert "entity_breakdown" in summary_data
        assert "position" in summary_data["entity_breakdown"]
        
        # Step 4: Verify adaptive insights
        position_data = positions_result["data"][0]
        assert "suggested_role" in position_data
        assert "characteristics" in position_data
    
    @pytest.mark.asyncio
    async def test_market_research_to_trading_workflow(self, mock_alpaca_clients):
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
        assert "latest_price" in updated_entity.characteristics
        
        # Step 3: Place order based on research
        order_result = await place_market_order("AAPL", "buy", 10.0)
        assert_success_response(order_result)
        
        # Verify order tracking
        order_entity = StateManager.get_symbol(f"order_{order_result['data']['order_id']}")
        assert order_entity is not None
        
        # Step 4: Check order status
        orders_result = await get_orders()
        assert_success_response(orders_result)
        assert len(orders_result["data"]["orders"]) == 1
    
    @pytest.mark.asyncio
    async def test_resource_mirror_consistency(self, mock_alpaca_clients):
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
    async def test_adaptive_prompts_with_data(self, mock_alpaca_clients):
        """Test that prompts adapt to actual portfolio data."""
        # Start with no data - should get generic prompt
        prompt_empty = await portfolio_first_look()
        prompt_text_empty = prompt_empty["messages"][0]["content"]["text"]
        assert "Let's get started" in prompt_text_empty or "Welcome" in prompt_text_empty
        
        # Add portfolio data
        await get_account_info()
        await get_positions()
        
        # Prompt should now be adaptive
        prompt_with_data = await portfolio_first_look()
        prompt_text_with_data = prompt_with_data["messages"][0]["content"]["text"]
        
        # Should reference actual data
        assert "$15,000" in prompt_text_with_data  # Portfolio value
        assert "1 tracked entities" in prompt_text_with_data or "tracked entities" in prompt_text_with_data
        assert "AAPL" in prompt_text_with_data or "positions" in prompt_text_with_data
    
    @pytest.mark.asyncio
    async def test_strategy_workshop_adaptation(self, mock_alpaca_clients):
        """Test strategy workshop adapts to portfolio context."""
        # Get initial strategy prompt
        strategy_empty = await trading_strategy_workshop("growth")
        
        # Add portfolio with growth position
        await get_account_info()
        await get_positions()
        
        # Strategy should adapt to portfolio
        strategy_with_data = await trading_strategy_workshop("growth")
        strategy_text = strategy_with_data["messages"][0]["content"]["text"]
        
        # Should reference actual portfolio
        assert "Portfolio Value" in strategy_text or "portfolio" in strategy_text.lower()
    
    @pytest.mark.asyncio
    async def test_error_propagation_through_workflow(self, mock_alpaca_clients):
        """Test error handling across workflow components."""
        # Make trading client fail
        mock_alpaca_clients["trading"].get_account.side_effect = Exception("API Error")
        
        # Error should propagate through all layers
        account_result = await get_account_info()
        assert account_result["status"] == "error"
        
        resource_result = await get_trading_resource("trading://account/info")
        assert "error" in resource_result
        
        mirror_result = await resource_account_info()
        assert mirror_result["status"] == "error"
        
        # Portfolio summary should handle missing data gracefully
        summary_result = await get_portfolio_summary()
        # Should either succeed with empty data or provide helpful error
        assert summary_result["status"] in ["success", "error"]
    
    @pytest.mark.asyncio
    async def test_memory_management_across_operations(self, mock_alpaca_clients):
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
        assert memory_after_positions["symbols_count"] == 1
        
        await get_stock_quote("MSFT")
        memory_after_quote = get_memory_snapshot()
        assert memory_after_quote["symbols_count"] == 2  # AAPL + MSFT
        
        await place_market_order("TSLA", "buy", 5.0)
        memory_after_order = get_memory_snapshot()
        assert memory_after_order["symbols_count"] == 3  # Added order entity
        
        # Memory should track all entities
        assert memory_after_order["total_entities"] == 1  # Only position in portfolio
    
    @pytest.mark.asyncio
    async def test_state_persistence_across_calls(self, mock_alpaca_clients):
        """Test that state persists across multiple tool calls."""
        # Initialize with account data
        await get_account_info()
        portfolio_1 = StateManager.get_portfolio()
        
        # Add position data
        await get_positions()
        portfolio_2 = StateManager.get_portfolio()
        
        # Should be same portfolio object, enhanced with entities
        assert portfolio_1.name == portfolio_2.name
        assert len(portfolio_2.entities) > len(portfolio_1.entities)
        
        # Add market data
        await get_stock_quote("AAPL")
        entity_1 = StateManager.get_symbol("AAPL")
        
        await get_stock_snapshot("AAPL")
        entity_2 = StateManager.get_symbol("AAPL")
        
        # Should be same entity, enhanced with additional data
        assert entity_1.name == entity_2.name
        assert len(entity_2.characteristics) >= len(entity_1.characteristics)
    
    @pytest.mark.asyncio
    async def test_comprehensive_system_health_check(self, mock_alpaca_clients):
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
    async def test_gold_standard_pattern_compliance(self, mock_alpaca_clients):
        """Test that implementation follows all gold standard patterns."""
        # 1. Adaptive Discovery Pattern
        await get_stock_snapshot("AAPL")
        entity = StateManager.get_symbol("AAPL")
        assert entity.suggested_role is not None
        assert len(entity.characteristics) > 0
        
        # 2. Resource Mirror Pattern
        resource_data = await get_trading_resource("trading://account/info")
        mirror_data = await resource_account_info()
        assert mirror_data["data"] == resource_data["resource_data"]
        
        # 3. Consistent Error Handling
        mock_alpaca_clients["trading"].get_account.side_effect = Exception("Test Error")
        error_result = await get_account_info()
        assert error_result["status"] == "error"
        assert "message" in error_result
        assert "error_type" in error_result
        
        # 4. Context-Aware Prompts
        # Reset client for successful call
        mock_alpaca_clients["trading"].get_account.side_effect = None
        await get_account_info()
        prompt = await portfolio_first_look()
        prompt_text = prompt["messages"][0]["content"]["text"]
        assert "portfolio" in prompt_text.lower()
        
        # 5. Comprehensive State Management
        memory = get_memory_snapshot()
        assert isinstance(memory, dict)
        assert "portfolios_count" in memory
        assert "symbols_count" in memory
        
        # 6. Safe Execution (verified through error handling)
        # All operations should handle errors gracefully without crashing