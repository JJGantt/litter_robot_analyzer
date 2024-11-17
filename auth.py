import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

from db import get_db, get_db_connection

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = get_db_connection()
        cur = conn.cursor()
        error = None

        if not username:
            error = 'Usernmae is required.'
        elif not password:
            error = 'Password is required.'

        if error is None:
            try:
                cur.execute(
                    'INSERT INTO users (username, password) VALUES (%s, %s)',
                    (username, generate_password_hash(password))
                    )
                conn.commit()
            except conn.IntegrityError:
                error = f"User {username} is already registered."
            else:
                cur.execute(
                    'SELECT * FROM users WHERE username = %s', (username,)
                )
                user = cur.fetchone()
                session.clear()
                session['user_id'] = user[0]
                return redirect(url_for('index'))
        cur.close()
        conn.close()
        
        flash(error)

    return render_template('auth/register.html')

@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = get_db_connection()
        cur = conn.cursor()
        error = None

        cur.execute(
            'SELECT * FROM users WHERE username = %s', (username,)
        )
        user = cur.fetchone()

        if user is None:
            error = 'Incorrect username.'
        elif not check_password_hash(user[2], password):
            error = 'Incorrect password.'

        if error is None:
            session.clear()
            session['user_id'] = user[0]
            return redirect(url_for('index'))
        
        flash(error)

        cur.close()
        conn.close()

    return render_template('auth/login.html')

@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            'SELECT * FROM users WHERE id = %s', (user_id,)
        )
        user = cur.fetchone()
        if user:
            g.user = {'user_id': user[0], 'username': user[1]}

@bp.route('/logout')
def logout():
    session.clear()
    if hasattr(g, 'user'):
        del g.user
    return redirect(url_for('index'))

def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view