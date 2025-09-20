from datetime import datetime

def format_date(date_string: str) -> str:
    """Format date string for display"""
    try:
        date = datetime.fromisoformat(date_string.replace('Z', '+00:00'))
        return date.strftime("%b %d, %Y %H:%M")
    except:
        return date_string

def format_price(price: float) -> str:
    """Format price with appropriate decimal places in INR"""
    from services.currency_service import currency_service
    return currency_service.format_inr(price)

def format_percentage(change: float) -> str:
    """Format percentage change"""
    sign = "+" if change > 0 else ""
    return f"{sign}{change:.2f}%"