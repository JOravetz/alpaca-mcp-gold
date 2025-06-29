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
    async def test_get_account_info_success(self, mock_alpaca_clients):
        """Test successful account info retrieval."""
        result = await get_account_info()
        
        assert_success_response(result)
        
        # Verify account data structure
        data = result["data"]
        assert data["account_id"] == "test_account_123"
        assert data["status"] == "ACTIVE"
        assert data["buying_power"] == 10000.0
        assert data["portfolio_value"] == 15000.0
        
        # Verify portfolio state was created
        portfolio = StateManager.get_portfolio()
        assert portfolio is not None
        assert portfolio.portfolio_metrics["buying_power"] == 10000.0
        
        # Verify metadata includes suggestions
        assert "suggested_operations" in result["metadata"]
    
    @pytest.mark.asyncio
    async def test_get_account_info_error_handling(self, mock_alpaca_clients):
        """Test account info error handling."""
        # Make the client raise an exception
        mock_alpaca_clients["trading"].get_account.side_effect = Exception("API Error")
        
        result = await get_account_info()
        
        assert_error_response(result)
        assert "API Error" in result["message"]
    
    @pytest.mark.asyncio
    async def test_get_positions_success(self, mock_alpaca_clients):
        """Test successful positions retrieval."""
        result = await get_positions()
        
        assert_success_response(result)
        
        # Verify positions data
        data = result["data"]
        assert len(data) == 1
        
        position = data[0]
        assert position["symbol"] == "AAPL"
        assert position["quantity"] == 100.0
        assert position["market_value"] == 15000.0
        assert "suggested_role" in position
        assert "characteristics" in position
        
        # Verify entity tracking
        entity = StateManager.get_symbol("AAPL")
        assert entity is not None
        assert entity.name == "AAPL"
        
        # Verify metadata
        metadata = result["metadata"]
        assert metadata["total_positions"] == 1
        assert "portfolio_insights" in metadata
    
    @pytest.mark.asyncio
    async def test_get_positions_empty(self, mock_alpaca_clients):
        """Test positions retrieval when no positions exist."""
        mock_alpaca_clients["trading"].get_all_positions.return_value = []
        
        result = await get_positions()
        
        assert_success_response(result)
        assert result["data"] == []
        assert result["metadata"]["message"] == "No open positions found"
    
    @pytest.mark.asyncio
    async def test_get_open_position_success(self, mock_alpaca_clients):
        """Test successful specific position retrieval."""
        result = await get_open_position("AAPL")
        
        assert_success_response(result)
        
        # Verify position data
        data = result["data"]
        assert data["symbol"] == "AAPL"
        assert data["quantity"] == 100.0
        assert data["asset_type"] == "stock"  # Not an option
        assert "suggested_role" in data
        
        # Verify entity tracking
        entity = StateManager.get_symbol("AAPL")
        assert entity is not None
    
    @pytest.mark.asyncio
    async def test_get_open_position_option_symbol(self, mock_alpaca_clients):
        """Test position retrieval for option symbol."""
        # Set up mock for option symbol
        mock_position = mock_alpaca_clients["trading"].get_open_position.return_value
        mock_position.symbol = "AAPL240315C00180000"  # Option symbol
        
        result = await get_open_position("AAPL240315C00180000")
        
        assert_success_response(result)
        data = result["data"]
        assert data["asset_type"] == "option"
        assert "contracts" in data["quantity_display"]
    
    @pytest.mark.asyncio
    async def test_get_open_position_invalid_symbol(self):
        """Test position retrieval with empty symbol."""
        result = await get_open_position("")
        
        assert_error_response(result)
        assert "Symbol parameter cannot be empty" in result["message"]
    
    @pytest.mark.asyncio
    async def test_get_open_position_not_found(self, mock_alpaca_clients):
        """Test position retrieval for non-existent position."""
        mock_alpaca_clients["trading"].get_open_position.side_effect = Exception("Position not found")
        
        result = await get_open_position("INVALID")
        
        assert_error_response(result)
        assert "Position not found" in result["message"]
    
    @pytest.mark.asyncio
    async def test_get_portfolio_summary_with_data(self, mock_alpaca_clients):
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
        
        # Verify entity breakdown
        assert data["entity_count"] > 0
        assert "position" in data["entity_breakdown"]
    
    @pytest.mark.asyncio
    async def test_get_portfolio_summary_no_data(self):
        """Test portfolio summary with no existing data."""
        # Mock account info call to fail initialization
        result = await get_portfolio_summary()
        
        # Should still succeed after initializing account data
        assert_success_response(result)
    
    @pytest.mark.asyncio
    async def test_state_management(self, mock_alpaca_clients):
        """Test that state is properly managed across tool calls."""
        # Start with empty state
        memory_before = get_memory_snapshot()
        assert memory_before["portfolios_count"] == 0
        assert memory_before["symbols_count"] == 0
        
        # Get account info - should create portfolio
        await get_account_info()
        memory_after_account = get_memory_snapshot()
        assert memory_after_account["portfolios_count"] == 1
        
        # Get positions - should add symbols
        await get_positions()
        memory_after_positions = get_memory_snapshot()
        assert memory_after_positions["symbols_count"] == 1
        
        # Get specific position - should not duplicate
        await get_open_position("AAPL")
        memory_final = get_memory_snapshot()
        assert memory_final["symbols_count"] == 1  # Still 1, not duplicated
    
    @pytest.mark.asyncio
    async def test_adaptive_insights(self, mock_alpaca_clients):
        """Test that adaptive insights are generated correctly."""
        # Get positions to trigger entity analysis
        result = await get_positions()
        
        position = result["data"][0]
        
        # Verify adaptive characteristics
        assert "suggested_role" in position
        assert "characteristics" in position
        
        characteristics = position["characteristics"]
        assert "quantity" in characteristics
        assert "unrealized_pl" in characteristics
        assert "market_value" in characteristics
        assert "position_size" in characteristics
        
        # Verify role assignment logic
        # With +500 unrealized P&L on 15000 market value, should be growth candidate
        assert position["suggested_role"] in ["growth_candidate", "income_generator"]
    
    @pytest.mark.asyncio
    async def test_error_propagation(self, mock_alpaca_clients):
        """Test that errors are properly propagated and formatted."""
        # Test various error scenarios
        mock_alpaca_clients["trading"].get_account.side_effect = ValueError("Invalid credentials")
        
        result = await get_account_info()
        
        assert_error_response(result)
        assert result["error_type"] == "ValueError"
        assert "Invalid credentials" in result["message"]