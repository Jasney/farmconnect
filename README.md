# Farm Connect - Agricultural Marketplace

A Django web application that connects farmers and buyers in a sustainable agricultural marketplace with email verification, messaging, and market price tracking.

## 🚀 Quick Start

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Setup environment:**
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

3. **Setup database:**
   ```bash
   python manage.py migrate
   python manage.py createsuperuser
   ```

4. **Run development server:**
   ```bash
   python manage.py runserver
   ```

5. **Access at:** `http://127.0.0.1:8000`

## 📁 Project Structure

```
farm-connect/
├── 📄 README.md                    # This file
├── ⚙️  .env                        # Environment variables (create from .env.example)
├── ⚙️  .env.example               # Environment template
├── ⚙️  .env.production           # Production environment example
├── 🔒 .gitignore                  # Git ignore rules
├── 🐍 manage.py                   # Django management script
├── 📦 requirements.txt            # Python dependencies
├── 🏗️  farm_connect_platform/     # Main Django project
├── 👥 accounts/                   # User authentication & profiles
├── 🌾 crops/                      # Crop listings & marketplace
├── 🏪 market/                     # Market prices & analytics
├── 💬 messaging/                  # User messaging system
└── 🎨 frontend/                   # Templates & static files
```

## 🔐 Security Configuration

### Development (Default)
- DEBUG=True (shows detailed errors)
- Insecure cookies allowed
- No SSL enforcement

### Production Settings
For production deployment, configure these environment variables:

```bash
# In your .env file for production:
DEBUG=False
SECURE_SSL_REDIRECT=True
SECURE_HSTS_SECONDS=31536000
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
ALLOWED_HOSTS=yourdomain.com
```

See `.env.production` for a complete production configuration example.

## 📧 Email Configuration

### Development
Uses console backend - emails appear in terminal/Django console.

### Production
Configure SMTP settings in `.env`:
```bash
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
EMAIL_USE_TLS=True
```

## 🚀 Deployment

### PythonAnywhere (Recommended)
1. Upload project files (exclude `venv/`, `__pycache__/`)
2. Create virtual environment: `python3.11 -m venv venv`
3. Install dependencies: `pip install -r requirements.txt`
4. Configure database and email in `.env`
5. Run migrations: `python manage.py migrate`
6. Configure web app with WSGI file
7. Set environment variables in web app settings

### Other Platforms
- **Heroku**: Use `heroku config:set` for environment variables
- **DigitalOcean**: Configure environment in App Platform dashboard
- **AWS**: Use Elastic Beanstalk environment variables

## 🛠️ Features

- ✅ User registration with email verification
- ✅ Farmer & buyer dashboards
- ✅ Crop listings marketplace
- ✅ Market price tracking
- ✅ User messaging system
- ✅ Responsive Bootstrap UI
- ✅ MySQL/PostgreSQL support
- ✅ Production security settings

## 📞 Support

For issues or questions:
1. Check Django logs in deployment platform
2. Verify environment variables are set correctly
3. Ensure database is accessible
4. Check email configuration for SMTP issues

## 🚀 Quick Start

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Setup database:**
   ```bash
   python manage.py migrate
   python manage.py createsuperuser
   ```

3. **Run development server:**
   ```bash
   python manage.py runserver
   ```

4. **Access at:** `http://127.0.0.1:8000`

## 📦 Deployment

For production deployment, see the deployment guides in the `/docs/` folder or check:
- PythonAnywhere deployment guide
- Heroku deployment guide
- AWS/DigitalOcean guides

## 🗂️ File Organization for Deployment

### ✅ Keep for Production:
- `setup_instructions.md` - For future maintenance
- `TODO.md` - For ongoing development
- `DASHBOARD_DOCUMENTATION_INDEX.md` - For reference

### 🗑️ Can Remove for Production:
- `AUTHENTICATION_CHANGES.md` - Development history
- `CLEANUP_SUMMARY.md` - Completed tasks
- `DASHBOARD_DEPLOYMENT.md` - If deployment is documented elsewhere
- `DASHBOARD_ENHANCEMENTS.md` - Future plans
- `DASHBOARD_IMPLEMENTATION_COMPLETE.md` - Status update
- `DASHBOARD_VISUAL_GUIDE.md` - If UI is self-explanatory
- `UX_HCI_*` files - If UX work is complete

## 📞 Support

For questions about the codebase, check the documentation in `/docs/` first.