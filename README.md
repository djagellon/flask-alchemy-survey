# A Flask Survey and Reporting System

## Technologies Used
- Python 2.7
- Flask
- [SQLAlchemy](www.sqlalchemy.org)
- [Flask-WTF](https://flask-wtf.readthedocs.io/en/stable/)


## Getting Started

### Prerequisites

A python environment such as [virtualenv](https://virtualenv.pypa.io/en/latest/installation/)

### config.py

The following variables need to be present in your configuration file

```
    # Read from environment variable or hardcoded here
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-need-a-key-here'
    SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']

    # Flask-User settings
    USER_APP_NAME = "My Application"        # Shown in and email templates and page footers
    USER_ENABLE_EMAIL = True                # Disable email authentication
    USER_ENABLE_CONFIRM_EMAIL = False
    USER_ALLOW_LOGIN_WITHOUT_CONFIRMED_EMAIL = True
    USER_ENABLE_USERNAME = True             # Enable username authentication
    USER_REQUIRE_RETYPE_PASSWORD = False    # Simplify register form
    USER_EMAIL_SENDER_EMAIL = 'some@email.com'

    MAIL_SERVER = 'some.mailserver'
    MAIL_PORT = 465
    INCOMING_MAIL_PORT = 587
    MAIL_USE_SSL = True
    MAIL_USE_TLS = False
    MAIL_USERNAME = 'username'
    MAIL_PASSWORD = 'password'
    ADMINS = 'some@email.com'
```

### Installation
1. initialize virtual environment
`$ virtualenv venv`

1. activate virtual environment
`$ . venv/bin/activate`

1. install pip dependencies:
`(venv) $ pip install -r requirements.txt`

1. Place (JSON) surveys `surveys/` folder

1. Visit `/collect/[survey_file]/start` to start survey

## Surveys
Any (survey_name.json) file within the `/surveys` directory will be accessible by visiting `/collect/[survey_name]/start`.

### Formatting

Questions are shown in the order they are placed in the root-level list.

The `survey_name.json` must be formatted in the following manner:

```
[
    [
        {
            "label": "question1",
            "title": "This is question one. Show question two?"
            "condition": "all",
            "type": "radio"
            "answers": [
                {"label": "q1.yes", "text": "yes"},
                {"label": "q1.no", "text": "no"},
            ]
        }
    ],
    [
        {
            "label": "question2",
            "title": "This is question two. A multiple choice question."
            "condition": "q1.yes",
            "type": "multi"
            "answers": [
                {"label": "q2.apples", "text": "Apples"},
                {"label": "q2.oranges", "text": "Oranges"},
                {"label": "q2.bananas", "text": "Bananas"},
                {"label": "q2.grapes", "text": "Grapes"},
            ]
        }
    ]
]
```

### Survey Attributes

#### Questions
```
label: The label of the question

title: The text shown to the survey taker

condition: The answer label that must exist in the database in order for the question to be displayed. 
ie. The survey taker must select this answer from a previous question to see this question.

type: The question type. This can be one of:
    radio: Single select option
    multi: Multiple choice checkboxes
    select: Drop-down selection
    integer: Single row box with input validation
    string: Single row text box
    textarea: Multi-row text box

answers: List of possible answers to the question. Answers have the following attributes
```

#### Answers
```
label: Label of the answer. Must be in dot format: `questionlabel.answerlabel`. 
Optional, if '.other', is present as part of the label, a single row text box is added that accepts a string value.

text: The text shown to the survey taker

other: Text shown next to string input field. Must include `.other` as part of the answer label
```

## Reporting

You can view answers to the survey by going to: `/report/[survey_name]`

## Dashboard

The initial page displays all surveys available. From here, users have the option to start surveys or view their reports.

