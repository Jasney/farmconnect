# 🚀 Farm Connect - Quick Start Guide for PythonAnywhere

**Project is production-ready with all security configurations in place.**

## Files Created for Deployment

- ✅ `requirements.txt` - All dependencies listed
- ✅ `manage.py` - Django management script
- ✅ `farm_connect_platform/wsgi.py` - WSGI application entry point
- ✅ `DEPLOYMENT_PYTHONANYWHERE.md` - **Detailed step-by-step guide**
- ✅ `DEPLOYMENT_CHECKLIST.md` - **Complete pre/post deployment checklist**
- ✅ `.env.example` - Template for environment variables
- ✅ `deploy_check.sh` - Automated readiness check script

## 30-Second Summary

1. **Create PythonAnywhere account** → https://www.pythonanywhere.com
2. **Follow** `DEPLOYMENT_PYTHONANYWHERE.md` (complete step-by-step guide)
3. **Use** `DEPLOYMENT_CHECKLIST.md` to verify each step
4. **Access** your deployed app at `yourusername.pythonanywhere.com`

## What's Included

### Security
- ✅ Environment-based configuration (no secrets in code)
- ✅ Django security middleware enabled
- ✅ CSRF protection
- ✅ XSS protection
- ✅ Security headers configured
- ✅ SSL/HTTPS ready (PythonAnywhere provides free SSL)

### Database
- ✅ MySQL support configured
- ✅ Connection pooling with proper charset
- ✅ Migration system ready
- ✅ Transaction support enabled

### Static Files & Media
- ✅ Static files collection script ready
- ✅ Media upload directory structure
- ✅ Proper URL routing for both static and media files

### Email
- ✅ Configurable email backend (Gmail, SendGrid, etc.)
- ✅ Development mode uses MailHog
- ✅ Production mode requires app/secure password

### Logging
- ✅ Error and warning logging configured
- ✅ Production log aggregation ready

## Critical Production Settings to Configure

When creating `.env` on PythonAnywhere, set these to True:

```env
DEBUG=False
SECURE_SSL_REDIRECT=True
SECURE_HSTS_SECONDS=31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
```

This will eliminate all deployment warnings shown in `manage.py check --deploy`.

## Quick Troubleshooting

| Issue | Solution |
|-------|----------|
| `ModuleNotFoundError` | Run `pip install -r requirements.txt` in virtual environment |
| `ConnectionRefused` (database) | Check DB credentials in `.env` match PythonAnywhere MySQL setup |
| Static files not loading | Run `python manage.py collectstatic --noinput` |
| Email not sending | Use [Gmail App Password](https://support.google.com/accounts/answer/185833) in `.env` |
| 500 errors | Check `/var/log/yourusername.pythonanywhere.com_error_log` |

## Next Steps

1. **Read** → `DEPLOYMENT_PYTHONANYWHERE.md` (full detailed guide)
2. **Check** → `DEPLOYMENT_CHECKLIST.md` (verify each step)
3. **Deploy** → Follow step-by-step on PythonAnywhere
4. **Test** → Run through all user workflows (Farmer, Buyer, Admin)

## Support

- **PythonAnywhere Help:** https://www.pythonanywhere.com/help/
- **Django Docs:** https://docs.djangoproject.com/en/6.0/
- **Project Repo:** [Your GitHub URL]

---
**Ready to Deploy!** 🎉

All application code, database models, views, templates, and security features are production-ready.
