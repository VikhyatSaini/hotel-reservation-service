# Hotel Reservation Service — Operations Runbook

## 1. Service Overview

The application runs using Docker Compose:

| Service | Purpose |
|---|---|
| `nginx` | HTTP reverse proxy |
| `web` | Gunicorn and Django REST API |
| `db` | PostgreSQL database |

The application is accessed through:

- Liveness: `http://localhost/health/live/`
- Readiness: `http://localhost/health/ready/`

## 2. Check Service Health

Check container status:

```powershell
docker compose ps
```

Check readiness:

```powershell
curl.exe -i http://localhost/health/ready/
```

Expected HTTP status: `200 OK`.

Expected response:

```json
{
  "status": "ready",
  "database": "connected"
}
```

If readiness returns HTTP 503, investigate database availability and application logs.

## 3. Inspect Logs

Application logs:

```powershell
docker compose logs --tail=100 web
```

Nginx logs:

```powershell
docker compose logs --tail=100 nginx
```

Database logs:

```powershell
docker compose logs --tail=100 db
```

Follow application logs continuously:

```powershell
docker compose logs -f web
```

Look for structured events such as:

- `reservation_created`
- `reservation_conflict`

## 4. Recover the Application Container

If the Django application becomes unavailable:

1. Inspect container status:

   ```powershell
   docker compose ps
   ```

2. Inspect application logs:

   ```powershell
   docker compose logs --tail=100 web
   ```

3. Restart the application:

   ```powershell
   docker compose restart web
   ```

4. Wait for the health check to pass:

   ```powershell
   docker compose ps
   ```

5. Verify readiness:

   ```powershell
   curl.exe -i http://localhost/health/ready/
   ```

Expected result: HTTP 200 and database connected.

The PostgreSQL persistent volume should remain untouched during an application-only restart.

## 5. Recover PostgreSQL Connectivity

If PostgreSQL is stopped:

```powershell
docker compose start db
```

Wait until the database reports healthy:

```powershell
docker compose ps
```

Then verify application readiness:

```powershell
curl.exe -i http://localhost/health/ready/
```

Inspect database logs if it does not become healthy:

```powershell
docker compose logs --tail=100 db
```

Do not remove the PostgreSQL volume as a troubleshooting shortcut. Removing the volume can destroy persisted application data.

## 6. Create a PostgreSQL Backup

Create a local backup directory:

```powershell
New-Item -ItemType Directory -Force -Path .\backups
```

Create a custom-format backup inside the database container:

```powershell
docker exec hotel-postgres pg_dump -U hotel_app -d hotel_db -Fc -f /tmp/hotel_backup.dump
```

Copy it to the host:

```powershell
docker cp hotel-postgres:/tmp/hotel_backup.dump .\backups\hotel_backup.dump
```

Inspect the backup:

```powershell
docker exec hotel-postgres pg_restore -l /tmp/hotel_backup.dump
```

Keep backups in a secure location. The local `backups/` directory is excluded from Git.

## 7. Test Database Restore

Restore into a separate test database. Do not overwrite the active application database for a restore test.

Create the test database:

```powershell
docker exec hotel-postgres createdb -U hotel_app hotel_restore_test
```

Copy the backup into the database container if it is not already there:

```powershell
docker cp .\backups\hotel_backup.dump hotel-postgres:/tmp/hotel_backup.dump
```

Restore:

```powershell
docker exec hotel-postgres pg_restore -U hotel_app -d hotel_restore_test --no-owner /tmp/hotel_backup.dump
```

Verify the restored tables and records:

```powershell
docker exec -it hotel-postgres psql -U hotel_app -d hotel_restore_test
```

Inside `psql`:

```sql
\dt

SELECT COUNT(*) FROM rooms_room;

SELECT COUNT(*) FROM reservations_reservation;

SELECT conname, contype
FROM pg_constraint
WHERE conrelid = 'reservations_reservation'::regclass;

SELECT extname
FROM pg_extension
WHERE extname = 'btree_gist';
```

Exit with:

```sql
\q
```

The restore test for this project verified 12 tables, 5 rooms, 5 reservations, the date-range check constraint, the overlap exclusion constraint, and the `btree_gist` extension.

## 8. Deploy or Roll Back an Application Image

The application image is versioned in GitHub Container Registry.

Before changing versions:

1. Identify a previously tested image tag.
2. Confirm that the image is compatible with the current database schema and health endpoints.
3. Update the `web.image` value in `docker-compose.yml`.
4. Pull and recreate the application container:

   ```powershell
   docker compose pull web
   docker compose up -d --no-deps --force-recreate web
   ```

5. Verify:

   ```powershell
   docker compose ps
   curl.exe -i http://localhost/health/ready/
   ```

A version change is not considered a successful rollback until the container is healthy and the application readiness check passes.

The earlier rollback experiment used an image that did not expose the current health endpoint. That attempt was not considered a successful rollback.

## 9. Important Safety Notes

- Never commit `.env` or real credentials.
- Never delete the PostgreSQL volume as a routine restart step.
- Verify backups before relying on them.
- Test restores in a separate database first.
- Confirm image and database-schema compatibility before rolling back.
- Verify readiness after every recovery or deployment operation.