import os

css_dir = r'c:\Users\IANTO\Desktop\Tzwifte\Project\frontend\static\css'

# Dashboard CSS
dashboard_css = """/* DASHBOARD STYLES */
.dashboard-header { background: linear-gradient(135deg, #0f4d2e 0%, #1a7a3e 100%); color: white; padding: 1.5rem; border-radius: 8px; margin-bottom: 2rem; }
.dashboard-header h1 { color: white; margin-bottom: 0.5rem; font-size: 1.75rem; }
.stat-card { text-align: center; padding: 1.5rem; border-radius: 8px; transition: all 0.3s ease; }
.stat-card:hover { box-shadow: 0 8px 16px rgba(0, 0, 0, 0.1); transform: translateY(-2px); }
.stat-card i { font-size: 2.5rem; color: #1a7a3e; margin-bottom: 1rem; }
.stat-card h3 { font-size: 2rem; font-weight: 700; color: #0f4d2e; margin-bottom: 0.5rem; }
.stat-card p { color: #7f8c8d; font-size: 0.9rem; }
@media (max-width: 768px) { .dashboard-header { padding: 1rem; margin-bottom: 1rem; } .stat-card { padding: 1rem; } }
"""

# Forms CSS
forms_css = """/* FORM STYLES */
.form-label { font-weight: 500; color: #2c3e50; margin-bottom: 0.5rem; display: block; }
.form-control, .form-select { border: 1px solid #dee2e6; border-radius: 4px; }
.form-control:focus, .form-select:focus { border-color: #1a7a3e; box-shadow: 0 0 0 0.2rem rgba(26, 122, 62, 0.25); outline: none; }
.btn { padding: 0.6rem 1.2rem; font-weight: 500; border-radius: 4px; transition: all 0.3s ease; }
@media (max-width: 768px) { .btn { padding: 0.5rem 1rem; font-size: 0.9rem; } }
"""

# Landing CSS
landing_css = """/* LANDING STYLES */
.hero-section { background: linear-gradient(135deg, #0f4d2e 0%, #1a7a3e 100%); color: white; padding: 60px 20px; text-align: center; }
.hero-section h1 { font-size: 2.5rem; font-weight: 700; margin-bottom: 1rem; }
.hero-section p { font-size: 1.2rem; margin-bottom: 2rem; opacity: 0.95; }
.info-card { text-align: center; padding: 2rem; border-radius: 8px; transition: all 0.3s ease; }
.info-card i { font-size: 3rem; color: #1a7a3e; margin-bottom: 1rem; }
.info-card:hover { transform: translateY(-5px); }
@media (max-width: 768px) { .hero-section { padding: 40px 20px; } .hero-section h1 { font-size: 1.75rem; } }
"""

# Login CSS
login_css = """/* LOGIN STYLES */
.login-container { display: flex; justify-content: center; align-items: center; min-height: calc(100vh - 70px); padding: 2rem 1rem; }
.login-card { width: 100%; max-width: 450px; padding: 2rem; border-radius: 8px; box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1); }
.login-header { text-align: center; margin-bottom: 2rem; }
.login-header i { font-size: 2.5rem; color: #1a7a3e; margin-bottom: 1rem; }
.login-header h2 { color: #2c3e50; margin-bottom: 0.5rem; }
@media (max-width: 600px) { .login-card { padding: 1.5rem; } .login-header h2 { font-size: 1.5rem; } }
"""

# Register CSS
register_css = """/* REGISTER STYLES */
.register-container { display: flex; justify-content: center; align-items: flex-start; min-height: calc(100vh - 70px); padding: 2rem 1rem; }
.register-card { width: 100%; max-width: 500px; padding: 2rem; border-radius: 8px; box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1); }
.role-selector { display: flex; gap: 1rem; margin-bottom: 1.5rem; flex-wrap: wrap; }
.role-option label { display: block; padding: 1rem; text-align: center; border: 2px solid #dee2e6; border-radius: 4px; cursor: pointer; transition: all 0.3s ease; }
@media (max-width: 600px) { .register-card { padding: 1.5rem; } .role-selector { flex-direction: column; } }
"""

# Messages CSS
messages_css = """/* MESSAGING STYLES */
.conversations-list { max-height: 600px; overflow-y: auto; }
.conversation-item { padding: 1rem; border-bottom: 1px solid #dee2e6; cursor: pointer; transition: background-color 0.3s ease; }
.conversation-item:hover { background-color: #f8f9fa; }
.conversation-avatar { width: 50px; height: 50px; border-radius: 50%; object-fit: cover; margin-right: 1rem; }
.message-bubble { max-width: 70%; padding: 0.75rem 1rem; border-radius: 8px; }
.message.sent .message-bubble { background-color: #1a7a3e; color: white; }
.message.received .message-bubble { background-color: #f0f0f0; color: #2c3e50; }
@media (max-width: 768px) { .conversations-list { max-height: 300px; } .message-bubble { max-width: 90%; } }
"""

# Theme CSS
theme_css = """/* THEME & COLORS */
:root { --primary-green: #0f4d2e; --secondary-green: #1a7a3e; --light-green: #f0f7f5; --text-dark: #2c3e50; }
.text-primary { color: var(--primary-green) !important; }
.text-secondary { color: var(--secondary-green) !important; }
.badge-success { background-color: var(--secondary-green); }
"""

# Utilities CSS
utilities_css = """/* UTILITIES */
.mt-0 { margin-top: 0 !important; } .mt-1 { margin-top: 0.25rem !important; } .mt-2 { margin-top: 0.5rem !important; }
.mb-0 { margin-bottom: 0 !important; } .mb-1 { margin-bottom: 0.25rem !important; } .mb-2 { margin-bottom: 0.5rem !important; }
.p-0 { padding: 0 !important; } .p-1 { padding: 0.25rem !important; } .p-2 { padding: 0.5rem !important; }
.rounded-0 { border-radius: 0 !important; } .rounded-1 { border-radius: 0.25rem !important; }
.shadow-none { box-shadow: none !important; } .shadow-sm { box-shadow: 0 0.125rem 0.25rem rgba(0, 0, 0, 0.075) !important; }
.cursor-pointer { cursor: pointer !important; } .text-truncate { white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
"""

files = {
    'dashboard.css': dashboard_css,
    'forms.css': forms_css,
    'landing.css': landing_css,
    'login.css': login_css,
    'register.css': register_css,
    'messages.css': messages_css,
    'theme.css': theme_css,
    'utilities.css': utilities_css,
}

for filename, content in files.items():
    filepath = os.path.join(css_dir, filename)
    with open(filepath, 'w') as f:
        f.write(content)
    print(f'{filename} written successfully')

print('\nAll CSS files cleaned and written!')
