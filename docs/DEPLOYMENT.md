# Local operation and institutional hosting

## Personal or demonstration machine

Python 3.10+ is required. Run `python server.py`; it binds only `127.0.0.1:8765`. Use `--port 8770` to choose another local port. The bundled threaded wsgiref server is intended for local learning and demonstration. It does not expose the machine to the campus network.

For a teacher, run `python server.py create-teacher --username teacher` against the same `OPENSTUDIO_DB` path used by the service. The command prompts for a password and confirmation. There are no preconfigured accounts.

## Shared campus service

The provided production entry point is `app.wsgi:application`. Use an institution-managed WSGI host behind HTTPS with `OPENSTUDIO_ORIGIN` equal to the one exact public origin, and `OPENSTUDIO_DB` pointing to a writable non-public directory. For example, with a separately installed and maintained Gunicorn:

```bash
export OPENSTUDIO_ORIGIN=https://studio.example.edu
export OPENSTUDIO_DB=/srv/openstudio-private/studio.sqlite3
export OPENSTUDIO_REGISTRATION=1
gunicorn --workers 1 --threads 4 --bind 127.0.0.1:8765 app.wsgi:application
```

This is a configuration example, not a claim that a campus host or domain has been deployed. The reverse proxy must preserve the public Host header, terminate TLS, limit request sizes and provide its own access controls/rate limits. Login throttling in this release is process-local; use one worker or enforce a shared proxy-level rate limit. Install the chosen WSGI host according to its maintained official documentation.

Set registration to 0 after account provisioning when appropriate. No public teacher self-registration is available. Place the repository under a read-only service account except for its private data directory; never serve that directory as static content.

## Backup and data ownership

Keep exports for individual portability. For server backups, stop the service before copying the database, or use SQLite's online backup API; do not copy only a live main database while ignoring WAL files. Restrict backups like the original database. The source release contains no student records or real login credentials.

The current product does not implement institutional SSO, password-reset email, centralized retention scheduling, public student galleries or full administrative deletion workflows. Add these deliberately for the institution's own operational requirements rather than treating a local prototype as a complete campus identity system.
