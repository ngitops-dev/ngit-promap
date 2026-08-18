import pandas as pd


def format_currency(amount, currency="NGN"):
    symbols = {"NGN": "\u20a6", "USD": "$", "GBP": "\u00a3", "EUR": "\u20ac"}
    symbol = symbols.get(currency, currency + " ")
    try:
        val = float(amount)
        if val >= 1_000_000:
            return f"{symbol}{val/1_000_000:,.1f}M"
        elif val >= 1_000:
            return f"{symbol}{val/1_000:,.1f}K"
        return f"{symbol}{val:,.2f}"
    except (ValueError, TypeError):
        return f"{symbol}0"


def format_number(n):
    try:
        return f"{int(n):,}"
    except (ValueError, TypeError):
        return "0"


def format_date(date_str):
    if not date_str:
        return "-"
    try:
        from datetime import datetime
        for fmt in ["%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d"]:
            try:
                return datetime.strptime(str(date_str), fmt).strftime("%d %b %Y %H:%M")
            except ValueError:
                continue
        return str(date_str)
    except Exception:
        return str(date_str)


def time_ago(date_str):
    if not date_str:
        return "-"
    try:
        from datetime import datetime, timezone
        for fmt in ["%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d"]:
            try:
                dt = datetime.strptime(str(date_str), fmt)
                break
            except ValueError:
                continue
        else:
            return str(date_str)
        now = datetime.now()
        diff = now - dt
        if diff.days > 0:
            return f"{diff.days} day{'s' if diff.days > 1 else ''} ago"
        hours = diff.seconds // 3600
        if hours > 0:
            return f"{hours} hour{'s' if hours > 1 else ''} ago"
        minutes = diff.seconds // 60
        return f"{minutes} min{'s' if minutes > 1 else ''} ago"
    except Exception:
        return str(date_str)


def status_color(status: str) -> str:
    colors = {
        "PAID": "green",
        "COMPLETED": "green",
        "SENT": "green",
        "ACTIVE": "green",
        "PENDING": "orange",
        "PROCESSING": "orange",
        "UPCOMING": "blue",
        "FAILED": "red",
        "CANCELLED": "red",
        "INACTIVE": "gray",
        "MANUAL_REVIEW": "orange",
        "REFUNDED": "gray",
        "UNPAID": "red",
        "REGISTERED": "blue",
    }
    return colors.get(status.upper(), "gray")


def status_badge(status: str) -> str:
    color = status_color(status)
    icons = {
        "green": "\U0001f7e2",
        "orange": "\U0001f7e0",
        "red": "\U0001f534",
        "blue": "\U0001f535",
        "gray": "\u26aa",
    }
    icon = icons.get(color, "\u26aa")
    return f"{icon} {status.upper()}"
