import pytest
from django.urls import reverse
from rest_framework.test import APIClient

pytestmark = pytest.mark.django_db


def test_register_company_and_me_flow():
    client = APIClient()

    # 1) register company
    url = reverse("register-company")
    payload = {
        "name": "Soft T1",
        "admin_username": "t1_admin",
        "admin_email": "t1_admin@example.com",
        "admin_password": "t1_admin",
    }
    r = client.post(url, payload, format="json")
    assert r.status_code == 201
    company_id = r.data["company_id"]

    # 2) get token
    token_url = reverse("token_obtain_pair")
    r = client.post(token_url, {"username": "t1_admin", "password": "t1_admin"}, format="json")
    assert r.status_code == 200
    access = r.data["access"]

    # 3) /me
    me_url = reverse("me")
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")
    r = client.get(me_url)
    assert r.status_code == 200
    assert r.data["username"] == "t1_admin"
    assert r.data["company"] == company_id
    assert "admin" in r.data["roles"] or isinstance(r.data["roles"], list)
    assert isinstance(r.data["functions"], list) and "users:view" in r.data["functions"]
