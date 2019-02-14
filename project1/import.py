import csv
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

def main():
    f = open("books.csv")
    reader = csv.reader(f)
    for isbn, title, author, year in reader:
        if year == "year":
            continue
        print(isbn + ", " + title + ", " + author + ", " + year)
        db.execute("INSERT INTO books (isbn, author, title, publication_year) VALUES (:isbn, :author, :title, :publication_year)",
            {"isbn": isbn, "author": author, "title": title, "publication_year": year})
    db.commit()

if __name__ == "__main__":
    main()
