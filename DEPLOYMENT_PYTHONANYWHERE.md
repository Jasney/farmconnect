# Farm Connect - PythonAnywhere Deployment Guide

This guide will help you deploy the Farm Connect platform to PythonAnywhere.

## Prerequisites

1. PythonAnywhere account (https://www.pythonanywhere.com)
2. MySQL database enabled on PythonAnywhere
3. Domain name (optional, or use `yourusername.pythonanywhere.com`)

## Step-by-Step Deployment

### 1. Create a PythonAnywhere Web App

1. Log in to your PythonAnywhere account
2. Go to **Web** tab → **Add a new web app**
3. Choose **Manual Configuration** (not web framework)
4. Select **Python 3.10+** (or your preferred version)
5. Note your web app URL: `yourusername.pythonanywhere.com`

### 2. Set Up MySQL Database

1. Go to **Databases** tab
2. Create a new MySQL database
3. Note the **database name**: `yourusername$farmconnect`
4. Note the **hostname**: `yourusername.mysql.pythonanywhere-services.com`
5. Create a strong password and note the **username**: `yourusername`

### 3. Clone/Upload Your Code

Use bash console to clone your repository:

```bash
cd ~
git clone https://github.com/yourusername/farm-connect.git mysite
cd mysite
```

Or upload via file browser if not using git.

### 4. Create Virtual Environment

In your PythonAnywhere bash console:

```bash
mkvirtualenv --python=/usr/bin/python3.10 farmconnect
pip install -r requirements.txt
```

### 5. Configure Environment Variables

Create a `.env` file in your project root:

```bash
vim .env
```

Add the following (update with your actual values):

```
SECRET_KEY=<generate-new-secret-key>
DEBUG=False
ALLOWED_HOSTS=yourusername.pythonanywhere.com

DB_ENGINE=mysql
DB_NAME=yourusername$farmconnect
DB_USER=yourusername
DB_PASSWORD=your_mysql_password
DB_HOST=yourusername.mysql.pythonanywhere-services.com
DB_PORT=3306

SECURE_SSL_REDIRECT=True
SECURE_HSTS_SECONDS=31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True

EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
DEFAULT_FROM_EMAIL=your-email@gmail.com
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
EMAIL_USE_TLS=True
```

**Note:** For Gmail, use an [App Password](https://support.google.com/accounts/answer/185833), not your regular password.

### 6. Generate a New Secret Key

In your bash console:

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Copy the output and add it to your `.env` file.

### 7. Run Migrations

In your bash console:

```bash
cd ~/mysite
workon farmconnect
python manage.py migrate
```

### 8. Create Superuser

```bash
python manage.py createsuperuser
```

Follow the prompts to create your admin account.

### 9. Collect Static Files

```bash
python manage.py collectstatic --noinput
```

### 10. Configure WSGI File

Go to **Web** tab → Your Web App → **WSGI configuration file**

Replace the contents with:

```python
import os
import sys

# Add your project to the path
path = '/home/yourusername/mysite'
if path not in sys.path:
    sys.path.append(path)

# Set Django settings module
os.environ['DJANGO_SETTINGS_MODULE'] = 'farm_connect_platform.settings'

# Import WSGI application
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

Replace `yourusername` with your actual PythonAnywhere username.

### 11. Configure Virtual Environment Path

Go to **Web** tab → Your Web App → **Virtualenv**

Set the path to: `/home/yourusername/.virtualenvs/farmconnect`

### 12. Configure Static Files

Go to **Web** tab → Your Web App → **Static files:**

Add the following mapping:

| URL         | Directory                          |
|-------------|------------------------------------|
| `/static/`  | `/home/yourusername/mysite/staticfiles` |
| `/media/`   | `/home/yourusername/mysite/media/` |

### 13. Reload Your Web App

Go to **Web** tab → Your Web App → Click **Reload** button

## Verification

1. Visit `https://yourusername.pythonanywhere.com`
2. You should see the Farm Connect landing page
3. Try registering a new account
4. Access admin at `/admin/`

## Troubleshooting

**Issue: 500 Error or ImportError**
- Check **Web** tab → **Error log** and **Server log**
- Ensure `.env` file exists and is readable
- Verify virtual environment path is set correctly

**Issue: Database Connection Error**
- Check MySQL database credentials in `.env`
- Ensure MySQL is enabled on PythonAnywhere
- Verify database name format: `yourusername$farmconnect`

**Issue: Static files not loading**
- Run `python manage.py collectstatic --noinput` again
- Verify static files URL mapping in **Web** tab
- Clear browser cache (Ctrl+F5)

**Issue: Email not sending**
- Verify email credentials in `.env`
- For Gmail: Use [App Password](https://support.google.com/accounts/answer/185833)
- Check that EMAIL_HOST and EMAIL_PORT are correct

**Issue: Image uploads not working**
- Verify `/media/` directory exists and is writable
- Check permissions: `chmod 755 /home/yourusername/mysite/media/`

## Security Checklist

- [ ] DEBUG = False in production
- [ ] SECRET_KEY is unique and not shared
- [ ] ALLOWED_HOSTS configured correctly
- [ ] HTTPS enabled (PythonAnywhere provides free SSL)
- [ ] Database password is strong
- [ ] Email credentials are secure
- [ ] `.env` file is in `.gitignore` and not committed

## Backup and Maintenance

### Daily/Weekly Backups

```bash
# Backup database
mysqldump -h yourusername.mysql.pythonanywhere-services.com -u yourusername -p yourusername$farmconnect > backup_$(date +%Y%m%d).sql
```

### Check Logs

- Error log: `/var/log/yourusername.pythonanywhere.com_error_log`
- Access log: `/var/log/yourusername.pythonanywhere.com_access_log`

## Support

For PythonAnywhere-specific issues, visit: https://www.pythonanywhere.com/help/
For Django issues, visit: https://docs.djangoproject.com/

