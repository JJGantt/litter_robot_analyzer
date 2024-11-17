DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS data;

CREATE TABLE users (
    id serial PRIMARY KEY UNIQUE, 
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL
);

CREATE TABLE data (
    id serial PRIMARY KEY,
    userid INTEGER NOT NULL,
    poopdate INTEGER NOT NULL, 
    weight FLOAT NOT NULL
);