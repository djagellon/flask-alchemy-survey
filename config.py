import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-need-a-key-here'

    SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Flask-User settings
    USER_APP_NAME = "Flask Survey"      # Shown in and email templates and page footers
    USER_ENABLE_EMAIL = True      # Disable email authentication
    USER_ENABLE_CONFIRM_EMAIL = False
    USER_ALLOW_LOGIN_WITHOUT_CONFIRMED_EMAIL = True
    USER_ENABLE_USERNAME = True    # Enable username authentication
    USER_REQUIRE_RETYPE_PASSWORD = False    # Simplify register form
    USER_EMAIL_SENDER_EMAIL = os.environ['OUTGOING_EMAIL']

    MAIL_SERVER = os.environ['MAIL_SERVER']
    MAIL_PORT = 465
    INCOMING_MAIL_PORT = 587
    MAIL_USE_SSL = True
    MAIL_USE_TLS = False
    MAIL_USERNAME = os.environ['OUTGOING_EMAIL']
    MAIL_PASSWORD = os.environ['OUTGOING_PASS']
    ADMINS = os.environ['ADMIN_EMAILS']
