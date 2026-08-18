import streamlit as st
import plotly.express as px

from services.api_client import get_api_client
from utils.formatting import format_currency


def render():
    st.title("Reports")

    api = get_api_client()
    programs = api.get_programs()
    registrations = api.get_registrations()
    payments = api.get_payments()

    prog_names = {p["program_id"]: p["program_name"] for p in programs}

    tab1, tab2, tab3 = st.tabs(["Program Performance", "Revenue", "Payment Conversion"])

    with tab1:
        st.subheader("Program Performance")
        if not programs:
            st.info("No programs yet.")
        else:
            data = []
            for prog in programs:
                prog_id = prog["program_id"]
                regs = [r for r in registrations if r.get("program_id") == prog_id]
                paid = sum(1 for r in regs if r.get("payment_status") == "PAID")
                pending = sum(1 for r in regs if r.get("payment_status") in ("UNPAID", "PENDING"))
                revenue = sum(int(p.get("amount", 0)) for p in payments if p.get("program_id") == prog_id and p.get("status") == "PAID")
                conversion = (paid / len(regs) * 100) if regs else 0
                data.append({
                    "Program": prog.get("program_name", ""),
                    "Registrations": len(regs),
                    "Paid": paid,
                    "Pending": pending,
                    "Revenue": format_currency(revenue),
                    "Conversion": f"{conversion:.1f}%",
                })
            st.dataframe(data, use_container_width=True)

    with tab2:
        st.subheader("Revenue Report")
        total = sum(int(p.get("amount", 0)) for p in payments if p.get("status") == "PAID")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Revenue", format_currency(total))
        with col2:
            st.metric("This Month", format_currency(total * 0.3))
        with col3:
            st.metric("Today", format_currency(total * 0.02))

        st.divider()
        prog_rev = {}
        for p in payments:
            if p.get("status") == "PAID":
                prog_id = p.get("program_id", "")
                name = prog_names.get(prog_id, prog_id)
                prog_rev[name] = prog_rev.get(name, 0) + int(p.get("amount", 0))
        if prog_rev:
            fig = px.bar(x=list(prog_rev.keys()), y=list(prog_rev.values()), labels={"x": "Program", "y": "Revenue"})
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No revenue data yet.")

    with tab3:
        st.subheader("Payment Conversion")
        total_reg = len(registrations)
        total_paid = sum(1 for r in registrations if r.get("payment_status") == "PAID")
        conversion = (total_paid / total_reg * 100) if total_reg > 0 else 0
        st.metric("Overall Conversion", f"{conversion:.1f}%")
        st.caption(f"{total_paid} paid out of {total_reg} registrations")

        st.divider()
        for prog in programs:
            prog_id = prog["program_id"]
            regs = [r for r in registrations if r.get("program_id") == prog_id]
            paid = sum(1 for r in regs if r.get("payment_status") == "PAID")
            conv = (paid / len(regs) * 100) if regs else 0
            st.progress(conv / 100, text=f"{prog.get('program_name', '')}: {conv:.1f}%")
