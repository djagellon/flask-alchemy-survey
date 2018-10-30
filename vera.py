from app import create_app, db
from app.models import User, SurveyModel, QuestionModel, Role, UserRoles, ActionModel, \
Preferences, UserPreferences
import re
from datetime import datetime
from jinja2 import evalcontextfilter, Markup, escape

app = create_app()

SAVED_DATE_FMT = '%a, %d %b %Y %H:%M:%S %Z'
DISPLAY_FMT = '%b %d, %Y %X'

_paragraph_re = re.compile(r'(?:\r\n|\r|\n){2,}')

@app.template_filter()
def has_open(value):
    return value.render_kw and value.render_kw.get('class') == 'other_option'

@app.template_filter()
@evalcontextfilter
def nl2br(eval_ctx, value):
    result = u'\n\n'.join(u'<p>%s</p>' % p.replace('\n', Markup('<br>\n')) 
        for p in _paragraph_re.split(escape(value)))

    if eval_ctx.autoescape:
        result = Markup(result)

    return result

@app.template_filter('strftime')
def _jinja2_filter_datetime(date, fmt=None):
    date = datetime.strptime(date, SAVED_DATE_FMT)
    native = date.replace(tzinfo=None)
    return native.strftime(DISPLAY_FMT) 

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

