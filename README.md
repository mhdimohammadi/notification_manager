# Notification Manager

A Django REST Framework service for creating and dispatching notifications. Email delivery is implemented end to end. Channel types for SMS and Telegram exist on the model, but sending through those channels is not implemented yet but will be in the future.

The API authenticates with JWT. Notifications are queued with Celery and RabbitMQ, email SMTP passwords are encrypted at rest, Redis is used for cache, idempotency, and rate limiting, and delivery events are stored in MongoDB.

## Architecture

```
Client
  │  JWT
  ▼
Django REST API  ── PostgreSQL (users, channels, email config, notifications)
  │
  ├── Redis
  │     • Django cache (email configuration)
  │     • Idempotency keys
  │     • Rate limiting
  │
  └── Celery (RabbitMQ broker, Redis result backend)
        ├── notification_queue  → dispatch_notification
        ├── email_queue         → send_email
        └── monthly beat        → cleanup_notification_logs
              │
              ├── SMTP (per-channel EmailConfiguration)
              └── MongoDB (notification_logs)
```

### Django apps

| App | Role |
| --- | --- |
| `account` | Custom user model, registration, user CRUD, JWT token endpoints |
| `channel` | Notification channels, encrypted email SMTP configuration, email send task |
| `notification` | Notification records, dispatch, idempotency, rate limiting |
| `notification_log` | MongoDB event logs and retention cleanup |

## Tech stack

| Component | What the project uses |
| --- | --- |
| Language | Python 3.13 (Docker image `python:3.13-alpine`) |
| Framework | Django 6.0.7, Django REST Framework 3.17.1 |
| Auth | JWT via `djangorestframework-simplejwt` |
| PostgreSQL | Primary relational database (`postgres:17-alpine`) |
| Redis | Cache, idempotency, rate limiting, Celery result backend (`redis:7.0.11-alpine`) |
| RabbitMQ | Celery broker (`rabbitmq:management`) |
| MongoDB | Notification event logs (`mongo:8.0`, host port `27018`) |
| Celery | Worker plus Beat scheduler |
| Encryption | Fernet (`cryptography`) for SMTP passwords |

Python dependencies are pinned in `requirements.txt`.

## Requirements

- Docker and Docker Compose (recommended)
- A `.env` file (copy from `.env.example`)
- A Fernet key for `EMAIL_ENCRYPTION_KEY`

To generate a Fernet key:

```bash
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

## Quick start (Docker)

1. Copy environment variables:

   ```bash
   cp .env.example .env
   ```

2. Set at least `SECRET_KEY`, `DB_PASSWORD`, and `EMAIL_ENCRYPTION_KEY`. Keep `DB_HOST=postgres` and the Redis / RabbitMQ / MongoDB URLs as in `.env.example` when using Compose.

3. Start the stack:

   ```bash
   docker compose up --build
   ```

4. The Django container runs migrations, then starts the development server on [http://localhost:8000](http://localhost:8000).

5. Create a superuser if you need Django admin or staff-only APIs:

   ```bash
   docker compose exec django python manage.py createsuperuser
   ```

6. Optionally create MongoDB indexes used by notification logs:

   ```bash
   docker compose exec django python manage.py create_mongo_indexes
   ```

### Compose services

| Service | Purpose | Ports |
| --- | --- | --- |
| `django` | API (`migrate` then `runserver 0.0.0.0:8000`) | `8000` |
| `celery` | Celery worker | — |
| `celery-beat` | Celery Beat | — |
| `postgres` | PostgreSQL 17 | `5432` |
| `redis` | Redis 7 | not published to the host |
| `rabbitmq` | RabbitMQ with management UI | `5672`, `15672` |
| `mongodb` | MongoDB 8 | host `27018` → container `27017` |

Django, Celery, and Beat load `.env` via `env_file`. Persistent volumes: `postgres_data`, `mongodb_data`.

RabbitMQ management is available at [http://localhost:15672](http://localhost:15672) (image default user `guest` / `guest`, matching the sample broker URL).

## Environment variables

Loaded from `.env` by `django-environ` in `NotificationManager/settings.py`.

| Variable | Used for |
| --- | --- |
| `SECRET_KEY` | Django secret key |
| `DEBUG` | Django debug flag |
| `ALLOWED_HOSTS` | Comma-separated host list |
| `DB_NAME` | PostgreSQL database name (also used by the `postgres` service) |
| `DB_USER` | PostgreSQL user |
| `DB_PASSWORD` | PostgreSQL password |
| `DB_HOST` | Database host (`postgres` in Compose) |
| `DB_PORT` | Database port (`5432`) |
| `CELERY_BROKER_URL` | Celery broker (RabbitMQ AMQP URL) |
| `CELERY_RESULT_BACKEND` | Celery results (Redis) |
| `EMAIL_ENCRYPTION_KEY` | Fernet key for encrypting SMTP passwords |
| `REDIS_URL` | Django cache and rate-limit Redis (sample uses DB `1`) |
| `MONGODB_URL` | MongoDB connection string (default database is used for logs) |

`.env` is gitignored. `.env.example` is the documented template.

## Authentication

Default DRF authentication is JWT:

```http
Authorization: Bearer <access_token>
```

Tokens are issued by SimpleJWT’s default views (username and password). There is no project-specific JWT lifetime configuration; library defaults apply.

| Method | Path | Auth |
| --- | --- | --- |
| `POST` | `/register/` | Public |
| `POST` | `/token/` | Public (obtain access and refresh) |
| `POST` | `/token/refresh/` | Public |

Custom user model: `account.User` (`AUTH_USER_MODEL`). Extra fields: unique `email`, unique `phone` (11 digits, must start with `09`). Django admin is at `/admin/`.

## Permissions

There is no global `DEFAULT_PERMISSION_CLASSES`. Each view sets its own rules.

| Resource | Rules |
| --- | --- |
| `POST /register/` | Anyone |
| `/account/` create | Staff (`IsAdminUser`) |
| `/account/` list, retrieve, update, delete | Authenticated. Non-staff users are limited to their own user. Staff see all users. |
| `/channel/` list and retrieve | Authenticated. Non-staff see only `is_active=True` channels. |
| `/channel/` create, update, delete, `activate`, `deactivate` | Staff |
| `/email_config/` | Staff |
| `/notification/` create, list, retrieve | Authenticated. Non-staff list/retrieve only notifications they created. Staff see all. No update or delete API. |
| `/<notification_id>/logs/` | Staff |

Django admin: `User`, `Channel`, and `EmailConfiguration` are registered. `Notification` is registered as read-only (add, change, and delete are disabled).

## API reference

Routers use DRF trailing slashes.

### Accounts (`/account/`)

Standard ModelViewSet: list, create, retrieve, update, partial update, destroy.

**User fields:** `id`, `username`, `password` (write-only), `email`, `first_name`, `last_name`, `phone`, `created_at`, `updated_at`, `last_login`, `date_joined`, `is_active`, `is_staff`, `is_superuser`.

**Register body:** `username`, `email`, `password`, `first_name`, `last_name`, `phone`.

### Channels (`/channel/`)

| Method | Path | Notes |
| --- | --- | --- |
| `GET` | `/channel/` | List |
| `POST` | `/channel/` | Create (`name`, `type`). `is_active` is read-only and defaults to `true` |
| `GET` | `/channel/{id}/` | Retrieve |
| `PUT` / `PATCH` | `/channel/{id}/` | Update |
| `DELETE` | `/channel/{id}/` | Delete |
| `POST` | `/channel/{id}/activate/` | Sets `is_active=true` |
| `POST` | `/channel/{id}/deactivate/` | Sets `is_active=false` |

`type` choices: `email`, `sms`, `telegram`. Only `email` has a send path.

### Email configuration (`/email_config/`)

Full ModelViewSet. One configuration per channel (`OneToOneField`). The linked channel must be type `email`. TLS and SSL cannot both be on; one of them must be on.

| Field | Notes |
| --- | --- |
| `channel` | Channel id |
| `host`, `port`, `username`, `from_email`, `display_name` | SMTP settings |
| `password` | Write-only. Required on create. Encrypted with Fernet (`ENC:` prefix) before save |
| `confirm_password` | Write-only. Must match `password` when a password is set |
| `use_tls` | Default `true` |
| `use_ssl` | Default `false` |
| `timeout` | Default `30` |

On update, omit both password fields to leave the stored password unchanged.

### Notifications (`/notification/`)

Create, list, and retrieve only.

**Create** requires header `Idempotency-Key`. Response is `202 Accepted`.

```json
{
  "channel": 1,
  "recipient": "user@example.com",
  "subject": "Hello",
  "body": "Plain text body",
  "html_body": "<p>Optional HTML</p>"
}
```

`recipient` is an email field. `status` and `failure_reason` are read-only.

Statuses: `pending` → `processing` → `sent` or `failed`.

**Idempotency (Redis, 24-hour TTL)**

- Missing `Idempotency-Key`: `400`
- Same key while the first request is still claimed as processing: `409`
- Same key after a notification id is stored: `202` with the existing notification
- Failed claims are deleted so the key can be reused

**Rate limit (Redis, client IP from `REMOTE_ADDR`)**

- 10 create requests per 60 seconds per IP
- Exceeded: `429` (`too many requests. Try again later.`)
- If the client IP cannot be determined: `400`

After a successful create, `dispatch_notification` is queued on transaction commit.

### Notification logs (`/<id>/logs/`)

`GET` for a notification primary key. Staff only. Returns MongoDB documents for that `notification_id`, ordered by `created_at` ascending.

Log fields: `event`, `notification_id`, `channel_id`, `channel_type`, `status`, `recipient`, `created_at`, `metadata`.

Events written by the workers include `notification.processing`, `notification.sent`, and `notification.failed`.

## Background processing

Celery app: `NotificationManager` (`NotificationManager/celery.py`). Tasks are discovered from installed apps.

### Queues (topic exchange `notification_exchange`)

| Queue | Routing key | Task |
| --- | --- | --- |
| `notification_queue` | `notification` | `notification.tasks.dispatch_notification`, `notification_log.tasks.cleanup_notification_logs` |
| `email_queue` | `email` | `channel.tasks.send_email` |
| `sms_queue` | `sms` | Declared; no routed tasks |
| `telegram_queue` | `telegram` | Declared; no routed tasks |

### `dispatch_notification`

1. Loads the notification, sets status to `processing`, writes a MongoDB log.
2. Fails if the channel is inactive.
3. **Email:** loads `channel.email_configuration` and queues `send_email`.
4. **SMS / Telegram:** raises `NotImplementedError` (notification is marked `failed` via the shared task base class).

### `send_email`

- Reads SMTP settings from Redis cache (1 hour TTL), falling back to PostgreSQL.
- Decrypts the password and sends via Django `EmailBackend` / `EmailMultiAlternatives`.
- Optional HTML alternative when `html_body` is set.
- Connection and timeout errors: retry up to 3 times with backoff `10 * 2 ** retries` seconds.
- Authentication errors are not retried.
- On success, status becomes `sent` and a log is written.

Cache entries are invalidated on `EmailConfiguration` save or delete.

### Task failure handling

`NotificationTask` (`notification/task_base.py`) on failure sets `status=failed`, stores `failure_reason`, and writes `notification.failed` with exception metadata.

### Beat schedule

On the first day of each month at `00:00` UTC, `cleanup_notification_logs` deletes MongoDB log documents older than 90 days.

## Data stores

**PostgreSQL** holds `User`, `Channel`, `EmailConfiguration`, and `Notification`.

**Redis** (`REDIS_URL`):

- Django cache backend for email configuration objects
- Idempotency keys (`notification:idempotency:…`)
- Rate-limit counters (`notification:rate-limit:…`) via a Lua script

Celery results use `CELERY_RESULT_BACKEND` (sample: Redis DB `0`, separate from `REDIS_URL` DB `1`).

**MongoDB** collection `notification_logs` on the default database from `MONGODB_URL`. Indexes (management command): `created_at`; compound `notification_id` + `created_at`.

## Management commands

| Command | Description |
| --- | --- |
| `python manage.py migrate` | Apply PostgreSQL migrations (also run on Django container start) |
| `python manage.py createsuperuser` | Create a staff/superuser |
| `python manage.py create_mongo_indexes` | Create MongoDB indexes for `notification_logs` |
| `python manage.py runserver` | Development server |

## Tests

Each app has a `tests.py` file with the default Django `TestCase` stub. There are no implemented test cases.

## Project layout

```
NotificationManager/     # Django project (settings, URLs, Celery)
account/                 # Users, register, JWT URLs
channel/                 # Channels, email config, SMTP send
notification/            # Notifications, dispatch, idempotency, rate limit
notification_log/        # MongoDB logs, cleanup task, indexes command
docker-compose.yml
Dockerfile
requirements.txt
.env.example
manage.py
```

## License

No license file is included in this repository.
