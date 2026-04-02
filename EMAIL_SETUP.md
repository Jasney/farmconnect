# Email Configuration Guide

## Development Setup (MailHog)

MailHog is a simple test mail server for local development. All emails sent by your application will be captured and viewable in a web UI.

### 1. Download MailHog

- Go to: https://github.com/mailhog/MailHog/releases
- Download `MailHog_windows_amd64.exe` (latest version)
- Save it to a convenient location (e.g., `C:\Tools\MailHog\` or your project folder)

### 2. Run MailHog

Open PowerShell and run:

```powershell
# Navigate to where you saved MailHog
cd C:\path\to\MailHog

# Run it
.\MailHog_windows_amd64.exe
```

You should see:
```
[APIv1] SMTP server listening on [::]:1025
[APIv2] Web UI available at http://127.0.0.1:8025
```

**Keep this terminal running while developing.**

### 3. View Emails

Open your browser to: **http://127.0.0.1:8025**

Every email sent by your application will appear here in real-time. You can view the full email content, headers, and raw message.

### 4. Verify It Works

1. Start your Django server: `python manage.py runserver`
2. Register a new account at http://127.0.0.1:8000/accounts/register/
3. Check MailHog at http://127.0.0.1:8025 for the verification email
4. Copy the verification code and complete registration

---

## Production Setup

For production deployment, you need a real email service. Choose one of the following:

### Option 1: Gmail (Recommended for small projects)

**Setup Steps:**

1. **Enable 2-Factor Authentication**
   - Go to: https://myaccount.google.com/security
   - Scroll to "2-Step Verification" and enable it

2. **Create App Password**
   - Go to: https://myaccount.google.com/apppasswords
   - Select "Mail" and "Windows Computer"
   - Copy the 16-character password

3. **Update .env file**
   ```
   DEBUG=False
   EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
   EMAIL_HOST=smtp.gmail.com
   EMAIL_PORT=587
   EMAIL_HOST_USER=your-email@gmail.com
   EMAIL_HOST_PASSWORD=xxxx-xxxx-xxxx-xxxx  # 16-char app password
   EMAIL_USE_TLS=True
   EMAIL_USE_SSL=False
   DEFAULT_FROM_EMAIL=your-email@gmail.com
   ```

**Cost:** Free (up to 500 emails/day)

**Limitations:** 
- Limited daily email quota
- Not recommended for high-volume applications

---

### Option 2: SendGrid (Best for production)

**Setup Steps:**

1. **Sign up for SendGrid**
   - Go to: https://app.sendgrid.com/signup
   - Create a free account (100 emails/day) or paid plan

2. **Create API Key**
   - Login to SendGrid
   - Go to Settings > API Keys
   - Create new API Key > Full Access
   - Copy the key (starts with `SG.`)

3. **Verify Sender Email**
   - Go to Sender Authentication
   - Verify your domain or single sender email address
   - Follow the verification steps

4. **Update .env file**
   ```
   DEBUG=False
   EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
   EMAIL_HOST=smtp.sendgrid.net
   EMAIL_PORT=587
   EMAIL_HOST_USER=apikey
   EMAIL_HOST_PASSWORD=SG.your-full-api-key-here
   EMAIL_USE_TLS=True
   EMAIL_USE_SSL=False
   DEFAULT_FROM_EMAIL=verified-email@yourdomain.com
   ```

**Cost:** 
- Free plan: 100 emails/day
- Paid plans: $19.95+/month for unlimited emails

**Benefits:**
- Excellent deliverability
- Detailed analytics and logs
- Professional support

---

### Option 3: AWS SES (For high-volume applications)

**Setup Steps:**

1. **Create AWS Account**
   - Go to: https://aws.amazon.com/ses/
   - Create an account if you don't have one

2. **Verify Email Address**
   - In AWS SES console
   - Go to "Verified identities"
   - Click "Create identity"
   - Select "Email address" and enter your email
   - Confirm the verification link sent to your email

3. **Create SMTP Credentials**
   - Go to "Account dashboard"
   - Click "Create SMTP credentials"
   - Download credentials (contains username and password)

4. **Find Your SMTP Endpoint**
   - In SES console, note your region (e.g., `us-east-1`)
   - SMTP endpoint will be: `email-smtp.us-east-1.amazonaws.com`

5. **Update .env file**
   ```
   DEBUG=False
   EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
   EMAIL_HOST=email-smtp.us-east-1.amazonaws.com  # Change region if needed
   EMAIL_PORT=587
   EMAIL_HOST_USER=AKIAIOSFODNN7EXAMPLE  # From credentials file
   EMAIL_HOST_PASSWORD=your-password-here  # From credentials file
   EMAIL_USE_TLS=True
   EMAIL_USE_SSL=False
   DEFAULT_FROM_EMAIL=your-email@yourdomain.com
   ```

**Cost:** 
- $0.10 per 1,000 emails
- Very affordable for production

**Benefits:**
- Highly scalable
- Pay-as-you-go pricing
- Excellent deliverability

---

## Troubleshooting

### Emails not sending in development?

1. **Check MailHog is running**
   - Browser: http://127.0.0.1:8025
   - Terminal should show: `SMTP server listening on [::]:1025`

2. **Check DEBUG = True**
   - In your `.env` file or settings

3. **Check EMAIL_PORT is 1025**
   - In your `.env` file

4. **Restart Django server**
   - Stop `python manage.py runserver` and restart it

### Emails not sending in production?

1. **Check email credentials**
   - Copy-paste the password/API key again
   - Verify there are no extra spaces

2. **Check firewall/security groups**
   - Ensure port 587 is accessible
   - Some hosting providers block outbound SMTP

3. **Check sender email is verified**
   - Most services require sender email to be verified first

4. **Check Django DEBUG = False**
   - In production, DEBUG should be False

5. **Enable less secure apps** (Gmail only)
   - If using Gmail, enable "Less secure app access"
   - Go to: https://myaccount.google.com/lesssecureapps

---

## Switching Between Development and Production

Your code automatically switches based on the `DEBUG` setting:

- **DEBUG = True** → Uses MailHog (development)
- **DEBUG = False** → Uses production email service from .env

No code changes needed—just update your `.env` file and restart Django!

