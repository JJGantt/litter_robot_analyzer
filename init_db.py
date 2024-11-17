import os 
import psycopg2
from urllib.parse import urlparse


#dev connection
'''
conn = psycopg2.connect(
	host="localhost",
	database="flask_db",
	user=os.environ['DB_USERNAME'],
	password=os.environ['DB_PASSWORD'])
'''

DATABASE_URL = os.environ.get('DATABASE_URL')
url = urlparse(DATABASE_URL)

conn = psycopg2.connect(
    dbname=url.path[1:],  
    user=url.username,
    password=url.password,
    host=url.hostname,
    port=url.port
)

cur = conn.cursor()

cur.execute('DROP TABLE IF EXISTS users;')
cur.execute('''CREATE TABLE users(
                id serial PRIMARY KEY UNIQUE, 
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL);'''
            )

print('something happening')
print(conn)

cur.execute('DROP TABLE IF EXISTS data;')
cur.execute('''CREATE TABLE data (
                id serial PRIMARY KEY,
                userid INTEGER NOT NULL,
                poopdate INTEGER NOT NULL, 
                weight FLOAT NOT NULL);'''
            )
'''
cur.execute('INSERT INTO users (username, password)'
            'VALUES (%s, %s)',
            ('testuser',
             'testpassword')
             )

cur.execute('INSERT INTO data (userid, poopdate, weight)'
            'VALUES ( %s, %s, %s)',
            (13,
             'testdate',
             'weight')
            )
'''

conn.commit()

cur.close()
conn.close()