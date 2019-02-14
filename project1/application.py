import os
import requests
import json

from flask import Flask, render_template, request, session, abort
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

app = Flask(__name__)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

@app.route("/")
def index():
    if not 'linusername' in session:
        session['linusername'] = ""
    return render_template("index.html", linusername=session['linusername'])

@app.route("/search", methods=["POST"])
def search():
    search = request.form.get("search")
    #TODO: search for partial matches also
    books = db.execute("SELECT * FROM books WHERE UPPER(isbn) SIMILAR TO UPPER(:search) OR UPPER(author) SIMILAR TO UPPER(:search) OR UPPER(title) SIMILAR TO UPPER(:search)", {"search": "%" + search + "%"}).fetchall()
    return render_template("search-results.html", books=books)

@app.route("/book/<int:book_id>")
def book(book_id):
    book = db.execute("SELECT * FROM books WHERE id = :book_id", {"book_id": book_id}).fetchone()
    if book is None:
        return render_template("error.html", message="No such book.")

    reviews = db.execute("SELECT * FROM reviews WHERE book_id = :book_id", {"book_id": book_id}).fetchall()
    
    print("Asking goodreads")
    res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "QUPYwLJPKFaRBjuGasaMw", "isbns": book.isbn})
    grAveragerating = ""
    grReviewsCount = ""
    if 200 == res.status_code:
        response = json.loads(res.text)
        grAveragerating = response['books'][0]['average_rating']
        grReviewsCount = response['books'][0]['reviews_count']
    return render_template("book.html", book=book, reviews=reviews, linusername=session['linusername'], grAveragerating=grAveragerating, grReviewsCount=grReviewsCount)

@app.route("/api/<string:isbn>")
def isbn(isbn):
    book = db.execute("SELECT * FROM books WHERE isbn = :isbn", {"isbn": isbn}).fetchone()
    if book is None:
        abort(404)
    result = db.execute("SELECT COUNT(*) AS nrreviews FROM reviews WHERE book_id = :book_id", {"book_id": book.id}).fetchone()
    nrr = result["nrreviews"]
    result = db.execute("SELECT AVG(rate) AS arate FROM reviews WHERE book_id = :book_id", {"book_id": book.id}).fetchone()
    arate = result["arate"]
    return render_template("isbn.json", book=book, nrr=nrr, arate=round(arate,2))

@app.route("/review", methods=["POST"])
def review():
    rate = request.form.get("rate")
    review = request.form.get("review")
    book_id = request.form.get("id")
    user_id = session['linuserid']

    book = db.execute("SELECT * FROM books WHERE id = :id", {"id": book_id}).fetchone()
    if book is None:
        return render_template("error.html", message="Invalid book id.")
    if rate is None:
        return render_template("error.html", message="Rank is needed for review.")
    db.execute("INSERT INTO reviews (book_id, user_id, rate, review_text) VALUES (:book_id, :user_id, :rate, :review_text)",
            {"book_id": book_id, "user_id": user_id, "rate": rate, "review_text": review})
    db.commit()

    book = db.execute("SELECT * FROM books WHERE id = :book_id", {"book_id": book_id}).fetchone()
    #TODO: Do  the join magic and get the user names
    reviews = db.execute("SELECT rate, review_text, name FROM reviews JOIN users ON reviews.user_id = users.id WHERE book_id = :book_id", {"book_id": book_id}).fetchall()

    return render_template("book.html", book=book, reviews=reviews)


@app.route("/login", methods=["POST"])
def login():
    name = request.form.get("name")
    password = request.form.get("password")

    if name is None or name == "" or password is None or password == "":
        return render_template("login-error.html", message="Both username and password is needed.") 

    user = db.execute("SELECT * FROM users WHERE name = :name", {"name": name}).fetchone()
    if user is None:
        return render_template("login-error.html", message="User not found.")
    if user.password == password:
        session['linusername'] = user.name
        session['linuserid'] = user.id
        return render_template("index.html", linusername=session['linusername'])
    else:
        return render_template("login-error.html", message="Password error.")

@app.route("/register", methods=["POST"])
def register():
    name = request.form.get("name")
    password = request.form.get("password")

    if name is None or name == "" or password is None or password == "":
        return render_template("register-error.html", message="Both username and password is needed.") 

    user = db.execute("SELECT * FROM users WHERE name = :name", {"name": name}).fetchone()
    if user is not None:
        return render_template("login-error.html", message="User already exists.")
    db.execute("INSERT INTO users (name, password) VALUES (:name, :password)",
            {"name": name, "password": password})
    db.commit()
    return render_template("index.html")

@app.route("/logout", methods=["POST"])
def logout():
    session['linusername'] = None
    session['linuserid'] = None
    return render_template("index.html", linusername=session['linusername'])
    
