#!/bin/bash

# Farm Connect - Quick Deployment Checklist for PythonAnywhere

echo "Farm Connect - Deployment Readiness Check"
echo "=========================================="
echo ""

# Check Python version
echo "✓ Python version:"
python3 --version
echo ""

# Check Django installation
echo "✓ Django version:"
python3 -c "import django; print(f'Django {django.get_version()}')"
echo ""

# Check requirements.txt
echo "✓ Checking requirements.txt..."
if [ -f "requirements.txt" ]; then
    echo "  requirements.txt found"
    echo "  Contents:"
    cat requirements.txt
else
    echo "  ❌ requirements.txt NOT found"
fi
echo ""

# Check .env.example
echo "✓ Checking .env.example..."
if [ -f ".env.example" ]; then
    echo "  .env.example found"
else
    echo "  ❌ .env.example NOT found (create manually)"
fi
echo ""

# Run Django checks
echo "✓ Running Django system checks..."
python3 manage.py check
echo ""

# Check database connectivity (will fail if not configured, but that's OK)
echo "✓ Checking database configuration..."
python3 manage.py dbshell --help > /dev/null 2>&1 && echo "  Database configured" || echo "  Database not yet configured (expected)"
echo ""

# Check static files
echo "✓ Checking static files..."
if [ -d "frontend/static" ]; then
    echo "  Static files directory found"
    echo "  Contents:"
    ls -la frontend/static/
else
    echo "  ❌ Static files directory NOT found"
fi
echo ""

# Check media directory
echo "✓ Checking media directory..."
if [ -d "media" ]; then
    echo "  Media directory exists"
else
    echo "  Creating media directory..."
    mkdir -p media
fi
echo ""

# Check templates
echo "✓ Checking templates..."
if [ -d "frontend/templates" ]; then
    echo "  Templates directory found"
    echo "  Number of templates: $(find frontend/templates -name '*.html' | wc -l)"
else
    echo "  ❌ Templates directory NOT found"
fi
echo ""

echo "=========================================="
echo "Pre-Deployment Checklist Complete!"
echo ""
echo "Next Steps:"
echo "1. Copy .env.example to .env and update with your PythonAnywhere credentials"
echo "2. Read DEPLOYMENT_PYTHONANYWHERE.md for detailed instructions"
echo "3. Run: python manage.py collectstatic --noinput"
echo "4. Upload to PythonAnywhere and configure WSGI"
echo ""
