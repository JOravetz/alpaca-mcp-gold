"""
Trading prompts following gold standard patterns.
Context-aware conversation starters that adapt to portfolio state.
"""

import logging
from typing import Dict, Any, Optional
from ..models.schemas import StateManager, TradingEntityType, EntityRole

logger = logging.getLogger(__name__)

async def portfolio_first_look() -> Dict[str, Any]:
    """
    Adaptive prompt that provides initial portfolio exploration guidance.
    References actual portfolio data when available.
    
    Returns:
        Prompt dict with context-aware content
    """
    try:
        # Get current portfolio state
        portfolio = StateManager.get_portfolio()
        symbols = StateManager.get_all_symbols()
        
        if portfolio and len(portfolio.entities) > 0:
            # Portfolio exists - provide specific guidance
            entity_count = len(portfolio.entities)
            portfolio_value = portfolio.portfolio_metrics.get('portfolio_value', 0)
            
            # Analyze portfolio composition
            positions = [e for e in portfolio.entities.values() if e.entity_type == TradingEntityType.POSITION]
            volatile_assets = [e for e in portfolio.entities.values() if e.suggested_role == EntityRole.VOLATILE_ASSET]
            growth_candidates = [e for e in portfolio.entities.values() if e.suggested_role == EntityRole.GROWTH_CANDIDATE]
            
            prompt_text = f"""I can see you have an active portfolio worth ${portfolio_value:,.2f} with **{entity_count} tracked entities**!

Let me help you analyze your current holdings and explore opportunities:

📊 **Your Portfolio at a Glance:**
• **{len(positions)} active positions** being tracked
• **Portfolio Value:** ${portfolio_value:,.2f}
• **Cash Allocation:** {portfolio.portfolio_metrics.get('cash_allocation', 0)*100:.1f}%

"""
            
            if volatile_assets:
                symbols_list = [e.name for e in volatile_assets[:3]]
                prompt_text += f"⚡ **High Volatility Assets:** {', '.join(symbols_list)}\n"
                prompt_text += "→ These positions may need closer monitoring\n\n"
            
            if growth_candidates:
                symbols_list = [e.name for e in growth_candidates[:3]]
                prompt_text += f"🚀 **Growth Candidates:** {', '.join(symbols_list)}\n"
                prompt_text += "→ These positions show positive momentum\n\n"
            
            # Add actionable suggestions
            prompt_text += "**🎯 What would you like to explore?**\n"
            if len(positions) > 0:
                prompt_text += f"• **Position Analysis**: `get_positions()` - Review your {len(positions)} holdings\n"
            if portfolio_value > 0:
                prompt_text += "• **Portfolio Summary**: `get_portfolio_summary()` - Complete portfolio insights\n"
            prompt_text += "• **Market Research**: `get_stock_quote('SYMBOL')` - Research new opportunities\n"
            prompt_text += "• **Risk Management**: Set stop losses or take profits on existing positions\n"
            
            if portfolio.suggested_operations:
                prompt_text += f"\n**💡 Recommendations:**\n"
                for suggestion in portfolio.suggested_operations[:3]:
                    prompt_text += f"• {suggestion}\n"
        
        elif symbols and len(symbols) > 0:
            # Some symbols tracked but no full portfolio
            symbol_names = list(symbols.keys())[:5]
            
            prompt_text = f"""I can see you've been researching **{len(symbols)} symbols**: {', '.join(symbol_names)}

Let's turn this research into actionable portfolio management:

📈 **Recently Analyzed:**
"""
            for symbol, entity in list(symbols.items())[:3]:
                prompt_text += f"• **{symbol}**: {entity.suggested_role.value.replace('_', ' ').title()}\n"
            
            prompt_text += f"""
**🎯 Next Steps:**
• **Account Overview**: `get_account_info()` - Check your buying power
• **Market Data**: `get_stock_snapshot('SYMBOL')` - Get comprehensive data
• **Position Entry**: `place_limit_order()` - Execute trades on researched symbols
• **Portfolio Building**: Start building positions in your analyzed symbols
"""
        
        else:
            # No portfolio data - general guidance
            prompt_text = """Welcome to your Alpaca trading assistant! I'm here to help you manage your portfolio and execute trades.

**🚀 Let's get started:**

**📊 Account & Portfolio:**
• `get_account_info()` - Check your account status and buying power
• `get_positions()` - Review your current holdings
• `get_portfolio_summary()` - Comprehensive portfolio analysis

**📈 Market Research:**
• `get_stock_quote('AAPL')` - Get real-time quotes
• `get_stock_snapshot('TSLA')` - Comprehensive market data
• `get_historical_bars('MSFT')` - Analyze price trends

**⚡ Trading Operations:**
• `place_market_order('SYMBOL', 'buy', 10)` - Execute immediate trades
• `place_limit_order('SYMBOL', 'buy', 10, 150.00)` - Set price targets
• `place_stop_loss_order('SYMBOL', 'sell', 10, 140.00)` - Risk management

**🔍 What type of trading strategy interests you?**
• Day trading with quick entries/exits
• Long-term investing with fundamental analysis
• Options strategies for income generation
• Portfolio diversification and risk management
"""
        
        return {
            "name": "portfolio_first_look",
            "description": "Get started with portfolio analysis and trading guidance",
            "messages": [
                {
                    "role": "user",
                    "content": {
                        "type": "text",
                        "text": prompt_text
                    }
                }
            ]
        }
        
    except Exception as e:
        logger.error(f"Error generating portfolio first look prompt: {e}")
        # Fallback to basic prompt
        return {
            "name": "portfolio_first_look",
            "description": "Get started with portfolio analysis and trading guidance",
            "messages": [
                {
                    "role": "user",
                    "content": {
                        "type": "text",
                        "text": "Let's start exploring your trading portfolio and market opportunities!"
                    }
                }
            ]
        }

async def trading_strategy_workshop(strategy_focus: str = "general") -> Dict[str, Any]:
    """
    Adaptive prompt for trading strategy guidance based on portfolio context.
    
    Args:
        strategy_focus: Type of strategy to focus on ('growth', 'income', 'risk_management', 'general')
    
    Returns:
        Prompt dict with strategy-specific guidance
    """
    try:
        portfolio = StateManager.get_portfolio()
        
        # Base strategy guidance
        strategy_prompts = {
            "growth": {
                "title": "Growth Trading Strategy Workshop",
                "focus": "building positions in growth candidates and momentum stocks"
            },
            "income": {
                "title": "Income Generation Strategy Workshop", 
                "focus": "generating consistent income through dividends and covered calls"
            },
            "risk_management": {
                "title": "Risk Management Strategy Workshop",
                "focus": "protecting capital and managing downside risk"
            },
            "general": {
                "title": "Trading Strategy Workshop",
                "focus": "developing a comprehensive trading approach"
            }
        }
        
        strategy_info = strategy_prompts.get(strategy_focus, strategy_prompts["general"])
        
        prompt_text = f"""# {strategy_info['title']}

Let's develop a strategic approach for {strategy_info['focus']}.

"""
        
        # Add portfolio-specific context
        if portfolio and len(portfolio.entities) > 0:
            positions = [e for e in portfolio.entities.values() if e.entity_type == TradingEntityType.POSITION]
            portfolio_value = portfolio.portfolio_metrics.get('portfolio_value', 0)
            
            prompt_text += f"**Your Current Portfolio Context:**\n"
            prompt_text += f"• Portfolio Value: ${portfolio_value:,.2f}\n"
            prompt_text += f"• Active Positions: {len(positions)}\n"
            
            if strategy_focus == "growth":
                growth_positions = [e for e in portfolio.entities.values() 
                                 if e.suggested_role == EntityRole.GROWTH_CANDIDATE]
                if growth_positions:
                    symbols = [e.name for e in growth_positions[:3]]
                    prompt_text += f"• Current Growth Positions: {', '.join(symbols)}\n"
                    prompt_text += "→ We can build on these existing momentum plays\n\n"
                
            elif strategy_focus == "risk_management":
                volatile_positions = [e for e in portfolio.entities.values() 
                                    if e.suggested_role == EntityRole.VOLATILE_ASSET]
                if volatile_positions:
                    symbols = [e.name for e in volatile_positions[:3]]
                    prompt_text += f"• High-Risk Positions: {', '.join(symbols)}\n"
                    prompt_text += "→ These positions may need protective stops\n\n"
        
        # Strategy-specific guidance
        if strategy_focus == "growth":
            prompt_text += """**🚀 Growth Strategy Framework:**

**1. Stock Selection Criteria:**
• Revenue growth > 20% year-over-year
• Strong technical momentum (price above moving averages)
• Market leadership in growing sectors (tech, clean energy, biotech)

**2. Entry Strategies:**
• `get_stock_snapshot('SYMBOL')` - Analyze momentum indicators
• `place_limit_order()` - Enter on pullbacks to support levels
• Scale into positions over time to reduce timing risk

**3. Position Management:**
• Set initial stop loss at 8-10% below entry
• Take partial profits at 20-25% gains
• Let winners run with trailing stops

**🎯 Action Items:**
• Screen for stocks with strong earnings growth
• Identify breakout candidates above resistance
• Build watchlist of sector leaders"""

        elif strategy_focus == "income":
            prompt_text += """**💰 Income Generation Framework:**

**1. Dividend Stock Selection:**
• Dividend yield 3-6% with consistent payment history
• Payout ratio < 60% for sustainability
• Defensive sectors (utilities, REITs, consumer staples)

**2. Covered Call Strategy:**
• Own 100+ shares of stable stocks
• Sell out-of-the-money calls for monthly income
• Target 1-2% monthly premium collection

**3. Cash Management:**
• Maintain 10-20% cash for opportunities
• Reinvest dividends for compound growth
• Use limit orders to accumulate quality names

**🎯 Action Items:**
• Build positions in dividend aristocrats
• Implement covered call writing program
• Create income tracking spreadsheet"""

        elif strategy_focus == "risk_management":
            prompt_text += """**🛡️ Risk Management Framework:**

**1. Position Sizing:**
• Risk no more than 1-2% of portfolio per trade
• Maximum 5% allocation to any single position
• Diversify across sectors and asset classes

**2. Stop Loss Strategy:**
• `place_stop_loss_order()` - Protect against major losses
• Use technical levels (support/resistance) for stops
• Adjust stops higher as positions move in your favor

**3. Portfolio Protection:**
• Hedge with put options during market uncertainty
• Maintain 20-30% cash during volatile periods
• Rebalance quarterly to maintain target allocations

**🎯 Action Items:**
• Set stop losses on all current positions
• Calculate proper position sizes for new trades
• Review portfolio correlation risk"""

        else:  # general
            prompt_text += """**📈 Comprehensive Trading Framework:**

**1. Market Analysis:**
• `get_historical_bars()` - Study price trends and patterns
• Monitor economic indicators and earnings reports
• Track sector rotation and market sentiment

**2. Trade Execution:**
• Use limit orders for better entry/exit prices
• Scale into positions gradually
• Maintain detailed trading journal

**3. Portfolio Balance:**
• Combine growth and income positions
• Manage risk through diversification
• Regular performance review and adjustment

**🎯 Action Items:**
• Define your risk tolerance and time horizon
• Create a balanced portfolio allocation
• Establish systematic trading rules"""

        prompt_text += f"""

**🔧 Available Tools for This Strategy:**
• Market Research: `get_stock_quote()`, `get_stock_snapshot()`
• Position Analysis: `get_positions()`, `get_portfolio_summary()`
• Trade Execution: `place_limit_order()`, `place_stop_loss_order()`
• Risk Management: `get_open_position()`, `cancel_order()`

What aspect of this {strategy_focus} strategy would you like to explore first?"""

        return {
            "name": f"trading_strategy_{strategy_focus}",
            "description": f"Strategic guidance for {strategy_focus} trading approach",
            "messages": [
                {
                    "role": "user",
                    "content": {
                        "type": "text",
                        "text": prompt_text
                    }
                }
            ]
        }
        
    except Exception as e:
        logger.error(f"Error generating strategy workshop prompt: {e}")
        return {
            "name": "trading_strategy_workshop",
            "description": "Trading strategy guidance and planning",
            "messages": [
                {
                    "role": "user",
                    "content": {
                        "type": "text",
                        "text": "Let's develop a strategic approach to your trading and portfolio management!"
                    }
                }
            ]
        }

async def market_analysis_session() -> Dict[str, Any]:
    """
    Adaptive prompt for market analysis based on currently tracked symbols.
    
    Returns:
        Prompt dict with market analysis guidance
    """
    try:
        symbols = StateManager.get_all_symbols()
        portfolio = StateManager.get_portfolio()
        
        if symbols and len(symbols) > 0:
            # Provide analysis on tracked symbols
            symbol_names = list(symbols.keys())[:5]
            
            prompt_text = f"""# Market Analysis Session

Let's dive deep into the market data for your tracked symbols and discover new opportunities.

**📊 Currently Tracking {len(symbols)} Symbols:**
"""
            
            # Analyze each tracked symbol
            for symbol, entity in list(symbols.items())[:5]:
                characteristics = entity.characteristics
                role = entity.suggested_role.value.replace('_', ' ').title()
                
                prompt_text += f"""
**{symbol}** - {role}
"""
                if 'latest_price' in characteristics:
                    prompt_text += f"• Current Price: ${characteristics['latest_price']:.2f}\n"
                if 'price_change_percent' in characteristics:
                    change = characteristics['price_change_percent']
                    direction = "📈" if change > 0 else "📉"
                    prompt_text += f"• Daily Change: {direction} {change:.2f}%\n"
                if 'volatility' in characteristics:
                    prompt_text += f"• Volatility: {characteristics['volatility']:.1f}%\n"
            
            prompt_text += f"""

**🔍 Recommended Analysis:**
• `get_stock_snapshot('{symbol_names[0]}')` - Complete market data for top symbol
• `get_historical_bars('{symbol_names[0]}', '1Day', limit=30)` - 30-day price trend
• Compare performance across your watchlist symbols
• Identify correlation patterns between holdings
"""
            
        else:
            # General market analysis guidance
            prompt_text = """# Market Analysis Session

Let's explore the markets and identify trading opportunities using comprehensive data analysis.

**📈 Market Research Tools:**

**Real-Time Data:**
• `get_stock_quote('AAPL')` - Current bid/ask and spreads
• `get_stock_snapshot('TSLA')` - Complete market picture with volume
• `get_stock_trade('MSFT')` - Latest trade execution data

**Historical Analysis:**
• `get_historical_bars('SPY', '1Day', limit=50)` - Market trend analysis
• `get_historical_bars('QQQ', '1Hour', limit=100)` - Intraday patterns
• Compare multiple timeframes for complete picture

**🎯 Analysis Strategies:**
"""
        
        prompt_text += """
**Technical Analysis Framework:**
• **Trend Identification**: Use 20/50/200 moving averages
• **Support/Resistance**: Identify key price levels
• **Volume Analysis**: Confirm price moves with volume
• **Momentum Indicators**: Look for oversold/overbought conditions

**Fundamental Screening:**
• **Earnings Growth**: Research upcoming earnings reports
• **Sector Rotation**: Identify leading/lagging sectors
• **Economic Indicators**: Monitor Fed policy and economic data
• **News Catalyst**: Track company-specific developments

**Risk Assessment:**
• **Volatility Analysis**: Measure historical price swings
• **Correlation Study**: Understand portfolio diversification
• **Sector Exposure**: Avoid overconcentration risk
• **Market Sentiment**: Gauge fear/greed levels

**🚀 Popular Symbols to Analyze:**
• **Large Cap Tech**: AAPL, MSFT, GOOGL, AMZN
• **Market ETFs**: SPY, QQQ, IWM, VTI
• **Sector Leaders**: XLF (Financials), XLE (Energy), XLK (Tech)
• **Growth Stocks**: NVDA, TSLA, AMD, CRM

**What type of market analysis would you like to start with?**
• Sector rotation analysis
• Individual stock deep dive
• Market trend identification
• Volatility and risk assessment
"""

        return {
            "name": "market_analysis_session",
            "description": "Comprehensive market analysis and research guidance",
            "messages": [
                {
                    "role": "user",
                    "content": {
                        "type": "text",
                        "text": prompt_text
                    }
                }
            ]
        }
        
    except Exception as e:
        logger.error(f"Error generating market analysis prompt: {e}")
        return {
            "name": "market_analysis_session", 
            "description": "Market analysis and research guidance",
            "messages": [
                {
                    "role": "user",
                    "content": {
                        "type": "text",
                        "text": "Let's analyze market data and identify trading opportunities!"
                    }
                }
            ]
        }

async def list_mcp_capabilities() -> Dict[str, Any]:
    """
    Prompt that explains all available MCP tools and resources.
    
    Returns:
        Prompt dict with comprehensive capability overview
    """
    prompt_text = """# Alpaca Trading MCP Server - Complete Capabilities

Welcome to your comprehensive trading assistant! Here's everything I can help you with:

## 📊 Account & Portfolio Management

**Account Information:**
• `get_account_info()` - Account status, buying power, cash, portfolio value
• `get_portfolio_summary()` - Adaptive portfolio analysis with insights
• `resource_account_info()` - Tool mirror for account data access

**Position Management:**
• `get_positions()` - All current holdings with P&L analysis
• `get_open_position('AAPL')` - Specific position details
• `resource_account_positions()` - Tool mirror for positions access

## 📈 Market Data & Research

**Real-Time Quotes:**
• `get_stock_quote('SYMBOL')` - Latest bid/ask with spreads
• `get_stock_trade('SYMBOL')` - Most recent trade execution
• `get_stock_snapshot('SYMBOL')` - Comprehensive market data

**Historical Analysis:**
• `get_historical_bars('SYMBOL', '1Day', limit=30)` - Price history
• Supported timeframes: 1Min, 5Min, 15Min, 1Hour, 1Day
• Automatic volatility and trend analysis

## ⚡ Order Management

**Order Placement:**
• `place_market_order('SYMBOL', 'buy', quantity)` - Immediate execution
• `place_limit_order('SYMBOL', 'buy', quantity, price)` - Price targeting
• `place_stop_loss_order('SYMBOL', 'sell', quantity, stop_price)` - Risk management

**Order Tracking:**
• `get_orders(status='open')` - Filter by status (open/closed/all)
• `cancel_order('order_id')` - Cancel pending orders
• `resource_account_orders()` - Tool mirror for orders access

## 🔧 System Resources (Universal Compatibility)

**Resource Access (URI-based):**
• `trading://account/info` - Account information
• `trading://account/positions` - All positions
• `trading://portfolio/summary` - Portfolio analysis
• `trading://symbols/active` - Tracked symbols
• `trading://system/health` - System status

**Resource Mirrors (Tool-based):**
• All resources have corresponding `resource_*` tools for tool-only clients
• Identical functionality with consistent error handling
• Future-proof compatibility across MCP clients

## 🎯 Adaptive Intelligence Features

**Smart Entity Recognition:**
• Automatic classification of stocks, positions, and orders
• Suggested roles: Growth Candidate, Income Generator, Hedge Instrument
• Volatility and risk assessment for all holdings

**Context-Aware Prompts:**
• Portfolio-specific guidance based on your actual holdings
• Strategy recommendations adapted to your position sizes
• Dynamic suggestions based on market conditions

**Memory Management:**
• Tracks all analyzed symbols and positions
• Maintains portfolio state across sessions
• Memory usage monitoring and cleanup

## 💡 Conversation Starters

• `portfolio_first_look()` - Adaptive portfolio exploration
• `trading_strategy_workshop('growth')` - Strategy-specific guidance
• `market_analysis_session()` - Research and analysis framework

## 🛡️ Safety Features

• Input validation for all parameters
• Comprehensive error handling with helpful messages
• Paper trading mode support
• Risk management order types

## 🚀 Getting Started

**New to the platform?**
1. `get_account_info()` - Check your account status
2. `portfolio_first_look()` - Get personalized guidance
3. `get_stock_quote('AAPL')` - Try market data retrieval

**Ready to trade?**
1. `get_stock_snapshot('SYMBOL')` - Research your target
2. `place_limit_order('SYMBOL', 'buy', qty, price)` - Execute trades
3. `get_positions()` - Monitor your holdings

**Advanced features?**
1. `resource_portfolio_summary()` - Access via resource URI
2. `trading_strategy_workshop('risk_management')` - Advanced strategies
3. `get_historical_bars()` - Technical analysis

What would you like to explore first?"""

    return {
        "name": "list_mcp_capabilities",
        "description": "Complete overview of all MCP server capabilities and tools",
        "messages": [
            {
                "role": "user",
                "content": {
                    "type": "text",
                    "text": prompt_text
                }
            }
        ]
    }