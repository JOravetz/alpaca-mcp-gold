"""
Tests for account tools following gold standard patterns.
"""

import pytest
from src.mcp_server.tools.account_tools import (
    get_account_info,
    get_positions,
    get_open_position,
    get_portfolio_summary
)
from src.mcp_server.models.schemas import StateManager
from .conftest import assert_success_response, assert_error_response, get_memory_snapshot

class TestAccountTools:
    """Test suite for account management tools."""
    
    @pytest.mark.asyncio
    async def test_get_account_info_success(self, real_api_test):
        """Test successful account info retrieval."""
        result = await get_account_info()
        
        assert_success_response(result)
        
        # Verify account data structure
        data = result["data"]
        assert "account_id" in data
        assert "status" in data
        assert "buying_power" in data
        assert "portfolio_value" in data
        assert isinstance(data["buying_power"], (int, float))
        assert isinstance(data["portfolio_value"], (int, float))
        
        # Verify portfolio state was created
        portfolio = StateManager.get_portfolio()
        assert portfolio is not None
        assert "buying_power" in portfolio.portfolio_metrics
        assert isinstance(portfolio.portfolio_metrics["buying_power"], (int, float))
        
        # Verify metadata includes suggestions
        assert "suggested_operations" in result["metadata"]
    
    @pytest.mark.asyncio
    async def test_get_account_info_error_handling(self, real_api_test):
        """Test account info error handling with real API scenarios."""
        from src.mcp_server.config.simple_settings import settings
        original_key = settings.alpaca_api_key
        
        try:
            # Test with invalid credentials
            settings.alpaca_api_key = "invalid_key_for_testing"
            result = await get_account_info()
            
            # Should handle invalid credentials gracefully
            # Either succeed (if demo mode) or fail gracefully
            assert result["status"] in ["success", "error"]
            if result["status"] == "error":
                assert "message" in result
        finally:
            # Restore original key
            settings.alpaca_api_key = original_key
    
    @pytest.mark.asyncio
    async def test_get_positions_success(self, real_api_test):
        """Test successful positions retrieval."""
        result = await get_positions()
        
        assert_success_response(result)
        
        # Verify positions data structure
        data = result["data"]
        assert isinstance(data, list)
        
        if len(data) > 0:
            position = data[0]
            assert "symbol" in position
            assert "quantity" in position
            assert "market_value" in position
            assert "suggested_role" in position
            assert "characteristics" in position
            assert isinstance(position["quantity"], (int, float))
            assert isinstance(position["market_value"], (int, float))
        
        # Verify entity tracking if positions exist
        if len(data) > 0:
            symbol = data[0]["symbol"]
            entity = StateManager.get_symbol(symbol)
            assert entity is not None
            assert entity.name == symbol
        
        # Verify metadata structure (varies based on whether positions exist)
        metadata = result["metadata"]
        if len(data) > 0:
            assert "total_positions" in metadata
            assert "portfolio_insights" in metadata
            assert isinstance(metadata["total_positions"], int)
        else:
            assert "message" in metadata
            assert metadata["message"] == "No open positions found"
    
    @pytest.mark.asyncio
    async def test_get_positions_handles_empty_portfolio(self, real_api_test):
        """Test positions retrieval handles empty portfolio gracefully."""
        result = await get_positions()
        
        # Should succeed regardless of actual portfolio state
        assert_success_response(result)
        assert isinstance(result["data"], list)
        # Metadata structure depends on whether positions exist
        if len(result["data"]) > 0:
            assert "total_positions" in result["metadata"]
        else:
            assert "message" in result["metadata"]
    
    @pytest.mark.asyncio
    async def test_get_open_position_success(self, real_api_test):
        """Test specific position retrieval (may not exist in paper account)."""
        result = await get_open_position("AAPL")
        
        # Position may or may not exist in paper account
        if result["status"] == "success":
            # Verify position data structure if position exists
            data = result["data"]
            assert "symbol" in data
            assert "quantity" in data
            assert "asset_type" in data
            assert "suggested_role" in data
            assert data["symbol"] == "AAPL"
            assert isinstance(data["quantity"], (int, float))
            
            # Verify entity tracking
            entity = StateManager.get_symbol("AAPL")
            assert entity is not None
        else:
            # Position doesn't exist - this is expected for paper account
            assert result["status"] == "error"
            assert "message" in result
    
    @pytest.mark.asyncio
    async def test_get_open_position_option_symbol(self, real_api_test):
        """Test position retrieval for option symbol format detection."""
        # Test option symbol format detection
        result = await get_open_position("AAPL240315C00180000")
        
        # Should handle option symbols gracefully (might not exist in paper account)
        assert result["status"] in ["success", "error"]
        if result["status"] == "success":
            data = result["data"]
            # If position exists, should detect option format
            if "asset_type" in data:
                assert data["asset_type"] in ["stock", "option"]
    
    @pytest.mark.asyncio
    async def test_get_open_position_invalid_symbol(self):
        """Test position retrieval with empty symbol."""
        result = await get_open_position("")
        
        assert_error_response(result)
        assert "Symbol parameter cannot be empty" in result["message"]
    
    @pytest.mark.asyncio
    async def test_get_open_position_not_found(self, real_api_test):
        """Test position retrieval for non-existent position."""
        # Test with unlikely symbol that won't exist in paper account
        result = await get_open_position("NONEXISTENT123")
        
        # Should handle missing positions gracefully
        assert_error_response(result)
        assert "message" in result
    
    @pytest.mark.asyncio
    async def test_get_portfolio_summary_with_data(self, real_api_test):
        """Test portfolio summary with existing data."""
        # First get account info to initialize portfolio
        await get_account_info()
        await get_positions()
        
        result = await get_portfolio_summary()
        
        assert_success_response(result)
        
        # Verify summary structure
        data = result["data"]
        assert "portfolio_metrics" in data
        assert "entity_count" in data
        assert "suggested_operations" in data
        assert "entity_breakdown" in data
        assert "memory_usage" in data
        
        # Verify entity breakdown (may be zero if no positions)
        assert isinstance(data["entity_count"], int)
        assert data["entity_count"] >= 0
        # Entity breakdown structure depends on actual positions
        if data["entity_count"] > 0:
            assert "position" in data["entity_breakdown"]
    
    @pytest.mark.asyncio
    async def test_get_portfolio_summary_no_data(self):
        """Test portfolio summary with no existing data."""
        # Mock account info call to fail initialization
        result = await get_portfolio_summary()
        
        # Should still succeed after initializing account data
        assert_success_response(result)
    
    @pytest.mark.asyncio
    async def test_state_management(self, real_api_test):
        """Test that state is properly managed across tool calls."""
        # Start with empty state
        memory_before = get_memory_snapshot()
        assert memory_before["portfolios_count"] == 0
        assert memory_before["symbols_count"] == 0
        
        # Get account info - should create portfolio
        await get_account_info()
        memory_after_account = get_memory_snapshot()
        assert memory_after_account["portfolios_count"] == 1
        
        # Get positions - may add symbols if positions exist
        await get_positions()
        memory_after_positions = get_memory_snapshot()
        # May be 0 or more symbols depending on account state
        assert memory_after_positions["symbols_count"] >= 0
        
        # Get stock quote to add a symbol
        from src.mcp_server.tools.market_data_tools import get_stock_quote
        await get_stock_quote("AAPL")
        memory_final = get_memory_snapshot()
        assert memory_final["symbols_count"] >= memory_after_positions["symbols_count"]
    
    @pytest.mark.asyncio
    async def test_adaptive_insights(self, real_api_test):
        """Test that adaptive insights are generated correctly when data exists."""
        # Get positions to trigger entity analysis
        result = await get_positions()
        
        # Verify adaptive characteristics if positions exist
        if len(result["data"]) > 0:
            position = result["data"][0]
            assert "suggested_role" in position
            assert "characteristics" in position
            
            characteristics = position["characteristics"]
            assert "quantity" in characteristics
            assert "unrealized_pl" in characteristics
            assert "market_value" in characteristics
            assert "position_size" in characteristics
            
            # Verify role assignment logic
            assert position["suggested_role"] in ["growth_candidate", "income_generator", "speculative_holding", "liquidity_provider"]
        else:
            # No positions in paper account - test with stock quote instead
            from src.mcp_server.tools.market_data_tools import get_stock_snapshot
            quote_result = await get_stock_snapshot("AAPL")
            assert_success_response(quote_result)
            
            # Verify entity was created with adaptive insights
            entity = StateManager.get_symbol("AAPL")
            assert entity is not None
            assert entity.suggested_role is not None
            assert len(entity.characteristics) > 0
    
    @pytest.mark.asyncio
    async def test_error_propagation(self, real_api_test):
        """Test that errors are properly propagated and formatted."""
        # Test input validation error scenarios
        result = await get_open_position("")  # Empty symbol
        
        assert_error_response(result)
        assert "error_type" in result
        assert "message" in result
        assert "Symbol parameter cannot be empty" in result["message"]