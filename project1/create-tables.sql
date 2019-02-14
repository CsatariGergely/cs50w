CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    name VARCHAR NOT NULL,
    password VARCHAR NOT NULL
);

CREATE TABLE books (
    id SERIAL PRIMARY KEY,
    isbn VARCHAR NOT NULL,
    author VARCHAR NOT NULL,
    title VARCHAR NOT NULL,
    publication_year INTEGER
);

CREATE TABLE reviews (
    id SERIAL PRIMARY KEY,
    book_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    rate INTEGER,
    review_text VARCHAR
);


CREATE USER books WITH PASSWORD 'books';
CREATE DATABASE books;
GRANT ALL PRIVILEGES ON DATABASE "books" TO books;