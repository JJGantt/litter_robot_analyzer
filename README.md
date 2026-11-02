Litter Robot 4 data analyzer/visualizer (weight and frequency trends) with algorithmic cat identification and web interface

## Configuration

The app reads two environment variables and will not start without `SECRET_KEY`:

| variable | what it is |
|---|---|
| `SECRET_KEY` | Signs the session cookie. Any long random value, e.g. `python -c "import secrets; print(secrets.token_hex(32))"`. Changing it logs everyone out. |
| `DATABASE_URL` | Postgres connection URL (`postgres://user:pass@host:port/db`). `init_db.py` creates the tables in it, dropping any that exist. |

Run with `gunicorn app:app` (the `Procfile`).
