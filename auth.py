import functools
import secrets

import psycopg2

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

from db import db_cursor

bp = Blueprint('auth', __name__, url_prefix='/auth')

_DUMMY_HASH = generate_password_hash(secrets.token_hex(16))

@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        error = None

        if not username:
            error = 'Usernmae is required.'
        elif not password:
            error = 'Password is required.'

        if error is None:
            with db_cursor() as (conn, cur):
                try:
                    cur.execute(
                        'INSERT INTO users (username, password) VALUES (%s, %s) RETURNING id',
                        (username, generate_password_hash(password))
                        )
                    user_id = cur.fetchone()[0]
                    conn.commit()
                except psycopg2.IntegrityError:
                    conn.rollback()
                    error = f"User {username} is already registered."
            if error is None:
                session.clear()
                session['user_id'] = user_id
                return redirect(url_for('index'))

        flash(error)

    return render_template('auth/register.html')

@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        with db_cursor() as (_, cur):
            cur.execute(
                'SELECT * FROM users WHERE username = %s', (username,)
            )
            user = cur.fetchone()

        # An unknown username is checked against a dummy hash so it costs the
        # same time as a wrong password, and both get the same message: the
        # form must not reveal which usernames exist.
        password_hash = user[2] if user else _DUMMY_HASH
        if check_password_hash(password_hash, password) and user:
            session.clear()
            session['user_id'] = user[0]
            return redirect(url_for('index'))

        flash('Incorrect username or password.')

    return render_template('auth/login.html')

@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    g.user = None
    if user_id is not None:
        with db_cursor() as (_, cur):
            cur.execute(
                'SELECT * FROM users WHERE id = %s', (user_id,)
            )
            user = cur.fetchone()
        if user:
            g.user = {'user_id': user[0], 'username': user[1]}

@bp.route('/logout')
def logout():
    session.clear()
    g.user = None
    return redirect(url_for('index'))

def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view