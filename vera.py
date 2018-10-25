from app import create_app, db
from app.models import User, SurveyModel, QuestionModel, Role, UserRoles, ActionModel, \
Preferences, UserPreferences
import re
from jinja2 import evalcontextfilter, Markup, escape

app = create_app()

_paragraph_re = re.compile(r'(?:\r\n|\r|\n){2,}')

@app.template_filter()
@evalcontextfilter
def nl2br(eval_ctx, value):
    result = u'\n\n'.join(u'<p>%s</p>' % p.replace('\n', Markup('<br>\n')) 
        for p in _paragraph_re.split(escape(value)))

    if eval_ctx.autoescape:
        result = Markup(result)

    return result

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

