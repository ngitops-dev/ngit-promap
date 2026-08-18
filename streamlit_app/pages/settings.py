import streamlit as st

from utils.auth import get_current_user, get_current_role


def render():
    st.title("Settings")

    user = get_current_user()
    role = get_current_role()

    tab1, tab2, tab3 = st.tabs(["General", "Payment", "Security"])

    with tab1:
        st.subheader("General Settings")
        with st.form("general_settings"):
            st.text_input("Organization Name", value="NGiT Academy")
            st.selectbox("Default Currency", ["NGN", "USD", "GBP", "EUR"])
            st.selectbox("Timezone", ["Africa/Lagos", "UTC", "US/Eastern"])
            st.form_submit_button("Save")

    with tab2:
        st.subheader("Payment Settings")
        st.markdown("**Paystack:** Configure in `.env` file")
        st.code("PAYSTACK_SECRET_KEY=sk_test_xxx\nPAYSTACK_WEBHOOK_SECRET=sk_test_xxx", language="bash")

    with tab3:
        st.subheader("Security")
        if role == "Super Admin":
            st.markdown("**Admin Users**")
            st.info("Admin user management will be available in a future update.")
        else:
            st.info("Only Super Admin can manage users.")
