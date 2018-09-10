from app import create_app, db
from app.models import User, Role, UserRoles, SurveyModel, QuestionModel


app = create_app()

def has_open(value):
    return value.render_kw and value.render_kw.get('class') == 'other_option'

app.jinja_env.filters['has_open'] = has_open

@app.shell_context_processor
def make_shell_context():
    return {'db': db,
            'User': User, 
            'Role': Role,
            'UserRoles': UserRoles,
            'SurveyModel': SurveyModel, 
            'QuestionModel': QuestionModel}
