Subject: URGENT: Secrets exposed and repository history rewritten — re-clone required

Hi team,

We discovered that environment files containing secrets were accidentally committed to this repository. I have removed the files from the current repository tip, purged them from the history, and force-pushed a cleaned `main` branch. A backup branch named `backup-before-purge` was created before the purge.

What you must do now:
- Immediately rotate any credentials that may have been exposed: Django `SECRET_KEY`, DB passwords, SMTP/app passwords, and any API keys referenced in the `.env` files.
- Delete any locally cached sensitive files you may have (e.g., `.env`, `db.sqlite3`).
- Re-clone the repository to get the updated history:

  ```bash
  git clone https://github.com/Jasney/farmconnect.git
  ```

If you have local branches you must preserve, follow these advanced steps instead of re-cloning (reach out if you need help).

If you did not intentionally add secrets to the repo, please confirm whether you pushed anything else recently.

Thanks — please treat this as high priority.
