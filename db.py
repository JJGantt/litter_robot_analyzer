import sqlite3
import os
import psycopg2
from urllib.parse import urlparse

import click
from flask import current_app, g 

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'], 
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row

    return g.db

def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()

def init_db():
    db = get_db()

    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf8'))

@click.command('init-db')
def init_db_command():
    init_db()
    click.echo('Initialized the database.')

def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)

#dev connect
'''
def get_db_connection():
    conn = psycopg2.connect(
	host="localhost",
	database="flask_db",
	user=os.environ['DB_USERNAME'],
	password=os.environ['DB_PASSWORD'])

    return conn

'''
def get_db_connection():
    DATABASE_URL = os.environ.get('DATABASE_URL')

    url = urlparse(DATABASE_URL)

    conn = psycopg2.connect(
        dbname=url.path[1:], 
        user=url.username,
        password=url.password,
        host=url.hostname,
        port=url.port
    )
    
    return conn