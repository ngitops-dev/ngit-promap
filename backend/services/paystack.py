import httpx

from backend.config import settings
from backend.utils.logging import get_logger

logger = get_logger(__name__)

BASE_URL = settings.PAYSTACK_BASE_URL


def _headers() -> dict[str, str]:
    return {
        "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
        "Content-Type": "application/json",
    }


def verify_transaction(reference: str) -> dict | None:
    try:
        resp = httpx.get(
            f"{BASE_URL}/transaction/verify/{reference}",
            headers=_headers(),
            timeout=15,
        )
        resp.raise_for_status()
        data = resp.json()
        if data.get("status") is True:
            return data.get("data")
        logger.warning(
            "Paystack verify returned status=false | reference=%s", reference
        )
        return None
    except httpx.HTTPStatusError as e:
        logger.error(
            "Paystack verify HTTP error | reference=%s | status=%s",
            reference,
            e.response.status_code,
        )
        return None
    except Exception as e:
        logger.error("Paystack verify error | reference=%s | error=%s", reference, e)
        return None


def initialize_transaction(email: str, amount: int, reference: str, metadata: dict | None = None) -> dict | None:
    try:
        body: dict = {
            "email": email,
            "amount": amount,
            "reference": reference,
        }
        if metadata:
            body["metadata"] = metadata
        resp = httpx.post(
            f"{BASE_URL}/transaction/initialize",
            headers=_headers(),
            json=body,
            timeout=15,
        )
        resp.raise_for_status()
        data = resp.json()
        if data.get("status") is True:
            return data.get("data")
        return None
    except Exception as e:
        logger.error("Paystack initialize error | error=%s", e)
        return None
