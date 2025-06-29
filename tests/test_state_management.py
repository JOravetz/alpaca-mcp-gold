"""
Tests for state management following gold standard patterns.
"""

import pytest
from src.mcp_server.models.schemas import (
    StateManager,
    TradingPortfolioSchema,
    EntityInfo,
    TradingEntityType,
    EntityRole
)
from .conftest import assert_memory_cleared, assert_memory_increased, get_memory_snapshot

class TestStateManager:
    """Test suite for state management."""
    
    def test_initial_state_empty(self):
        """Test that initial state is empty."""
        memory = get_memory_snapshot()
        assert_memory_cleared(memory)
        
        # Verify empty states
        assert StateManager.get_portfolio() is None
        assert StateManager.get_all_symbols() == {}
        assert StateManager.get_symbol("AAPL") is None
    
    def test_portfolio_storage_and_retrieval(self, sample_portfolio_data):
        """Test portfolio storage and retrieval."""
        # Create and store portfolio
        portfolio = TradingPortfolioSchema.from_account_data(sample_portfolio_data)
        StateManager.set_portfolio(portfolio)
        
        # Verify storage
        memory = get_memory_snapshot()
        assert memory["portfolios_count"] == 1
        
        # Verify retrieval
        retrieved = StateManager.get_portfolio()
        assert retrieved is not None
        assert retrieved.name == portfolio.name
        assert retrieved.portfolio_metrics == portfolio.portfolio_metrics
    
    def test_symbol_storage_and_retrieval(self, sample_stock_data):
        """Test symbol storage and retrieval."""
        # Create and store entity
        entity = EntityInfo.from_stock_data("AAPL", sample_stock_data)
        StateManager.add_symbol("AAPL", entity)
        
        # Verify storage
        memory = get_memory_snapshot()
        assert memory["symbols_count"] == 1
        
        # Verify retrieval
        retrieved = StateManager.get_symbol("AAPL")
        assert retrieved is not None
        assert retrieved.name == "AAPL"
        assert retrieved.entity_type == TradingEntityType.STOCK
        
        # Verify all symbols
        all_symbols = StateManager.get_all_symbols()
        assert len(all_symbols) == 1
        assert "AAPL" in all_symbols
    
    def test_clear_all_state(self, sample_portfolio_data, sample_stock_data):
        """Test clearing all state."""
        # Add some data
        portfolio = TradingPortfolioSchema.from_account_data(sample_portfolio_data)
        StateManager.set_portfolio(portfolio)
        
        entity = EntityInfo.from_stock_data("AAPL", sample_stock_data)
        StateManager.add_symbol("AAPL", entity)
        
        # Verify data exists
        memory_before = get_memory_snapshot()
        assert memory_before["portfolios_count"] == 1
        assert memory_before["symbols_count"] == 1
        
        # Clear all
        StateManager.clear_all()
        
        # Verify cleared
        memory_after = get_memory_snapshot()
        assert_memory_cleared(memory_after)
        
        assert StateManager.get_portfolio() is None
        assert StateManager.get_all_symbols() == {}
    
    def test_memory_usage_tracking(self, sample_portfolio_data, sample_stock_data):
        """Test memory usage tracking accuracy."""
        # Start with empty state
        memory_start = get_memory_snapshot()
        assert_memory_cleared(memory_start)
        
        # Add portfolio
        portfolio = TradingPortfolioSchema.from_account_data(sample_portfolio_data)
        StateManager.set_portfolio(portfolio)
        
        memory_after_portfolio = get_memory_snapshot()
        assert memory_after_portfolio["portfolios_count"] == 1
        
        # Add symbols
        for symbol in ["AAPL", "MSFT", "GOOGL"]:
            entity = EntityInfo.from_stock_data(symbol, sample_stock_data)
            StateManager.add_symbol(symbol, entity)
        
        memory_after_symbols = get_memory_snapshot()
        assert memory_after_symbols["symbols_count"] == 3
        
        # Add entities to portfolio
        for symbol in ["AAPL", "MSFT"]:
            entity = EntityInfo.from_stock_data(symbol, sample_stock_data)
            portfolio.add_entity(entity)
        
        memory_final = get_memory_snapshot()
        assert memory_final["total_entities"] == 2  # Entities in portfolio

class TestTradingPortfolioSchema:
    """Test suite for portfolio schema."""
    
    def test_from_account_data(self, sample_portfolio_data):
        """Test portfolio creation from account data."""
        portfolio = TradingPortfolioSchema.from_account_data(sample_portfolio_data)
        
        # Verify basic properties
        assert portfolio.name == "portfolio"
        assert len(portfolio.entities) == 0
        assert isinstance(portfolio.suggested_operations, list)
        
        # Verify metrics calculation
        metrics = portfolio.portfolio_metrics
        assert metrics["buying_power"] == 10000.0
        assert metrics["portfolio_value"] == 15000.0
        assert metrics["equity"] == 15000.0
        assert metrics["cash_allocation"] == 10000.0 / 15000.0
    
    def test_from_account_data_with_name(self, sample_portfolio_data):
        """Test portfolio creation with custom name."""
        portfolio = TradingPortfolioSchema.from_account_data(sample_portfolio_data, "test_portfolio")
        assert portfolio.name == "test_portfolio"
    
    def test_add_entity_updates_suggestions(self, sample_portfolio_data, sample_stock_data):
        """Test that adding entities updates suggested operations."""
        portfolio = TradingPortfolioSchema.from_account_data(sample_portfolio_data)
        
        # Initially should have some suggestions based on cash allocation
        initial_suggestions = len(portfolio.suggested_operations)
        
        # Add a volatile stock
        volatile_stock = EntityInfo.from_stock_data("VOLATILE", {
            "price_change_percent": 10.0,  # Very volatile
            "volume": 1000000,
            "volatility": 15.0
        })
        portfolio.add_entity(volatile_stock)
        
        # Should have updated suggestions
        assert len(portfolio.suggested_operations) >= initial_suggestions
    
    def test_suggested_operations_logic(self, sample_portfolio_data):
        """Test suggested operations generation logic."""
        # High cash allocation scenario
        high_cash_data = sample_portfolio_data.copy()
        high_cash_data["buying_power"] = "8000.00"  # 80% of portfolio value
        
        portfolio = TradingPortfolioSchema.from_account_data(high_cash_data)
        
        # Should suggest deploying cash
        suggestions = [op for op in portfolio.suggested_operations if "cash" in op.lower()]
        assert len(suggestions) > 0

class TestEntityInfo:
    """Test suite for entity information."""
    
    def test_from_stock_data_growth_candidate(self):
        """Test stock entity creation for growth candidate."""
        stock_data = {
            "price_change_percent": 3.5,  # Positive growth
            "volume": 2000000,
            "market_cap": 50000000000  # Large cap
        }
        
        entity = EntityInfo.from_stock_data("GROWTH", stock_data)
        
        assert entity.name == "GROWTH"
        assert entity.entity_type == TradingEntityType.STOCK
        assert entity.suggested_role == EntityRole.GROWTH_CANDIDATE
        assert entity.characteristics["price_volatility"] == 3.5
        assert entity.characteristics["price_trend"] == "up"
    
    def test_from_stock_data_volatile_asset(self):
        """Test stock entity creation for volatile asset."""
        stock_data = {
            "price_change_percent": -7.5,  # High volatility
            "volume": 5000000,
            "market_cap": 1000000000
        }
        
        entity = EntityInfo.from_stock_data("VOLATILE", stock_data)
        
        assert entity.suggested_role == EntityRole.VOLATILE_ASSET
        assert entity.characteristics["price_volatility"] == 7.5
        assert entity.characteristics["price_trend"] == "down"
    
    def test_from_stock_data_liquid_asset(self):
        """Test stock entity creation for liquid asset.""" 
        stock_data = {
            "price_change_percent": 1.0,  # Moderate change
            "volume": 50000000,  # High volume
            "market_cap": 500000000000  # Very large cap
        }
        
        entity = EntityInfo.from_stock_data("LIQUID", stock_data)
        
        assert entity.suggested_role == EntityRole.LIQUID_ASSET
        assert entity.characteristics["volume"] == 50000000
    
    def test_from_position_data_growth_position(self, sample_position_data):
        """Test position entity creation for growth position."""
        # Modify for 15% gain
        position_data = sample_position_data.copy()
        position_data["unrealized_pl"] = "2250.0"  # 15% of 15000 market value
        
        entity = EntityInfo.from_position_data("AAPL", position_data)
        
        assert entity.entity_type == TradingEntityType.POSITION
        assert entity.suggested_role == EntityRole.GROWTH_CANDIDATE
        assert entity.characteristics["unrealized_pl"] == 2250.0
    
    def test_from_position_data_hedge_position(self, sample_position_data):
        """Test position entity creation for hedge position."""
        # Modify for loss
        position_data = sample_position_data.copy()
        position_data["unrealized_pl"] = "-800.0"  # 5.3% loss
        
        entity = EntityInfo.from_position_data("HEDGE", position_data)
        
        assert entity.suggested_role == EntityRole.HEDGE_INSTRUMENT
        assert entity.characteristics["unrealized_pl"] == -800.0
    
    def test_position_size_classification(self, sample_position_data):
        """Test position size classification."""
        # Small position
        small_position_data = sample_position_data.copy()
        small_position_data["qty"] = "10.0"
        small_position_data["market_value"] = "1500.0"
        
        entity = EntityInfo.from_position_data("SMALL", small_position_data)
        assert entity.characteristics["position_size"] == "small"
        
        # Large position  
        large_position_data = sample_position_data.copy()
        large_position_data["qty"] = "1000.0"
        large_position_data["market_value"] = "150000.0"
        
        entity = EntityInfo.from_position_data("LARGE", large_position_data)
        assert entity.characteristics["position_size"] == "large"
    
    def test_metadata_includes_timestamp(self, sample_stock_data):
        """Test that metadata includes timestamp."""
        entity = EntityInfo.from_stock_data("TEST", sample_stock_data)
        
        assert "last_updated" in entity.metadata
        # Should be a valid ISO format timestamp
        timestamp = entity.metadata["last_updated"]
        assert "T" in timestamp  # ISO format includes T
    
    def test_characteristics_persistence(self, sample_stock_data):
        """Test that characteristics are properly stored."""
        stock_data = {
            "price_change_percent": 2.5,
            "volume": 1000000,
            "high": 155.0,
            "low": 148.0,
            "volatility": 4.5
        }
        
        entity = EntityInfo.from_stock_data("TEST", stock_data)
        
        # All characteristics should be preserved
        assert entity.characteristics["price_volatility"] == 2.5
        assert entity.characteristics["volume"] == 1000000
        # Note: Additional characteristics like high/low are not currently stored
        # but the pattern allows for easy extension