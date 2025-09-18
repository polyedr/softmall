import pytest
from django.urls import reverse
from rest_framework.test import APIClient

pytestmark = pytest.mark.django_db


def auth_client_for_company(name: str, username: str) -> tuple[APIClient, int, int, str]:
    """Регистрирует компанию, возвращает (клиент с Bearer, company_id, admin_id, access)."""
    client = APIClient()
    r = client.post(
        reverse("register-company"),
        {
            "name": name,
            "admin_username": username,
            "admin_email": f"{username}@example.com",
            "admin_password": username,
        },
        format="json",
    )
    assert r.status_code == 201
    company_id = r.data["company_id"]
    admin_id = r.data["admin_id"]

    tok = client.post(reverse("token_obtain_pair"), {"username": username, "password": username}, format="json")
    assert tok.status_code == 200
    access = tok.data["access"]
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")
    return client, company_id, admin_id, access


def test_settings_effective_company_scope():
    client, company_id, _, _ = auth_client_for_company("Example C", "example_c_admin")

    # создадим словарь настройки и company-значение
    # (эти ручки защищены users:edit — у админа она есть после register-company)
    from settingsapp.models import SettingDict

    sd = SettingDict.objects.create(code="theme", name="Theme")

    r = client.post(
        "/api/settings/values/",
        {"setting": sd.id, "value": {"color": "light"}},
        format="json",
    )
    assert r.status_code == 201

    # проверяем effective -> company
    r = client.get("/api/settings/effective/theme")
    assert r.status_code == 200
    assert r.data["scope"] == "company"
    assert r.data["value"] == {"color": "light"}


def test_catalogs_company_properties_isolation():
    # создаём две компании и по админскому токену в каждой
    client1, company1, admin1, _ = auth_client_for_company("Example C1", "c1_admin")
    client2, company2, admin2, _ = auth_client_for_company("Example C2", "c2_admin")

    # заводим код свойства (глобальный справочник)
    from catalogs.models import PropertyCodeDict

    pcode = PropertyCodeDict.objects.create(code="ui.theme", name="UI Theme")

    # в компании 1 создаём company-property
    r = client1.post(
        "/api/catalogs/company-properties/",
        {"property_code": pcode.id, "value": {"color": "dark"}},
        format="json",
    )
    assert r.status_code == 201

    # компания 2 не должна видеть записи компании 1
    r = client2.get("/api/catalogs/company-properties/")
    assert r.status_code == 200
    assert isinstance(r.data, list)  # pagination off в наших вьюхах
    assert len(r.data) == 0

    # компания 2 создаёт свою запись
    r = client2.post(
        "/api/catalogs/company-properties/",
        {"property_code": pcode.id, "value": {"color": "light"}},
        format="json",
    )
    assert r.status_code == 201

    # теперь у каждой компании видна только своя запись
    r1 = client1.get("/api/catalogs/company-properties/")
    r2 = client2.get("/api/catalogs/company-properties/")
    assert len(r1.data) == 1 and len(r2.data) == 1
    assert r1.data[0]["value"] == {"color": "dark"}
    assert r2.data[0]["value"] == {"color": "light"}
