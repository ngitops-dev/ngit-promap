import streamlit as st
import streamlit_authenticator as stauth

from config import APP_ENV
from utils.auth import check_auth, get_current_user, login_user, logout_user

st.set_page_config(
    page_title="NGiT Program Management Portal PMAP",
    page_icon="\U0001f393",
    layout="wide",
    initial_sidebar_state="expanded",
)

if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False
    st.session_state["user"] = None

if not check_auth():
    st.markdown(
        """
        <style>
        .main { display: flex; justify-content: center; align-items: center; min-height: 80vh; }
        .login-card { background: white; padding: 2rem; border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); max-width: 400px; width: 100%; }
        .login-title { text-align: center; color: #1a1a2e; font-size: 1.8rem; font-weight: 700; margin-bottom: 0.5rem; }
        .login-subtitle { text-align: center; color: #666; font-size: 0.95rem; margin-bottom: 2rem; }
        </style>
        """,
        unsafe_allow_html=True,
    )

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown('<div class="login-title">NGiT Academy</div>', unsafe_allow_html=True)
        st.markdown('<div class="login-subtitle">Admin Portal</div>', unsafe_allow_html=True)

        with st.form("login_form"):
            email = st.text_input("Email", placeholder="admin@ngit.com")
            password = st.text_input("Password", type="password", placeholder="Enter password")
            submitted = st.form_submit_button("Sign In", use_container_width=True)

            if submitted:
                if APP_ENV == "development":
                    demo_users = {
                        "admin@ngit.com": {"name": "Super Admin", "role": "Super Admin", "password": "admin123"},
                        "program@ngit.com": {"name": "Program Admin", "role": "Program Admin", "password": "admin123"},
                        "viewer@ngit.com": {"name": "Viewer", "role": "Viewer", "password": "admin123"},
                    }
                    user = demo_users.get(email.lower().strip())
                    if user and user["password"] == password:
                        login_user({"email": email, "name": user["name"], "role": user["role"]})
                        st.rerun()
                    else:
                        st.error("Invalid email or password")
                else:
                    st.error("Production auth not configured")

        st.caption("Demo: admin@ngit.com / admin123")

    st.stop()


user = get_current_user()
with st.sidebar:
    st.markdown(f"**Welcome, {user['name']}**")
    st.caption(f"Role: {user['role']}")
    st.divider()

    page = st.radio(
        "Navigation",
        ["Dashboard", "Programs", "Cohorts", "Registrations", "Payments", "Pending Payments", "Communications", "Reports", "Settings", "Activity Logs"],
        label_visibility="collapsed",
    )

    st.divider()
    if st.button("Logout", use_container_width=True):
        logout_user()
        st.rerun()

if page == "Dashboard":
    from pages.dashboard import render
    render()
elif page == "Programs":
    from pages.programs import render
    render()
elif page == "Cohorts":
    from pages.cohorts import render
    render()
elif page == "Registrations":
    from pages.registrations import render
    render()
elif page == "Payments":
    from pages.payments import render
    render()
elif page == "Pending Payments":
    from pages.pending_payments import render
    render()
elif page == "Communications":
    from pages.communications import render
    render()
elif page == "Reports":
    from pages.reports import render
    render()
elif page == "Settings":
    from pages.settings import render
    render()
elif page == "Activity Logs":
    from pages.activity_logs import render
    render()
