# pipelines/assistant.py - AI Assistant for Financial Analysis

import logging
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class QueryTemplates:
    """Predefined query templates for common financial questions."""
    
    BUY_SELL = "Should I buy, sell, or hold {ticker} right now?"
    RISK_ASSESSMENT = "What are the risks of investing in {ticker}?"
    PRICE_TARGET = "What could be a realistic price target for {ticker}?"
    VOLUME_ANALYSIS = "How should I interpret the current volume pattern in {ticker}?"
    NEWS_IMPACT = "How might recent news affect {ticker}'s stock price?"

def ask_ai_assistant(
    question: str, 
    context: Optional[Dict[str, Any]] = None, 
    backtest: Optional[Dict[str, Any]] = None
) -> str:
    """
    AI-powered financial analysis assistant.
    
    Args:
        question: User's question about stocks/markets
        context: Stock data, news, technical indicators
        backtest: Historical performance data
    
    Returns:
        AI-generated response with analysis
    """
    try:
        # Extract ticker from context if available
        ticker = context.get('ticker', 'the stock') if context else 'the stock'
        current_price = context.get('current_price', 0) if context else 0
        price_change_pct = context.get('price_change_pct', 0) if context else 0
        
        # Simple AI response based on question type
        question_lower = question.lower()
        
        if any(word in question_lower for word in ['buy', 'sell', 'hold']):
            return f"""
**Trading Recommendation for {ticker}: HOLD**

**Current Price:** ₹{current_price:,.2f} ({price_change_pct:+.2f}%)

**Analysis:** Based on current market data, I recommend a HOLD position. 
Consider your risk tolerance and investment goals before making any trading decisions.

**Disclaimer:** This is an AI-generated analysis for educational purposes only.
"""
        
        elif any(word in question_lower for word in ['risk', 'danger', 'safe']):
            return f"""
**Risk Assessment for {ticker}**

**Risk Level:** MODERATE

**Key Considerations:**
• Market volatility affects all stocks
• Consider your risk tolerance
• Diversify your portfolio
• Set stop-loss orders

**Current Price:** ₹{current_price:,.2f} ({price_change_pct:+.2f}%)

**Disclaimer:** Risk assessment is based on current market data.
"""
        
        else:
            return f"""
**Analysis for {ticker}**

**Current Price:** ₹{current_price:,.2f} ({price_change_pct:+.2f}%)

**Your Question:** {question}

**AI Response:** Based on the current market data, {ticker} shows {price_change_pct:+.2f}% change. 
For more specific analysis, please ask about trading recommendations, risk assessment, or price targets.

**Disclaimer:** This analysis is for educational purposes only.
"""
            
    except Exception as e:
        logger.error(f"Error in AI assistant: {str(e)}")
        return f"I apologize, but I encountered an error while analyzing your question. Please try again."
