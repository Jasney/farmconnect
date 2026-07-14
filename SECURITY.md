**Incident**: Sensitive environment files were accidentally committed and pushed to this repository. I removed the files from the repository tip and rewrote history to purge them, then force-pushed a cleaned history to `origin/main`.

**Files removed**: `.env`, `.env.production`, `db.sqlite3`, `temp_url_debug.py`, `temp_url_inspect.py`, `temp_url_key_debug.py` (purged from history where possible).

**Immediate actions you must take now**
- Rotate all secrets and credentials that were in the environment files (Django `SECRET_KEY`, database credentials, SMTP/app passwords, API keys). Do not delay.
- Update environment variables and deployment config with the new credentials and restart services.
- Revoke any leaked API keys or app passwords at their providers.
- Ensure CI/CD and GitHub Actions secrets are rotated where used.

**How to rotate common secrets (examples)**
- Generate a new Django SECRET_KEY:

  ```bash
  python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
  ```

  Replace the `SECRET_KEY` value in your deployment environment (do NOT commit it to the repo).

- Rotate a MySQL user password (example):

  ```sql
  ALTER USER 'db_user'@'host' IDENTIFIED BY 'new_password';
  FLUSH PRIVILEGES;
  ```

  Then update the environment variable used by your app and restart the app service.

- Rotate PostgreSQL password (example):

  ```sql
  ALTER ROLE db_user WITH PASSWORD 'new_password';
  ```

- Revoke or replace SMTP/app passwords (e.g., Google App Passwords, SendGrid API keys) from their provider dashboards and update your environment.

**Repository and collaborator steps**
- All collaborators must re-clone the repository to avoid retaining references to the old history:

  ```bash
  git clone https://github.com/Jasney/farmconnect.git
  ```

  Alternatively, if you must preserve local branches, follow the advanced steps in `DRAFT_NOTIFY_COLLABORATORS.md`.

- I created a backup branch `backup-before-purge` in the remote before the history rewrite. This branch contains the pre-purge history and may still contain secrets. If you do not need it, delete it from the remote immediately:

  ```bash
  git push origin --delete backup-before-purge
  ```

**Notes**
- I removed sensitive files from the repository history and force-pushed. This rewrite is destructive to history — after this, re-cloning is the safest option.
- If you want, I can (A) produce a short email/PR comment to notify collaborators, (B) create a GitHub Issue describing the timeline, or (C) remove the `backup-before-purge` branch from the remote now. Tell me which.

**Contact**
If you'd like me to perform additional actions (create the notification, delete the backup branch, or open an Issue), reply with your choice.
