import streamlit as st


def render_status_badge(status: str) -> str:
    colors = {
        "PAID": ("green", "\u2705"),
        "COMPLETED": ("green", "\u2705"),
        "SENT": ("green", "\u2705"),
        "ACTIVE": ("green", "\u2705"),
        "PENDING": ("orange", "\u23f3"),
        "PROCESSING": ("orange", "\u23f3"),
        "UPCOMING": ("blue", "\U0001f535"),
        "FAILED": ("red", "\u274c"),
        "CANCELLED": ("red", "\u274c"),
        "INACTIVE": ("gray", "\u26ab"),
        "MANUAL_REVIEW": ("orange", "\u26a0\ufe0f"),
        "REFUNDED": ("gray", "\u26ab"),
        "UNPAID": ("red", "\u274c"),
        "REGISTERED": ("blue", "\U0001f535"),
    }
    color, icon = colors.get(status.upper(), ("gray", "\u26ab"))
    return f"{icon} {status.upper()}"
