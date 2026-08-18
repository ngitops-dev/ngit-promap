import streamlit as st

from services.api_client import get_api_client
from utils.formatting import status_badge, format_currency, format_date


def render():
    st.title("Payments")

    api = get_api_client()
    programs = api.get_programs()
    payments = api.get_payments()

    prog_names = {p["program_id"]: p["program_name"] for p in programs}

    col1, col2, col3 = st.columns(3)
    with col1:
        search = st.text_input("Search", placeholder="Reference / Participant")
    with col2:
        status_filter = st.selectbox("Status", ["All", "PAID", "PENDING", "FAILED", "MANUAL_REVIEW"])
    with col3:
        prog_filter = st.selectbox("Program", ["All"] + [p.get("program_name", "") for p in programs])

    if search:
        payments = [p for p in payments if search.lower() in p.get("transaction_reference", "").lower()]
    if status_filter != "All":
        payments = [p for p in payments if p.get("status") == status_filter]
    if prog_filter != "All":
        prog_id = next((p["program_id"] for p in programs if p.get("program_name") == prog_filter), None)
        if prog_id:
            payments = [p for p in payments if p.get("program_id") == prog_id]

    st.caption(f"Showing {len(payments)} payments")
    st.divider()

    if not payments:
        st.info("No payments found.")
        return

    for pay in payments:
        prog_name = prog_names.get(pay.get("program_id", ""), pay.get("program_id", ""))

        with st.expander(f"{pay.get('transaction_reference') or 'N/A'} - {status_badge(pay.get('status', ''))} - {format_currency(pay.get('amount', 0), pay.get('currency', 'NGN'))}"):
            c1, c2 = st.columns(2)
            with c1:
                st.markdown(f"**Reference:** {pay.get('transaction_reference', '')}")
                st.markdown(f"**Amount:** {format_currency(pay.get('amount', 0), pay.get('currency', 'NGN'))}")
                st.markdown(f"**Currency:** {pay.get('currency', '')}")
            with c2:
                st.markdown(f"**Program:** {prog_name}")
                st.markdown(f"**Status:** {status_badge(pay.get('status', ''))}")
                st.markdown(f"**Gateway:** {pay.get('gateway', '')}")
                if pay.get("paid_at"):
                    st.markdown(f"**Paid:** {format_date(pay['paid_at'])}")

            st.divider()
            if pay.get("status") in ("PENDING", "MANUAL_REVIEW"):
                if st.button("Verify with Paystack", key=f"verify_{pay['payment_id']}"):
                    with st.spinner("Verifying payment with Paystack..."):
                        result = api.verify_payment(pay["transaction_reference"])
                        if result and result.get("status") == "verified":
                            st.success("Payment verified successfully!")
                            st.rerun()
                        else:
                            st.error("Verification failed or transaction not found.")
