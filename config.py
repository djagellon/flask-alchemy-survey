import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-need-a-key-here'

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

    MAIL_SERVER = 'mail.verastrategic.com'
    MAIL_PORT = 465
    MAIL_USE_SSL = True
    MAIL_USE_TLS = False
    MAIL_USERNAME = os.environ['OUTGOING_EMAIL']
    MAIL_PASSWORD = os.environ['OUTGOING_PASS']

    ADMINS = [
        '"Vera Admin" <dj@verastrategic.com>',
    ]
