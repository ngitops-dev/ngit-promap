import streamlit as st

from services.api_client import get_api_client
from utils.formatting import status_badge, format_date


def render():
    st.title("Cohorts")

    api = get_api_client()
    programs = api.get_programs()
    cohorts = api.get_cohorts()

    prog_names = {p["program_id"]: p["program_name"] for p in programs}

    col1, col2 = st.columns([3, 1])
    with col1:
        prog_filter = st.selectbox("Filter by Program", ["All"] + [p.get("program_name", "") for p in programs])
    with col2:
        st.write("")
        st.write("")
        if st.button("+ Create Cohort", use_container_width=True):
            st.session_state["show_create_cohort"] = True

    if st.session_state.get("show_create_cohort"):
        with st.expander("Create Cohort", expanded=True):
            with st.form("create_cohort"):
                program = st.selectbox("Program", [p.get("program_name", "") for p in programs])
                name = st.text_input("Cohort Name")
                col_a, col_b = st.columns(2)
                with col_a:
                    start = st.date_input("Start Date")
                with col_b:
                    end = st.date_input("End Date")
                deadline = st.date_input("Registration Deadline")
                capacity = st.number_input("Capacity", min_value=1, value=100)
                st.subheader("Payment Configuration")
                col_x, col_y = st.columns(2)
                with col_x:
                    amount = st.number_input("Amount (Kobo)", value=5000000)
                with col_y:
                    currency = st.selectbox("Currency", ["NGN"])
                paystack_page = st.text_input("Paystack Page")
                whatsapp = st.text_input("WhatsApp Group Link")
                email_template = st.text_input("Email Template")
                status = st.selectbox("Status", ["UPCOMING", "ACTIVE", "INACTIVE"])

                submitted = st.form_submit_button("Create Cohort")
                cancel = st.form_submit_button("Cancel")
                if submitted and name:
                    program_id = next((p["program_id"] for p in programs if p.get("program_name") == program), "")
                    result = api.create_cohort({
                        "program_id": program_id,
                        "cohort_name": name,
                        "start_date": str(start),
                        "end_date": str(end),
                        "registration_deadline": str(deadline),
                        "capacity": str(capacity),
                        "expected_amount": str(amount),
                        "currency": currency,
                        "paystack_page": paystack_page,
                        "whatsapp_link": whatsapp,
                        "email_template": email_template,
                        "status": status,
                    })
                    if result:
                        st.success(f"Cohort '{name}' created!")
                        st.session_state["show_create_cohort"] = False
                        st.rerun()
                if cancel:
                    st.session_state["show_create_cohort"] = False
                    st.rerun()

    if prog_filter != "All":
        prog_id = next((p["program_id"] for p in programs if p.get("program_name") == prog_filter), None)
        if prog_id:
            cohorts = [c for c in cohorts if c.get("program_id") == prog_id]

    if not cohorts:
        st.info("No cohorts yet. Create your first cohort to get started.")
        return

    st.divider()

    for cohort in cohorts:
        prog_name = prog_names.get(cohort.get("program_id", ""), cohort.get("program_id", ""))
        with st.container():
            c1, c2, c3, c4, c5 = st.columns([2, 2, 1, 1, 1])
            with c1:
                st.markdown(f"**{prog_name}**")
            with c2:
                st.markdown(f"**{cohort.get('cohort_name', '')}**")
            with c3:
                st.markdown(status_badge(cohort.get("status", "")))
            with c4:
                st.caption(f"Start: {format_date(cohort.get('start_date', ''))}")
            with c5:
                st.caption(f"Capacity: {cohort.get('capacity', '0')}")
            st.divider()
