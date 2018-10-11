from app import create_app, db
from app.models import User, SurveyModel, QuestionModel, Role, UserRoles, ActionModel, \
Preferences, UserPreferences


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
            'Preferences': Preferences,
            'UserPreferences': UserPreferences,
            'SurveyModel': SurveyModel, 
            'QuestionModel': QuestionModel,
            'ActionModel': ActionModel}
