import streamlit as st
import plotly.express as px

from services.api_client import get_api_client
from utils.formatting import format_currency, format_number, format_date


def render():
    st.title("Dashboard")

    api = get_api_client()
    programs = api.get_programs()
    registrations = api.get_registrations()
    payments = api.get_payments()

    col1, col2, col3, col4 = st.columns(4)
    total_reg = len(registrations)
    paid = sum(1 for r in registrations if r.get("payment_status") == "PAID")
    pending = sum(1 for r in registrations if r.get("payment_status") in ("UNPAID", "PENDING"))
    revenue = sum(int(p.get("amount", 0)) for p in payments if p.get("status") == "PAID")

    with col1:
        st.metric("Registrations", format_number(total_reg))
    with col2:
        st.metric("Paid", format_number(paid))
    with col3:
        st.metric("Pending", format_number(pending))
    with col4:
        st.metric("Revenue", format_currency(revenue))

    st.divider()

    col_a, col_b = st.columns(2)
    with col_a:
        st.subheader("Payment Conversion")
        conversion = (paid / total_reg * 100) if total_reg > 0 else 0
        st.metric("Conversion Rate", f"{conversion:.1f}%")

    with col_b:
        st.subheader("Active Programs")
        active = sum(1 for p in programs if p.get("status") == "ACTIVE")
        st.metric("Active Programs", active)

    st.divider()

    col_x, col_y = st.columns(2)
    with col_x:
        st.subheader("Revenue by Program")
        prog_rev = {}
        for p in payments:
            if p.get("status") == "PAID":
                prog_id = p.get("program_id", "")
                name = next((pr["program_name"] for pr in programs if pr["program_id"] == prog_id), prog_id)
                prog_rev[name] = prog_rev.get(name, 0) + int(p.get("amount", 0))
        if prog_rev:
            fig = px.bar(x=list(prog_rev.keys()), y=list(prog_rev.values()), labels={"x": "Program", "y": "Revenue (Kobo)"})
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No revenue data yet.")

    with col_y:
        st.subheader("Registrations by Program")
        prog_reg = {}
        for r in registrations:
            prog_id = r.get("program_id", "")
            name = next((p["program_name"] for p in programs if p["program_id"] == prog_id), prog_id)
            prog_reg[name] = prog_reg.get(name, 0) + 1
        if prog_reg:
            fig = px.pie(values=list(prog_reg.values()), names=list(prog_reg.keys()))
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No registration data yet.")

    st.divider()
    st.info("Recent activity and notifications will be available in a future update.")
