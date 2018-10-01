import os
basedir = os.path.abspath(os.path.dirname(__file__))
# user_template_base = '/app/auth/templates/'

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-need-a-key-here'

    # SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
    #     'postgresql://' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Flask-User settings
    USER_APP_NAME = "Vera Strategic"      # Shown in and email templates and page footers
    USER_ENABLE_EMAIL = True      # Disable email authentication
    USER_ENABLE_CONFIRM_EMAIL = False
    USER_ALLOW_LOGIN_WITHOUT_CONFIRMED_EMAIL = True
    USER_ENABLE_USERNAME = True    # Enable username authentication
    USER_REQUIRE_RETYPE_PASSWORD = False    # Simplify register form
    USER_EMAIL_SENDER_EMAIL = 'register@verastrategic.com'

    # For smtp.gmail.com to work, you MUST set "Allow less secure apps" to ON in Google Accounts.
    # Change it in https://myaccount.google.com/security#connectedapps (near the bottom).
    MAIL_SERVER = 'mail.verastrategic.com'
    MAIL_PORT = 465
    MAIL_USE_SSL = True
    MAIL_USE_TLS = False
    MAIL_USERNAME = os.environ['OUTGOING_EMAIL']
    MAIL_PASSWORD = os.environ['OUTGOING_PASS']
    # USER_CHANGE_PASSWORD_TEMPLATE = user_template_base + 'change_password.html'
    # USER_CHANGE_USERNAME_TEMPLATE = user_template_base + 'change_username.html'
    # USER_EDIT_USER_PROFILE_TEMPLATE = user_template_base + 'edit_user_profile.html'
    # USER_FORGOT_PASSWORD_TEMPLATE = user_template_base + 'forgot_password.html'
    # USER_INVITE_USER_TEMPLATE = user_template_base + 'invite_user.html'
    # USER_LOGIN_TEMPLATE = user_template_base + 'login.html'
    # USER_LOGIN_AUTH0_TEMPLATE = user_template_base + 'login_auth0.html'
    # USER_MANAGE_EMAILS_TEMPLATE = user_template_base + 'manage_emails.html'
    # USER_REGISTER_TEMPLATE = user_template_base + 'register.html'
    # USER_RESEND_CONFIRM_EMAIL_TEMPLATE = user_template_base + 'resend_confirm_email.html'
    # USER_RESET_PASSWORD_TEMPLATE = user_template_base + 'reset_password.html'
    # Sendgrid settings
    # SENDGRID_API_KEY='place-your-sendgrid-api-key-here'

    ADMINS = [
        '"Vera Admin" <dj@verastrategic.com>',
    ]
