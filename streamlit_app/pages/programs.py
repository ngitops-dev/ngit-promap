import streamlit as st

from services.api_client import get_api_client
from utils.formatting import status_badge, format_number


def render():
    st.title("Programs")

    api = get_api_client()

    col1, col2 = st.columns([3, 1])
    with col1:
        search = st.text_input("Search", placeholder="Search programs...")
    with col2:
        st.write("")
        st.write("")
        if st.button("+ Create Program", use_container_width=True):
            st.session_state["show_create_program"] = True

    if st.session_state.get("show_create_program"):
        with st.expander("Create Program", expanded=True):
            with st.form("create_program"):
                name = st.text_input("Program Name")
                desc = st.text_area("Description")
                col_a, col_b = st.columns(2)
                with col_a:
                    currency = st.selectbox("Currency", ["NGN", "USD", "GBP", "EUR"])
                with col_b:
                    status = st.selectbox("Status", ["ACTIVE", "INACTIVE"])
                submitted = st.form_submit_button("Save Program")
                cancel = st.form_submit_button("Cancel")
                if submitted and name:
                    result = api.create_program({
                        "program_name": name,
                        "description": desc,
                        "currency": currency,
                        "status": status,
                    })
                    if result:
                        st.success(f"Program '{name}' created successfully!")
                        st.session_state["show_create_program"] = False
                        st.rerun()
                if cancel:
                    st.session_state["show_create_program"] = False
                    st.rerun()

    programs = api.get_programs()

    if not programs:
        st.info("No programs yet. Create your first program to get started.")
        return

    if search:
        programs = [p for p in programs if search.lower() in p.get("program_name", "").lower()]

    st.divider()

    for prog in programs:
        cohorts = api.get_cohorts(prog["program_id"])
        registrations = api.get_registrations(program_id=prog["program_id"])
        paid_count = sum(1 for r in registrations if r.get("payment_status") == "PAID")

        with st.container():
            c1, c2, c3, c4, c5 = st.columns([3, 1, 1, 1, 1])
            with c1:
                st.markdown(f"**{prog.get('program_name', '')}**")
                desc_text = prog.get("description", "")
                st.caption(desc_text[:60] + "..." if len(desc_text) > 60 else desc_text)
            with c2:
                st.markdown(status_badge(prog.get("status", "")))
            with c3:
                st.metric("Cohorts", len(cohorts))
            with c4:
                st.metric("Registrations", len(registrations))
            with c5:
                st.metric("Paid", paid_count)
            st.divider()
