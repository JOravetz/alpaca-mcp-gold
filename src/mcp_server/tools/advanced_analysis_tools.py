"""
Advanced Portfolio Analysis Tools
Implements sophisticated analysis suggestions and insights following gold standard patterns.
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from ..models.schemas import StateManager, EntityInfo, TradingPortfolioSchema

logger = logging.getLogger(__name__)

async def generate_portfolio_health_assessment() -> Dict[str, Any]:
    """
    Comprehensive portfolio health assessment with scoring and recommendations.
    
    Returns:
        Dict containing portfolio health score, risk analysis, and actionable recommendations
    """
    try:
        # Get current portfolio state
        portfolio = StateManager.get_portfolio()
        symbols = StateManager.get_all_symbols()
        
        if not portfolio:
            return {
                "status": "error",
                "message": "No portfolio data available. Load portfolio data first with get_portfolio_summary()"
            }
        
        # Initialize health assessment
        health_assessment = {
            "overall_score": 0,
            "risk_assessment": {},
            "diversification_analysis": {},
            "performance_analysis": {},
            "recommendations": [],
            "action_items": []
        }
        
        # Calculate diversification score
        diversification_score = _calculate_diversification_score(portfolio, symbols)
        health_assessment["diversification_analysis"] = diversification_score
        
        # Risk concentration analysis
        risk_analysis = _analyze_risk_concentration(portfolio, symbols)
        health_assessment["risk_assessment"] = risk_analysis
        
        # Performance analysis
        performance_analysis = _analyze_portfolio_performance(portfolio, symbols)
        health_assessment["performance_analysis"] = performance_analysis
        
        # Calculate overall score
        overall_score = (
            diversification_score.get("score", 0) * 0.4 +
            risk_analysis.get("score", 0) * 0.3 +
            performance_analysis.get("score", 0) * 0.3
        )
        health_assessment["overall_score"] = round(overall_score, 1)
        
        # Generate recommendations
        recommendations = _generate_health_recommendations(health_assessment)
        health_assessment["recommendations"] = recommendations
        
        # Generate action items
        action_items = _generate_action_items(health_assessment, portfolio)
        health_assessment["action_items"] = action_items
        
        return {
            "status": "success",
            "data": health_assessment,
            "metadata": {
                "operation": "portfolio_health_assessment",
                "assessed_entities": len(symbols),
                "assessment_timestamp": datetime.now().isoformat()
            }
        }
        
    except Exception as e:
        logger.error(f"Error in portfolio health assessment: {e}")
        return {
            "status": "error",
            "message": f"Portfolio health assessment failed: {str(e)}",
            "error_type": type(e).__name__
        }

def _calculate_diversification_score(portfolio: TradingPortfolioSchema, symbols: Dict[str, EntityInfo]) -> Dict[str, Any]:
    """Calculate portfolio diversification score and analysis."""
    
    # Analyze entity roles distribution
    role_distribution: dict[str, int] = {}
    for entity in symbols.values():
        role = entity.suggested_role.value
        role_distribution[role] = role_distribution.get(role, 0) + 1
    
    # Calculate diversification metrics
    total_entities = len(symbols)
    unique_roles = len(role_distribution)
    
    # Diversification score based on role distribution
    if total_entities == 0:
        diversification_score = 0
    elif total_entities == 1:
        diversification_score = 30  # Single holding is risky
    elif unique_roles >= 4:
        diversification_score = 90  # Well diversified
    elif unique_roles >= 3:
        diversification_score = 75  # Good diversification
    elif unique_roles >= 2:
        diversification_score = 55  # Moderate diversification
    else:
        diversification_score = 35  # Poor diversification
    
    # Check for over-concentration
    max_role_count = max(role_distribution.values()) if role_distribution else 0
    concentration_ratio = max_role_count / total_entities if total_entities > 0 else 0
    
    if concentration_ratio > 0.7:
        diversification_score -= 20  # Penalty for over-concentration
    
    return {
        "score": max(0, min(100, diversification_score)),
        "total_entities": total_entities,
        "unique_roles": unique_roles,
        "role_distribution": role_distribution,
        "concentration_ratio": round(concentration_ratio, 2),
        "assessment": _get_diversification_assessment(diversification_score)
    }

def _analyze_risk_concentration(portfolio: TradingPortfolioSchema, symbols: Dict[str, EntityInfo]) -> Dict[str, Any]:
    """Analyze risk concentration in the portfolio."""
    
    # Count volatile assets
    volatile_count = sum(1 for entity in symbols.values() 
                        if entity.suggested_role.value == "volatile_asset")
    
    # Count speculative assets
    speculative_count = sum(1 for entity in symbols.values() 
                           if entity.suggested_role.value == "speculative")
    
    total_entities = len(symbols)
    high_risk_ratio = (volatile_count + speculative_count) / total_entities if total_entities > 0 else 0
    
    # Risk score calculation
    if high_risk_ratio > 0.6:
        risk_score = 30  # Too much risk
    elif high_risk_ratio > 0.4:
        risk_score = 60  # Moderate risk
    elif high_risk_ratio > 0.2:
        risk_score = 85  # Balanced risk
    else:
        risk_score = 75  # Conservative (might be too conservative)
    
    return {
        "score": risk_score,
        "volatile_assets": volatile_count,
        "speculative_assets": speculative_count,
        "high_risk_ratio": round(high_risk_ratio, 2),
        "risk_assessment": _get_risk_assessment(high_risk_ratio),
        "suggestions": _get_risk_suggestions(high_risk_ratio, total_entities)
    }

def _analyze_portfolio_performance(portfolio: TradingPortfolioSchema, symbols: Dict[str, EntityInfo]) -> Dict[str, Any]:
    """Analyze portfolio performance indicators."""
    
    # Analyze entity characteristics for performance indicators
    growth_candidates = sum(1 for entity in symbols.values() 
                           if entity.suggested_role.value == "growth_candidate")
    
    income_generators = sum(1 for entity in symbols.values() 
                           if entity.suggested_role.value == "income_generator")
    
    total_entities = len(symbols)
    
    # Performance balance score
    if total_entities == 0:
        performance_score = 0
    else:
        growth_ratio = growth_candidates / total_entities
        income_ratio = income_generators / total_entities
        
        # Balanced approach gets higher score
        if 0.3 <= growth_ratio <= 0.7 and income_ratio >= 0.1:
            performance_score = 90
        elif growth_ratio >= 0.5:
            performance_score = 75  # Growth-focused
        elif income_ratio >= 0.3:
            performance_score = 70  # Income-focused
        else:
            performance_score = 60  # Unclear strategy
    
    return {
        "score": performance_score,
        "growth_candidates": growth_candidates,
        "income_generators": income_generators,
        "growth_ratio": round(growth_candidates / total_entities, 2) if total_entities > 0 else 0,
        "income_ratio": round(income_generators / total_entities, 2) if total_entities > 0 else 0,
        "strategy_assessment": _get_strategy_assessment(growth_candidates, income_generators, total_entities)
    }

def _generate_health_recommendations(assessment: Dict[str, Any]) -> List[str]:
    """Generate health recommendations based on assessment."""
    recommendations = []
    
    # Diversification recommendations
    diversification = assessment.get("diversification_analysis", {})
    if diversification.get("score", 0) < 60:
        recommendations.append("Consider diversifying across more asset types and sectors")
        if diversification.get("unique_roles", 0) < 3:
            recommendations.append("Add positions in different entity roles (growth, income, hedge instruments)")
    
    # Risk recommendations
    risk_analysis = assessment.get("risk_assessment", {})
    if risk_analysis.get("high_risk_ratio", 0) > 0.5:
        recommendations.append("Reduce exposure to high-risk volatile and speculative assets")
        recommendations.append("Consider adding stable income-generating positions")
    elif risk_analysis.get("high_risk_ratio", 0) < 0.1:
        recommendations.append("Portfolio may be too conservative - consider adding some growth positions")
    
    # Performance recommendations
    performance = assessment.get("performance_analysis", {})
    if performance.get("growth_ratio", 0) < 0.2:
        recommendations.append("Consider adding growth candidates for long-term appreciation")
    if performance.get("income_ratio", 0) < 0.1:
        recommendations.append("Consider adding income-generating assets for cash flow")
    
    # Overall score recommendations
    overall_score = assessment.get("overall_score", 0)
    if overall_score < 50:
        recommendations.append("Portfolio needs significant rebalancing - consider comprehensive review")
    elif overall_score < 70:
        recommendations.append("Portfolio has room for improvement - focus on identified weak areas")
    
    return recommendations

def _generate_action_items(assessment: Dict[str, Any], portfolio: TradingPortfolioSchema) -> List[Dict[str, Any]]:
    """Generate specific action items with tool commands."""
    action_items = []
    
    # Diversification actions
    diversification = assessment.get("diversification_analysis", {})
    if diversification.get("unique_roles", 0) < 3:
        action_items.append({
            "priority": "high",
            "action": "Research and add positions in underrepresented asset types",
            "tools": ["get_stock_snapshot('SYMBOL')", "place_limit_order()"],
            "category": "diversification"
        })
    
    # Risk management actions
    risk_analysis = assessment.get("risk_assessment", {})
    if risk_analysis.get("high_risk_ratio", 0) > 0.5:
        action_items.append({
            "priority": "high", 
            "action": "Set stop losses on volatile positions",
            "tools": ["place_stop_loss_order()", "get_positions()"],
            "category": "risk_management"
        })
    
    # Performance actions
    performance = assessment.get("performance_analysis", {})
    if performance.get("score", 0) < 70:
        action_items.append({
            "priority": "medium",
            "action": "Review and rebalance portfolio strategy",
            "tools": ["get_portfolio_summary()", "trading_strategy_workshop()"],
            "category": "performance"
        })
    
    # Monitoring actions (always include)
    action_items.append({
        "priority": "low",
        "action": "Schedule regular portfolio health assessments",
        "tools": ["generate_portfolio_health_assessment()"],
        "category": "monitoring"
    })
    
    return action_items

def _get_diversification_assessment(score: float) -> str:
    """Get diversification assessment text."""
    if score >= 80:
        return "Excellent diversification across multiple asset types"
    elif score >= 60:
        return "Good diversification with room for improvement"
    elif score >= 40:
        return "Moderate diversification - consider adding variety"
    else:
        return "Poor diversification - concentrated in few asset types"

def _get_risk_assessment(risk_ratio: float) -> str:
    """Get risk assessment text."""
    if risk_ratio > 0.6:
        return "High risk concentration - consider reducing volatile positions"
    elif risk_ratio > 0.4:
        return "Moderate risk level - well balanced for growth-oriented investors"
    elif risk_ratio > 0.2:
        return "Conservative risk level - appropriate for stable returns"
    else:
        return "Very conservative - may limit growth potential"

def _get_risk_suggestions(risk_ratio: float, total_entities: int) -> List[str]:
    """Get risk management suggestions."""
    suggestions = []
    
    if risk_ratio > 0.5:
        suggestions.append("Reduce volatile asset allocation")
        suggestions.append("Add stable income-generating positions")
        suggestions.append("Implement stop-loss orders on high-risk positions")
    elif risk_ratio < 0.1 and total_entities > 3:
        suggestions.append("Consider adding moderate growth positions")
        suggestions.append("Evaluate risk tolerance and investment timeline")
    
    return suggestions

def _get_strategy_assessment(growth_count: int, income_count: int, total: int) -> str:
    """Get portfolio strategy assessment."""
    if total == 0:
        return "No clear strategy - portfolio is empty"
    
    growth_ratio = growth_count / total
    income_ratio = income_count / total
    
    if growth_ratio > 0.6:
        return "Growth-focused strategy - emphasizes capital appreciation"
    elif income_ratio > 0.4:
        return "Income-focused strategy - emphasizes cash flow generation"
    elif growth_ratio >= 0.3 and income_ratio >= 0.2:
        return "Balanced strategy - combines growth and income objectives"
    else:
        return "Unclear strategy - consider defining investment objectives"

async def generate_advanced_market_correlation_analysis(symbols: Optional[str] = None) -> Dict[str, Any]:
    """
    Advanced market correlation analysis with sector and benchmark comparisons.
    
    Args:
        symbols: Optional comma-separated symbols to analyze (uses tracked symbols if not provided)
    
    Returns:
        Dict containing correlation analysis, sector exposure, and benchmark comparisons
    """
    try:
        # Determine symbols to analyze
        if symbols:
            symbol_list = [s.strip().upper() for s in symbols.split(',') if s.strip()]
        else:
            tracked_symbols = StateManager.get_all_symbols()
            symbol_list = list(tracked_symbols.keys())
        
        if len(symbol_list) < 2:
            return {
                "status": "error",
                "message": "Need at least 2 symbols for correlation analysis"
            }
        
        # Get market data for symbols
        from .market_data_tools import get_historical_bars
        
        correlation_data = {}
        for symbol in symbol_list:
            try:
                # Get recent price data
                hist_result = await get_historical_bars(symbol, "1Day", limit=30)
                if hist_result["status"] == "success":
                    bars = hist_result["data"]["bars"]
                    prices = [bar["close"] for bar in bars]
                    correlation_data[symbol] = {
                        "prices": prices,
                        "returns": _calculate_returns(prices)
                    }
            except Exception as e:
                logger.warning(f"Could not get data for {symbol}: {e}")
        
        if len(correlation_data) < 2:
            return {
                "status": "error",
                "message": "Insufficient price data for correlation analysis"
            }
        
        # Calculate correlations
        correlations = _calculate_correlations(correlation_data)
        
        # Analyze results
        analysis = {
            "correlation_matrix": correlations,
            "high_correlations": _find_high_correlations(correlations),
            "diversification_score": _calculate_correlation_diversification_score(correlations),
            "risk_insights": _generate_correlation_risk_insights(correlations),
            "recommendations": _generate_correlation_recommendations(correlations)
        }
        
        return {
            "status": "success",
            "data": analysis,
            "metadata": {
                "operation": "market_correlation_analysis",
                "symbols_analyzed": list(correlation_data.keys()),
                "analysis_period": "30 days",
                "timestamp": datetime.now().isoformat()
            }
        }
        
    except Exception as e:
        logger.error(f"Error in correlation analysis: {e}")
        return {
            "status": "error",
            "message": f"Correlation analysis failed: {str(e)}",
            "error_type": type(e).__name__
        }

def _calculate_returns(prices: List[float]) -> List[float]:
    """Calculate daily returns from price series."""
    if len(prices) < 2:
        return []
    
    returns = []
    for i in range(1, len(prices)):
        if prices[i-1] != 0:
            ret = (prices[i] - prices[i-1]) / prices[i-1]
            returns.append(ret)
    
    return returns

def _calculate_correlations(correlation_data: Dict[str, Dict[str, Any]]) -> Dict[str, Dict[str, float]]:
    """Calculate correlation matrix between symbols."""
    symbols = list(correlation_data.keys())
    correlations: dict[str, dict[str, float]] = {}
    
    for i, symbol1 in enumerate(symbols):
        correlations[symbol1] = {}
        returns1 = correlation_data[symbol1]["returns"]
        
        for j, symbol2 in enumerate(symbols):
            returns2 = correlation_data[symbol2]["returns"]
            
            if symbol1 == symbol2:
                correlations[symbol1][symbol2] = 1.0
            else:
                # Calculate Pearson correlation
                correlation = _pearson_correlation(returns1, returns2)
                correlations[symbol1][symbol2] = round(correlation, 3)
    
    return correlations

def _pearson_correlation(x: List[float], y: List[float]) -> float:
    """Calculate Pearson correlation coefficient."""
    if len(x) != len(y) or len(x) < 2:
        return 0.0
    
    n = len(x)
    mean_x = sum(x) / n
    mean_y = sum(y) / n
    
    numerator = sum((x[i] - mean_x) * (y[i] - mean_y) for i in range(n))
    
    sum_sq_x = sum((x[i] - mean_x) ** 2 for i in range(n))
    sum_sq_y = sum((y[i] - mean_y) ** 2 for i in range(n))
    
    denominator = (sum_sq_x * sum_sq_y) ** 0.5
    
    if denominator == 0:
        return 0.0
    
    return float(numerator / denominator)

def _find_high_correlations(correlations: Dict[str, Dict[str, float]]) -> List[Dict[str, Any]]:
    """Find pairs with high correlation."""
    high_correlations = []
    
    symbols = list(correlations.keys())
    for i, symbol1 in enumerate(symbols):
        for j, symbol2 in enumerate(symbols[i+1:], i+1):
            corr = correlations[symbol1][symbol2]
            if abs(corr) > 0.6:  # High correlation threshold
                high_correlations.append({
                    "symbol1": symbol1,
                    "symbol2": symbol2,
                    "correlation": corr,
                    "strength": "strong" if abs(corr) > 0.8 else "moderate"
                })
    
    return sorted(high_correlations, key=lambda x: abs(x["correlation"]), reverse=True)

def _calculate_correlation_diversification_score(correlations: Dict[str, Dict[str, float]]) -> Dict[str, Any]:
    """Calculate diversification score based on correlations."""
    symbols = list(correlations.keys())
    total_pairs = 0
    high_corr_pairs = 0
    
    for i, symbol1 in enumerate(symbols):
        for j, symbol2 in enumerate(symbols[i+1:], i+1):
            total_pairs += 1
            if abs(correlations[symbol1][symbol2]) > 0.7:
                high_corr_pairs += 1
    
    if total_pairs == 0:
        diversification_score = 100
    else:
        # Lower score for more highly correlated pairs
        correlation_ratio = float(high_corr_pairs) / float(total_pairs)
        diversification_score = max(0.0, 100.0 - (correlation_ratio * 60.0))
    
    return {
        "score": round(diversification_score, 1),
        "high_correlation_pairs": high_corr_pairs,
        "total_pairs": total_pairs,
        "assessment": _get_correlation_diversification_assessment(diversification_score)
    }

def _get_correlation_diversification_assessment(score: float) -> str:
    """Get correlation-based diversification assessment."""
    if score >= 80:
        return "Excellent diversification - low correlation between holdings"
    elif score >= 60:
        return "Good diversification - moderate correlation levels"
    elif score >= 40:
        return "Fair diversification - some highly correlated positions"
    else:
        return "Poor diversification - many highly correlated positions"

def _generate_correlation_risk_insights(correlations: Dict[str, Dict[str, float]]) -> List[str]:
    """Generate risk insights from correlation analysis."""
    insights = []
    
    high_corrs = _find_high_correlations(correlations)
    
    if len(high_corrs) > 3:
        insights.append("Portfolio has multiple highly correlated positions, increasing concentration risk")
    elif len(high_corrs) > 1:
        insights.append("Some positions are highly correlated, reducing diversification benefits")
    else:
        insights.append("Portfolio shows good diversification with low correlations")
    
    # Check for very high correlations
    very_high = [hc for hc in high_corrs if abs(hc["correlation"]) > 0.9]
    if very_high:
        insights.append("Extremely high correlation detected between some positions (>0.9)")
    
    return insights

def _generate_correlation_recommendations(correlations: Dict[str, Dict[str, float]]) -> List[str]:
    """Generate recommendations based on correlation analysis."""
    recommendations = []
    
    high_corrs = _find_high_correlations(correlations)
    
    if len(high_corrs) > 2:
        recommendations.append("Consider reducing positions in highly correlated assets")
        recommendations.append("Look for assets in different sectors or with different characteristics")
    
    if len(correlations) < 5:
        recommendations.append("Consider adding more positions to improve diversification")
    
    # Find negatively correlated pairs (good for hedging)
    negative_corrs = [hc for hc in high_corrs if hc["correlation"] < -0.5]
    if negative_corrs:
        recommendations.append("Some positions provide good hedging benefits with negative correlations")
    else:
        recommendations.append("Consider adding hedge instruments or defensive positions")
    
    return recommendations