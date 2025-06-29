"""
Data models and schemas for Alpaca MCP server.
Follows gold standard adaptive discovery patterns.
"""

from datetime import datetime, date
from typing import Dict, List, Optional, Any, Union
from pydantic import BaseModel, Field
from enum import Enum

class TradingEntityType(str, Enum):
    """Types of trading entities we can analyze."""
    STOCK = "stock"
    OPTION = "option"
    POSITION = "position"
    ORDER = "order"
    WATCHLIST = "watchlist"
    
class EntityRole(str, Enum):
    """Suggested roles for trading entities based on characteristics."""
    LIQUID_ASSET = "liquid_asset"
    VOLATILE_ASSET = "volatile_asset"
    INCOME_GENERATOR = "income_generator"
    GROWTH_CANDIDATE = "growth_candidate"
    HEDGE_INSTRUMENT = "hedge_instrument"
    SPECULATIVE = "speculative"

class EntityInfo(BaseModel):
    """Information about a trading entity with adaptive characteristics."""
    name: str
    entity_type: TradingEntityType
    characteristics: Dict[str, Any] = Field(default_factory=dict)
    suggested_role: EntityRole
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    @classmethod
    def from_stock_data(cls, symbol: str, data: Dict[str, Any]) -> 'EntityInfo':
        """Auto-discover stock characteristics from market data."""
        # Analyze price volatility
        price_change = data.get('price_change_percent', 0)
        volume = data.get('volume', 0)
        market_cap = data.get('market_cap', 0)
        
        # Determine suggested role based on characteristics
        if abs(price_change) > 5:
            role = EntityRole.VOLATILE_ASSET
        elif volume > 1000000 and market_cap > 10000000000:  # High volume, large cap
            role = EntityRole.LIQUID_ASSET
        elif price_change > 2:
            role = EntityRole.GROWTH_CANDIDATE
        else:
            role = EntityRole.INCOME_GENERATOR
            
        return cls(
            name=symbol,
            entity_type=TradingEntityType.STOCK,
            characteristics={
                "price_volatility": abs(price_change),
                "volume": volume,
                "market_cap": market_cap,
                "price_trend": "up" if price_change > 0 else "down"
            },
            suggested_role=role,
            metadata={"last_updated": datetime.now().isoformat()}
        )
    
    @classmethod
    def from_position_data(cls, symbol: str, data: Dict[str, Any]) -> 'EntityInfo':
        """Auto-discover position characteristics."""
        qty = float(data.get('qty', 0))
        unrealized_pl = float(data.get('unrealized_pl', 0))
        market_value = float(data.get('market_value', 0))
        
        # Determine role based on position characteristics
        if unrealized_pl > market_value * 0.1:  # 10%+ gain
            role = EntityRole.GROWTH_CANDIDATE
        elif unrealized_pl < -market_value * 0.05:  # 5%+ loss
            role = EntityRole.HEDGE_INSTRUMENT
        else:
            role = EntityRole.INCOME_GENERATOR
            
        return cls(
            name=symbol,
            entity_type=TradingEntityType.POSITION,
            characteristics={
                "quantity": qty,
                "unrealized_pl": unrealized_pl,
                "market_value": market_value,
                "position_size": "large" if abs(qty * market_value) > 10000 else "small"
            },
            suggested_role=role,
            metadata={"last_updated": datetime.now().isoformat()}
        )

class TradingPortfolioSchema(BaseModel):
    """Schema representing the overall trading portfolio with adaptive insights."""
    name: str
    entities: Dict[str, EntityInfo] = Field(default_factory=dict)
    suggested_operations: List[str] = Field(default_factory=list)
    portfolio_metrics: Dict[str, Any] = Field(default_factory=dict)
    last_updated: datetime = Field(default_factory=datetime.now)
    
    @classmethod
    def from_account_data(cls, account_data: Dict[str, Any], name: str = "portfolio") -> 'TradingPortfolioSchema':
        """Auto-discover portfolio characteristics from account data."""
        buying_power = float(account_data.get('buying_power', 0))
        portfolio_value = float(account_data.get('portfolio_value', 0))
        equity = float(account_data.get('equity', 0))
        
        # Generate suggested operations based on portfolio state
        suggested_ops = []
        if buying_power > portfolio_value * 0.5:
            suggested_ops.append("Consider deploying excess cash in diversified positions")
        if equity > portfolio_value * 0.9:
            suggested_ops.append("Portfolio is well-capitalized for growth strategies")
            
        return cls(
            name=name,
            portfolio_metrics={
                "buying_power": buying_power,
                "portfolio_value": portfolio_value,
                "equity": equity,
                "cash_allocation": buying_power / portfolio_value if portfolio_value > 0 else 0
            },
            suggested_operations=suggested_ops
        )
    
    def add_entity(self, entity: EntityInfo):
        """Add a trading entity to the portfolio."""
        self.entities[entity.name] = entity
        self._update_suggested_operations()
        
    def _update_suggested_operations(self):
        """Update suggested operations based on current entities."""
        operations = []
        
        # Analyze by entity type
        stocks = [e for e in self.entities.values() if e.entity_type == TradingEntityType.STOCK]
        positions = [e for e in self.entities.values() if e.entity_type == TradingEntityType.POSITION]
        
        if len(stocks) > 0:
            volatile_stocks = [s for s in stocks if s.suggested_role == EntityRole.VOLATILE_ASSET]
            if len(volatile_stocks) > len(stocks) * 0.3:
                operations.append("High volatility detected - consider risk management strategies")
                
        if len(positions) > 0:
            large_positions = [p for p in positions if p.characteristics.get('position_size') == 'large']
            if len(large_positions) > 3:
                operations.append("Multiple large positions - consider diversification review")
                
        self.suggested_operations = operations

class StateManager:
    """Centralized state management following gold standard patterns."""
    
    _portfolios: Dict[str, TradingPortfolioSchema] = {}
    _active_symbols: Dict[str, EntityInfo] = {}
    
    @classmethod
    def get_portfolio(cls, name: str = "default") -> Optional[TradingPortfolioSchema]:
        """Get portfolio by name."""
        return cls._portfolios.get(name)
    
    @classmethod
    def set_portfolio(cls, portfolio: TradingPortfolioSchema, name: str = "default"):
        """Store portfolio."""
        cls._portfolios[name] = portfolio
        
    @classmethod
    def add_symbol(cls, symbol: str, entity_info: EntityInfo):
        """Add symbol information."""
        cls._active_symbols[symbol] = entity_info
        
    @classmethod
    def get_symbol(cls, symbol: str) -> Optional[EntityInfo]:
        """Get symbol information."""
        return cls._active_symbols.get(symbol)
        
    @classmethod
    def get_all_symbols(cls) -> Dict[str, EntityInfo]:
        """Get all symbol information."""
        return cls._active_symbols.copy()
        
    @classmethod
    def clear_all(cls):
        """Clear all state - ESSENTIAL for testing."""
        cls._portfolios.clear()
        cls._active_symbols.clear()
        
    @classmethod
    def get_memory_usage(cls) -> Dict[str, Any]:
        """Get current memory usage statistics."""
        return {
            "portfolios_count": len(cls._portfolios),
            "symbols_count": len(cls._active_symbols),
            "total_entities": sum(len(p.entities) for p in cls._portfolios.values())
        }