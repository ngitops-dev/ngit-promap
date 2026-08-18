import json

from fastapi.testclient import TestClient

from backend.main import app

client = TestClient(app)


def test_webhook_missing_signature():
    response = client.post(
        "/webhooks/paystack",
        content=json.dumps({"type": "charge.success", "data": {}}),
        headers={"Content-Type": "application/json"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "error"


def test_webhook_invalid_json():
    response = client.post(
        "/webhooks/paystack",
        content="not json",
        headers={
            "Content-Type": "application/json",
            "x-paystack-signature": "sig",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "error"
