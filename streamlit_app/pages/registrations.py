import streamlit as st

from services.api_client import get_api_client
from utils.formatting import status_badge, format_date


def render():
    st.title("Registrations")

    api = get_api_client()
    programs = api.get_programs()
    cohorts = api.get_cohorts()
    registrations = api.get_registrations()

    prog_names = {p["program_id"]: p["program_name"] for p in programs}
    cohort_names = {c["cohort_id"]: c["cohort_name"] for c in cohorts}
    cohort_map = {c["cohort_id"]: c for c in cohorts}

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        search = st.text_input("Search", placeholder="Name / Email / ID")
    with col2:
        prog_filter = st.selectbox("Program", ["All"] + [p.get("program_name", "") for p in programs])
    with col3:
        cohort_filter = st.selectbox("Cohort", ["All"])
    with col4:
        payment_filter = st.selectbox("Payment", ["All", "PAID", "UNPAID", "PENDING", "MANUAL_REVIEW"])

    if search:
        registrations = [r for r in registrations if search.lower() in r.get("full_name", "").lower() or search.lower() in r.get("email", "").lower() or search.lower() in r.get("registration_id", "").lower()]
    if prog_filter != "All":
        prog_id = next((p["program_id"] for p in programs if p.get("program_name") == prog_filter), None)
        if prog_id:
            registrations = [r for r in registrations if r.get("program_id") == prog_id]
    if payment_filter != "All":
        registrations = [r for r in registrations if r.get("payment_status") == payment_filter]

    st.caption(f"Showing {len(registrations)} registrations")
    st.divider()

    if not registrations:
        st.info("No registrations found.")
        return

    for reg in registrations:
        prog_name = prog_names.get(reg.get("program_id", ""), reg.get("program_id", ""))
        cohort_name = cohort_names.get(reg.get("cohort_id", ""), reg.get("cohort_id", ""))
        cohort = cohort_map.get(reg.get("cohort_id", ""), {})
        default_whatsapp = cohort.get("whatsapp_link", "") if isinstance(cohort, dict) else ""

        with st.expander(f"{reg.get('full_name', '')} - {status_badge(reg.get('payment_status', ''))}"):
            c1, c2 = st.columns(2)
            with c1:
                st.markdown(f"**Email:** {reg.get('email', '')}")
                st.markdown(f"**Phone:** {reg.get('phone', '')}")
                st.markdown(f"**Program:** {prog_name}")
                st.markdown(f"**Cohort:** {cohort_name}")
            with c2:
                st.markdown(f"**Registration:** {format_date(reg.get('created_at', ''))}")
                st.markdown(f"**Payment Status:** {status_badge(reg.get('payment_status', ''))}")
                st.markdown(f"**Fulfillment:** {status_badge(reg.get('fulfillment_status', ''))}")
                if reg.get("payment_reference"):
                    st.markdown(f"**Reference:** {reg['payment_reference']}")

            st.divider()
            c_a, c_b, c_c = st.columns(3)
            with c_a:
                if reg.get("payment_status") == "PAID":
                    if st.button("Resend Confirmation", key=f"resend_{reg['registration_id']}"):
                        st.session_state[f"show_resend_{reg['registration_id']}"] = True

            if st.session_state.get(f"show_resend_{reg['registration_id']}"):
                with st.expander("Confirm Resend", expanded=True):
                    st.markdown(f"**Sending to:** {reg.get('full_name', '')}")
                    resend_email = st.text_input(
                        "Recipient Email",
                        value=reg.get("email", ""),
                        key=f"resend_email_{reg['registration_id']}",
                    )
                    resend_whatsapp = st.text_input(
                        "WhatsApp Group Link",
                        value=default_whatsapp,
                        key=f"resend_whatsapp_{reg['registration_id']}",
                        help="Leave empty to use the cohort default link",
                    )

                    col_confirm, col_cancel = st.columns(2)
                    with col_confirm:
                        if st.button("Confirm Send", key=f"confirm_resend_{reg['registration_id']}", type="primary"):
                            result = api.resend_confirmation(
                                reg["registration_id"],
                                email=resend_email,
                                whatsapp_link=resend_whatsapp,
                            )
                            if result:
                                st.success(f"Confirmation sent to {resend_email}!")
                            st.session_state[f"show_resend_{reg['registration_id']}"] = False
                            st.rerun()
                    with col_cancel:
                        if st.button("Cancel", key=f"cancel_resend_{reg['registration_id']}"):
                            st.session_state[f"show_resend_{reg['registration_id']}"] = False
                            st.rerun()

            with c_b:
                if st.button("View Timeline", key=f"timeline_{reg['registration_id']}"):
                    st.info("Timeline feature coming soon")
