### (WIP) Survey System Using: ###
- virtualenv
- Python 2.7
- Flask
- [SQLAlchemy](www.sqlalchemy.org)
- Flask-wtf
- git
- AWS RDS, EB
- Local Environment: w/Ubuntu Subsystem on Windows 10 (SP4)

### Instructions ###

1. initialize virtual environment
`$ virtualenv venv`

1. activate virtual environment
`$ . venv/bin/activate`

  to deactivate: 
    `(venv) $ deactivate`

1. install pip dependencies:
`(venv) $ pip install -r requirements.txt`

1. set database url:
    ``` 
    export DATABASE_URL="postgres://username:pass@db_url_from.amazonaws.com:port/dbname"
    ```

1. Place (JSON) surveys `surveys/` folder

1. Visit `/collect/[survey_file]/start` to start survey

### TODO ###
- excel to JSON converter
