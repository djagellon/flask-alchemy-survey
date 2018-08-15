from app import create_app

app = create_app()

def has_open(value):
    return value.render_kw and value.render_kw.get('class') == 'other_option'

app.jinja_env.filters['has_open'] = has_open

####MOVE ALL THIS BELOW
@app.route('/')
@app.route('/home')
def show_home():
    return render_template('home.html')
