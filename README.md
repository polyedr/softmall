# SoftMall Test — Django + DRF (+ Celery)

Мини-API на Django/DRF с модулями **Accounts, RBAC, Settings, Catalogs**.
Поддерживает регистрацию компаний и пользователей, RBAC с датами активности, хранение настроек и свойств, изоляцию данных по компаниям.
Есть идемпотентность в `register-company` (через `Idempotency-Key`), throttling, индексы для Postgres и Celery-таски для рассылок.

## Содержимое

- [Docker](#docker)
- [Требования](#требования)
- [Быстрый старт (локально)](#быстрый-старт-локально)
- [.env — конфигурация](#env--конфигурация)
- [PostgreSQL — создание пользователя и БД](#postgresql--создание-пользователя-и-бд)
- [Redis — брокер для Celery](#redis--брокер-для-celery)
- [Миграции, сиды, запуск](#миграции-сиды-запуск)
- [API](#api)
- [Админка](#админка)
- [Celery](#celery)
- [Тесты](#тесты)
- [Обоснование изменений схемы](#обоснование-изменений-схемы)

---

## Docker

См. отдельную ветку [feature/docker](https://github.com/polyedr/softmall_test/tree/feature/docker)
для запуска проекта в контейнерах (Postgres, Redis, Celery, Django).
В этой ветке — локальный запуск.

---

## Требования

- Python 3.12
- Django 5.1 / DRF 3.15
- PostgreSQL 14+ (у меня проверено на PostgreSQL 17)
- Redis 5+ (для Celery)

---

## Быстрый старт (локально)

```bash
# 1) Клонируем репозиторий
git clone <repo-url> softmall_test
cd softmall_test

# 2) Виртуальное окружение
python3.12 -m venv .venv
source .venv/bin/activate

# 3) Установка зависимостей
pip install -r requirements.txt -r requirements-dev.txt
```
```sql
# 4) Создание БД и пользователя
CREATE USER softmall_user WITH PASSWORD 's63V-}5|KE|H';
DROP DATABASE IF EXISTS softmall_db;
CREATE DATABASE softmall_db OWNER softmall_user;

\c softmall_db
GRANT ALL PRIVILEGES ON DATABASE softmall_db TO softmall_user;
ALTER SCHEMA public OWNER TO softmall_user;
GRANT ALL ON SCHEMA public TO softmall_user;
```
```bash
# 5) Создаём .env (см. ниже)
cp .env.example .env    # или вручную

# 6) Миграции + сиды + запуск
python manage.py migrate
python manage.py seed_initial_data
python manage.py runserver
```

---

## .env — конфигурация

Файл `.env` лежит рядом с `manage.py`.

Пример для Postgres + Redis:

```dotenv
SECRET_KEY=dev-secret
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost

DATABASE_URL=postgres://softmall_user:smp_pass@localhost:5432/softmall_db

CELERY_TASK_ALWAYS_EAGER=False
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/1
```

---

## PostgreSQL — создание пользователя и БД

```sql
CREATE USER softmall_user WITH PASSWORD 's63V-}5|KE|H';
DROP DATABASE IF EXISTS softmall_db;
CREATE DATABASE softmall_db OWNER softmall_user;

\c softmall_db
GRANT ALL PRIVILEGES ON DATABASE softmall_db TO softmall_user;
ALTER SCHEMA public OWNER TO softmall_user;
GRANT ALL ON SCHEMA public TO softmall_user;
```

---

## Redis — брокер для Celery

```bash
sudo zypper install redis
sudo systemctl enable --now redis
redis-cli ping  # ожидаем "PONG"
```

---

## Миграции, сиды, запуск

```bash
python manage.py migrate
python manage.py seed_initial_data   # создаст admin/admin и базовые записи
python manage.py runserver
```

---

## API

Документация (Swagger/Redoc) доступна после запуска:

- http://127.0.0.1:8000/api/schema/swagger-ui/
- http://127.0.0.1:8000/api/schema/redoc/

Коллекция Postman — в корне проекта (`softmall_api.postman_collection.json` + окружение `softmall_local.postman_environment.json`).

Основные группы:
- **Accounts** — регистрация компаний/пользователей, JWT, `/me`.
- **RBAC** — CRUD ролей и функций, назначение ролей.
- **Settings** — словари и значения настроек, ручка `/effective/{code}`.
- **Catalogs** — справочники, свойства компаний и пользователей, лицензии на модули.

---

## Админка

- http://127.0.0.1:8000/admin/
- зарегистрированы все модели (Companies, Users, Roles, Functions, Settings, Properties, Modules).
- `verbose_name`/`plural` для удобочитаемых заголовков.

---

## Celery

- Пример задачи: `accounts.tasks.send_user_mailings`
- Запуск воркера:
  ```bash
  celery -A project worker -l info
  ```
- Тест задачи:
  ```bash
  python manage.py shell -c "from accounts.tasks import send_user_mailings; send_user_mailings.delay(42)"
  ```

---

## Тесты

Тестовый профиль: `project/settings_test.py`.
Запуск:

```bash
pytest -q
```

Покрыто:
- регистрация компании + `/me`;
- CRUD ролей/функций + назначение ролей;
- effective settings;
- изоляция company-properties.

---

## Обоснование изменений схемы

**Что было не так в исходной схеме:**
- Отсутствовали ограничения уникальности (например, для `(company, username)` у User, `(company, code)` у Role). Это допускало дубли.
- Не было индексов по полям, которые часто участвуют в фильтрации (company_id, active_from/active_to, property_code).
- Интервалы активности (`active_from`, `active_to`) не проверялись на корректность (возможен `from > to`).
- Поведение при удалении родительских сущностей не было явно задано (`CASCADE`/`PROTECT`).

**Что исправлено:**
- Добавлены `UniqueConstraint` для ключевых комбинаций (`User`, `Role`, `RoleFunction`, `UserRole`, `SettingValue`, `CompanyProperty`, и др.).
- В моделях и отдельными миграциями добавлены индексы для ускорения выборок:
  - составные (`company + code`, `role + function + active_from`),
  - частичные (Postgres: `WHERE active_to IS NULL`) для поиска «активных сейчас» записей.
- Добавлены `CheckConstraint` для интервалов: `active_from <= active_to OR active_to IS NULL`.
- Явно задано поведение ForeignKey:
  - `PROTECT` там, где удаление родителя недопустимо (например, Function/Role),
  - `CASCADE` там, где зависимые записи не имеют смысла без родителя.
- В `accounts.User` и других таблицах реализована изоляция по компании (все выборки ограничиваются `company_id`).

Эти изменения повышают целостность данных, позволяют эффективно выполнять типовые запросы (фильтрация по активным ролям/функциям/настройкам), и документируют бизнес-логику через саму схему.

---
