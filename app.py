import os

from flask import Flask

app = Flask(__name__, instance_relative_config=True)

# Signs the session cookie, so anyone holding it can log in as any user. It
# comes from the environment and the app refuses to start without it.
app.secret_key = os.environ.get('SECRET_KEY')
if not app.secret_key:
    raise RuntimeError('SECRET_KEY is not set')
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

@app.route('/hello')
def hello():
    return '123'

import auth
app.register_blueprint(auth.bp)

import profile_1
app.register_blueprint(profile_1.bp)
app.add_url_rule('/', endpoint='index')
    


'''
def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'poopr.sqlite'),
    )

    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.from_mapping(test_config)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    @app.route('/hello')
    def hello():
        return '123'
    
    from . import db
    db.init_app(app)

    from . import auth
    app.register_blueprint(auth.bp)

    from . import profile_1
    app.register_blueprint(profile_1.bp)
    app.add_url_rule('/', endpoint='index')
    
    return app
'''

