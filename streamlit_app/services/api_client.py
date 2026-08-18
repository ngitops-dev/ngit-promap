import streamlit as st
import httpx

from config import APP_ENV, FASTAPI_BASE_URL


class APIClient:
    def __init__(self):
        self.base_url = FASTAPI_BASE_URL

    def _headers(self) -> dict:
        h = {"Content-Type": "application/json"}
        token = st.session_state.get("token")
        if token:
            h["Authorization"] = f"Bearer {token}"
        return h

    def _get(self, path: str) -> dict | list | None:
        try:
            resp = httpx.get(f"{self.base_url}{path}", headers=self._headers(), timeout=10)
            resp.raise_for_status()
            return resp.json()
        except httpx.ConnectError:
            st.error("Cannot connect to FastAPI backend. Is it running on port 8000?")
            return None
        except Exception as e:
            st.error(f"API error: {e}")
            return None

    def _post(self, path: str, data: dict = None) -> dict | None:
        try:
            resp = httpx.post(f"{self.base_url}{path}", headers=self._headers(), json=data or {}, timeout=10)
            resp.raise_for_status()
            return resp.json()
        except httpx.ConnectError:
            st.error("Cannot connect to FastAPI backend. Is it running on port 8000?")
            return None
        except Exception as e:
            st.error(f"API error: {e}")
            return None

    def _put(self, path: str, data: dict = None) -> dict | None:
        try:
            resp = httpx.put(f"{self.base_url}{path}", headers=self._headers(), json=data or {}, timeout=10)
            resp.raise_for_status()
            return resp.json()
        except httpx.ConnectError:
            st.error("Cannot connect to FastAPI backend. Is it running on port 8000?")
            return None
        except Exception as e:
            st.error(f"API error: {e}")
            return None

    def get_programs(self) -> list:
        return self._get("/api/v1/programs") or []

    def get_program(self, program_id: str) -> dict | None:
        return self._get(f"/api/v1/programs/{program_id}")

    def create_program(self, data: dict) -> dict | None:
        return self._post("/api/v1/programs", data)

    def update_program(self, program_id: str, data: dict) -> dict | None:
        return self._put(f"/api/v1/programs/{program_id}", data)

    def get_cohorts(self, program_id: str = None) -> list:
        path = "/api/v1/cohorts"
        if program_id:
            path += f"?program_id={program_id}"
        return self._get(path) or []

    def get_cohort(self, cohort_id: str) -> dict | None:
        return self._get(f"/api/v1/cohorts/{cohort_id}")

    def create_cohort(self, data: dict) -> dict | None:
        return self._post("/api/v1/cohorts", data)

    def update_cohort(self, cohort_id: str, data: dict) -> dict | None:
        return self._put(f"/api/v1/cohorts/{cohort_id}", data)

    def get_registrations(self, program_id=None, cohort_id=None, payment_status=None, email=None) -> list:
        params = []
        if program_id:
            params.append(f"program_id={program_id}")
        if cohort_id:
            params.append(f"cohort_id={cohort_id}")
        if payment_status:
            params.append(f"payment_status={payment_status}")
        if email:
            params.append(f"email={email}")
        query = f"?{'&'.join(params)}" if params else ""
        return self._get(f"/api/v1/registrations{query}") or []

    def get_registration(self, reg_id: str) -> dict | None:
        return self._get(f"/api/v1/registrations/{reg_id}")

    def create_registration(self, data: dict) -> dict | None:
        return self._post("/api/v1/registrations", data)

    def resend_confirmation(self, reg_id: str, email: str = None, whatsapp_link: str = None) -> dict | None:
        body = {}
        if email:
            body["email"] = email
        if whatsapp_link:
            body["whatsapp_link"] = whatsapp_link
        return self._post(f"/api/v1/registrations/{reg_id}/resend-confirmation", body)

    def get_payments(self, status=None, program_id=None) -> list:
        params = []
        if status:
            params.append(f"status={status}")
        if program_id:
            params.append(f"program_id={program_id}")
        query = f"?{'&'.join(params)}" if params else ""
        return self._get(f"/api/v1/payments{query}") or []

    def get_payment(self, payment_id: str) -> dict | None:
        return self._get(f"/api/v1/payments/{payment_id}")

    def verify_payment(self, reference: str) -> dict | None:
        return self._post(f"/api/v1/payments/{reference}/verify")

    def get_system_health(self) -> dict | None:
        return self._get("/health")


def get_api_client() -> APIClient:
    return APIClient()
