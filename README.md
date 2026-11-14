# Hotel Reservation Service

A containerized hotel reservation API built with Django REST Framework and PostgreSQL, with CI/CD, health checks, security scanning, and recovery procedures.

## 1. Project Overview

Briefly describe the service and its purpose.

## 2. Architecture

Describe the request flow:

Client → Nginx → Gunicorn/Django REST API → PostgreSQL

CI/CD: GitHub Actions → GHCR → Docker Compose deployment.

(Add an architecture diagram.)

## 3. Technology Stack

- Python / Django / Django REST Framework
- PostgreSQL
- Docker and Docker Compose
- Gunicorn and Nginx
- GitHub Actions and GitHub Container Registry
- Ruff and pytest
- Trivy

## 4. Features

- Room availability search
- Reservation creation
- Prevention of overlapping confirmed reservations
- Database-level date-range and overlap constraints
- Health and readiness endpoints
- Structured application logs
- Repeatable seed data

## 5. Prerequisites

List the required tools and versions.

## 6. Configuration

Explain environment variables and `.env.example`.

Never include real credentials or secret values.

## 7. Run Locally

Document the exact commands to build and start the services, apply migrations, seed data, and run tests.

## 8. API Endpoints

Document each endpoint, required parameters, example requests, and expected responses.

## 9. CI/CD

Explain the GitHub Actions workflow, image build, version tags, and GHCR publishing.

## 10. Security

Document non-root execution, dependency separation, environment-based secrets, and Trivy scan results, including unresolved findings.

## 11. Health Checks and Troubleshooting

### Application Restart Recovery

1. Stopped the Django application using `docker compose stop web`.
2. Verified the application became unavailable through Nginx.
3. Restarted the application using `docker compose start web`.
4. Verified the web container returned to `healthy`.
5. Verified `GET /health/ready/` returned HTTP 200.
6. Confirmed the readiness response reported `"database": "connected"`.

**Result:** Application successfully recovered without recreating the database container or losing persisted data.

## 12. Backup and Restore

Created a PostgreSQL custom-format backup using pg_dump -Fc.

Inspected the archive using pg_restore -l.

Restored the backup into a separate database, hotel_restore_test.

Verified 12 restored tables.

Verified 5 room records and 5 reservation records.

Confirmed restoration of:

valid_reservation_date_range

prevent_overlapping_confirmed_reservations

btree_gist extension

Original production database remained untouched during the restore test.

Result: Backup archive successfully restored and database integrity objects verified.
## 13. Rollback

Document how to return to a previously working image version.

## 14. Evidence and Limitations

Link screenshots or reports and clearly state any unfinished work.