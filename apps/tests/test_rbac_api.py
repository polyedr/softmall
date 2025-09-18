import pytest
from django.urls import reverse
from rest_framework.test import APIClient

pytestmark = pytest.mark.django_db


def auth_client_for_new_company() -> tuple[APIClient, int, int]:
    """
    Registers a new company, returns (authed client, company_id, admin_user_id)
    with admin JWT access token.
    """
    client = APIClient()

    # register company + admin (admin gets users:view/edit)
    r = client.post(
        reverse("register-company"),
        {
            "name": "Example RBAC",
            "admin_username": "rbac_admin",
            "admin_email": "rbac_admin@example.com",
            "admin_password": "rbac_admin",
        },
        format="json",
    )
    assert r.status_code == 201
    company_id = r.data["company_id"]
    admin_id = r.data["admin_id"]

    # token
    r = client.post(reverse("token_obtain_pair"), {"username": "rbac_admin", "password": "rbac_admin"}, format="json")
    assert r.status_code == 200
    access = r.data["access"]
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")
    return client, company_id, admin_id


def test_role_function_crud_and_assign_user_role():
    client, company_id, admin_id = auth_client_for_new_company()

    # create function (admin has users:edit)
    r = client.post(
        "/api/rbac/functions/", {"code": "users:export", "name": "Export users", "is_active": True}, format="json"
    )
    assert r.status_code == 201
    function_id = r.data["id"]

    # create role
    r = client.post(
        "/api/rbac/roles/",
        {"code": "manager", "name": "Manager", "company": company_id, "is_active": True},
        format="json",
    )
    assert r.status_code == 201
    role_id = r.data["id"]

    # bind function to role
    r = client.post(f"/api/rbac/roles/{role_id}/functions/", {"function": function_id}, format="json")
    assert r.status_code == 201

    # assign role to admin
    r = client.post("/api/rbac/assign-role", {"user_id": admin_id, "role_id": role_id}, format="json")
    assert r.status_code == 201

    # list role-functions
    r = client.get("/api/rbac/role-functions/")
    assert r.status_code == 200
    assert any(obj["function"] == function_id and obj["role"] == role_id for obj in r.data)
