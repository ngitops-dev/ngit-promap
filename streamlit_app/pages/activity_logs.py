import streamlit as st


def render():
    st.title("Activity Logs")
    st.info("Audit trail and activity logs will be available in a future update.")
    st.divider()
    st.markdown("""
    **Coming soon:**
    - Admin action history
    - Payment verification logs
    - Email send logs
    - Filter by user, action, date
    """)
