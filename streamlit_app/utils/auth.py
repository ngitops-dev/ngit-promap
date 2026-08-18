import streamlit as st

from config import APP_ENV


def check_auth() -> bool:
    return st.session_state.get("authenticated", False)


def get_current_user() -> dict | None:
    return st.session_state.get("user", None)


def get_current_role() -> str:
    user = get_current_user()
    return user.get("role", "") if user else ""


def require_role(roles: list[str]) -> bool:
    role = get_current_role()
    return role in roles


def login_user(user: dict) -> None:
    st.session_state["authenticated"] = True
    st.session_state["user"] = user


def logout_user() -> None:
    st.session_state["authenticated"] = False
    st.session_state["user"] = None
    st.session_state.pop("token", None)
