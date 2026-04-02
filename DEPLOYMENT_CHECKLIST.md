# Farm Connect - PythonAnywhere Deployment Checklist

## Pre-Deployment

- [ ] All code changes are committed and pushed to Git
- [ ] `requirements.txt` is up to date with all dependencies
- [ ] `SECRET_KEY` is strong and unique (use `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"`)
- [ ] `.env.example` provides all required environment variable names
- [ ] `ALLOWED_HOSTS` in `.env` includes your PythonAnywhere domain

## PythonAnywhere Setup

- [ ] PythonAnywhere account created
- [ ] Web app created with Python 3.10+
- [ ] MySQL database created with strong password
- [ ] Code cloned/uploaded to `/home/yourusername/mysite`
- [ ] Virtual environment created: `mkvirtualenv --python=/usr/bin/python3.10 farmconnect`
- [ ] Dependencies installed: `pip install -r requirements.txt`

## Configuration

- [ ] `.env` file created with all required variables
- [ ] Database credentials match PythonAnywhere MySQL setup
- [ ] Email settings configured (Gmail or alternative)
- [ ] `SECURE_SSL_REDIRECT=True` in `.env`
- [ ] `SESSION_COOKIE_SECURE=True` and `CSRF_COOKIE_SECURE=True` in `.env`

## Django Setup

- [ ] Migrations applied: `python manage.py migrate`
- [ ] Superuser created: `python manage.py createsuperuser`
- [ ] Static files collected: `python manage.py collectstatic --noinput`
- [ ] Django system check passed: `python manage.py check`

## Web App Configuration

- [ ] WSGI file updated with correct project path and virtual environment
- [ ] Virtual environment path set correctly in Web app settings
- [ ] Static files URL mapping configured: `/static/` → `/home/yourusername/mysite/staticfiles`
- [ ] Media files URL mapping configured: `/media/` → `/home/yourusername/mysite/media`

## Testing

- [ ] Web app reloaded
- [ ] Homepage loads without 500 errors
- [ ] User can register a new account
- [ ] User can log in
- [ ] Admin panel accessible at `/admin/`
- [ ] Database queries work correctly
- [ ] Static files (CSS, JS, images) load properly
- [ ] Image uploads to media folder work

## Security

- [ ] `DEBUG = False` in production
- [ ] `SECURE_SSL_REDIRECT = True` enabled
- [ ] HTTPS certificate active (PythonAnywhere provides free SSL)
- [ ] `.env` is in `.gitignore` and not committed
- [ ] Database password is strong and stored securely
- [ ] Email credentials use app-specific passwords (for Gmail)

## Post-Deployment

- [ ] Set up automated backups for database
- [ ] Monitor error logs regularly
- [ ] Enable logging for critical operations
- [ ] Test email notifications
- [ ] Verify all user workflows (Farmer, Buyer, Admin)
- [ ] Set up monitoring/alerts for downtime

## Maintenance

- [ ] Set up regular backups
- [ ] Monitor disk usage and database size
- [ ] Keep dependencies updated (pip install --upgrade -r requirements.txt)
- [ ] Review error logs weekly
- [ ] Test disaster recovery procedures

## Emergency Contacts

- PythonAnywhere Support: https://www.pythonanywhere.com/help/
- Django Documentation: https://docs.djangoproject.com/
- Your Domain Provider: [Add your provider's support]

---
**Last Updated:** March 31, 2026
**Version:** 1.0
