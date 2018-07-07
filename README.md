### Development Session Utilizing: ###
- virtualenv
- Python 2.7
- Flask
- [SQLAlchemy](www.sqlalchemy.org)
- git
- Amazon Elastic Beanstalk
- Environment: w/Ubuntu Subsystem on Windows 10 (SP4)

### Instructions ###

1. initialize virtual environment
`$ virtualenv venv`

1. activate virtual environment
`$ . venv/bin/activate`

to deactivate: 
`(venv) $ deactivate`

1. pip installations required:
* flask
* sqlalchemy 
* flask-sqlalchemy 
* Flask-WTF

likely dependencies:
* packaging 
* oauth2client 
* redis 
* passlib 
* flask-httpauth
* psycopg2-binary 
* bleach 
* requests

1.

### Resources ###
[Udacity - Full Stack Foundations](https://classroom.udacity.com/courses/ud088)
[AWS Deploying a Flask Application to EB](https://docs.aws.amazon.com/elasticbeanstalk/latest/dg/create-deploy-python-flask.html)
[AWS CodeDeploy with GitHub](https://docs.aws.amazon.com/codedeploy/latest/userguide/integrations-partners-github.html) 
