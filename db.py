import os
from contextlib import contextmanager
import psycopg2
from urllib.parse import urlparse

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
@contextmanager
def db_cursor():
    """A cursor on a fresh connection, both closed on every exit path."""
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            yield conn, cur
    finally:
        conn.close()

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