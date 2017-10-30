from flask import Flask, render_template, url_for, redirect, session, request
from flask_sqlalchemy import SQLAlchemy
import json

app = Flask(__name__)
app.secret_key = b"Q\xc0Z?\x9ar'\xe1\xe4$\x99S\xa1\xbfA\x91i\xd60C\x19\x9d\xed|"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///db/development.db"
db = SQLAlchemy(app)

# User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True)
    active = db.Column(db.Boolean)
    location = db.Column(db.String)

    def __repr__(self):
        return "<User: %r>" % self.username

    def as_json(self):
        dct = {"id": self.id, "username": self.username, "active": self.active, "location": self.location}
        return json.dumps(dct)

# Frontend calls
@app.route("/", methods=["GET"])
def index():
    if session.get("logged_in"):
        return render_template("index.html")
    else:
        return redirect(url_for("login"))

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        session["logged_in"] = False
        return render_template("login.html")
    else:
        session["logged_in"] = True
        return redirect(url_for("index"))

# Backend calls
@app.route("/api/", methods=["GET"])
def api_index():
    if session.get("logged_in"):
        users = [u.as_json() for u in User.query.all()]
        response = {"type": "userlist", "users": users}
    else:
        response = {"type": "error", "message": "You must be logged in to access user data"}
    return json.dumps(response)
