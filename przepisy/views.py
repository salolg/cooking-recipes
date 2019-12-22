from flask import Flask, request, session, redirect, url_for, render_template, flash
from models import User, todays_recent_posts, searching_for_posts

app = Flask(__name__)


@app.route("/")
def index():
    posts = todays_recent_posts(5)
    print(posts)
    return render_template("index.html", posts=posts)


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        user = User(username)

        if not user.register(password):
            flash('Juz istnieje osoba z taka nazwa uzytkownika')
        else:
            flash('Zostales pomyslnie zarejestrowany.')
            return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        user = User(username)

        if not user.verify_password(password):
            flash("Niepoprawne dane logowania")
        else:
            flash("Zostales pomyslnie zalogowany")
            session["username"] = user.username
            return redirect(url_for("index"))

    return render_template("login.html")


@app.route("/add_post", methods=["POST"])
def add_post():
    title = request.form["title"]
    tags = request.form["tags"]
    text = request.form["text"]

    user = User(session["username"])

    if not title or not tags or not text:
        flash("You must give your post a title, tags, and a text body.")
    else:
        user.add_post(title, tags, text)

    return redirect(url_for("index"))



@app.route("/profile/<username>")
def profile(username):
    user1 = User(session.get("username"))
    user2 = User(username)
    posts = user2.recent_posts()


    return render_template("profile.html", username=username, posts=posts)

@app.route("/search_for_recipe")
def search_box():
    return render_template("searching.html")

@app.route("/search", methods=["POST"])
def searching():
    tag = request.form["tag"]
    posts = searching_for_posts(tag)
    print(posts)
    return render_template("searching.html", posts=posts)


@app.route("/logout")
def logout():
    session.pop("username")
    flash("Zostales wylogowny")
    return redirect(url_for("index"))