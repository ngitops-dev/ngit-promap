import streamlit as st

from services.api_client import get_api_client
from utils.formatting import format_date


def render():
    st.title("Pending Payments")

    api = get_api_client()
    programs = api.get_programs()
    registrations = api.get_registrations()

    prog_names = {p["program_id"]: p["program_name"] for p in programs}

    pending = [r for r in registrations if r.get("payment_status") in ("UNPAID", "PENDING")]

    st.subheader("Summary by Program")
    prog_stats = {}
    for r in registrations:
        prog_id = r.get("program_id", "")
        name = prog_names.get(prog_id, prog_id)
        if name not in prog_stats:
            prog_stats[name] = {"total": 0, "pending": 0}
        prog_stats[name]["total"] += 1
        if r.get("payment_status") in ("UNPAID", "PENDING"):
            prog_stats[name]["pending"] += 1

    if prog_stats:
        cols = st.columns(len(prog_stats))
        for i, (name, stats) in enumerate(prog_stats.items()):
            with cols[i]:
                conversion = ((stats["total"] - stats["pending"]) / stats["total"] * 100) if stats["total"] > 0 else 0
                st.metric(name, f"{stats['pending']} pending", f"{conversion:.1f}% conversion")
    else:
        st.info("No registration data yet.")

    st.divider()

    st.subheader(f"Participants Awaiting Payment ({len(pending)})")

    if not pending:
        st.info("All registered participants have completed payment.")
        return

    for reg in pending:
        prog_name = prog_names.get(reg.get("program_id", ""), reg.get("program_id", ""))
        with st.container():
            c1, c2, c3 = st.columns([2, 2, 1])
            with c1:
                st.markdown(f"**{reg.get('full_name', '')}**")
                st.caption(reg.get("email", ""))
            with c2:
                st.markdown(f"**{prog_name}**")
                st.caption(format_date(reg.get("created_at", "")))
            with c3:
                if st.button("Resend", key=f"resend_{reg['registration_id']}"):
                    st.session_state[f"show_resend_{reg['registration_id']}"] = True

            if st.session_state.get(f"show_resend_{reg['registration_id']}"):
                with st.expander("Confirm Resend", expanded=True):
                    st.markdown(f"**Sending payment reminder to:** {reg.get('full_name', '')}")
                    resend_email = st.text_input(
                        "Recipient Email",
                        value=reg.get("email", ""),
                        key=f"resend_email_{reg['registration_id']}",
                    )
                    resend_whatsapp = st.text_input(
                        "WhatsApp Group Link",
                        value="",
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
                                st.success(f"Payment reminder sent to {resend_email}!")
                            st.session_state[f"show_resend_{reg['registration_id']}"] = False
                            st.rerun()
                    with col_cancel:
                        if st.button("Cancel", key=f"cancel_resend_{reg['registration_id']}"):
                            st.session_state[f"show_resend_{reg['registration_id']}"] = False
                            st.rerun()

            st.divider()
