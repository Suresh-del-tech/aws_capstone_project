from flask import Flask, render_template, request, redirect, session
import sqlite3

def get_db():
    conn = sqlite3.connect("train.db")
    conn.row_factory = sqlite3.Row
    return conn


app = Flask(__name__)
app.secret_key = "train_secret"

@app.route("/")
def home():
    return redirect("/login")

@app.route("/signup", methods=["GET","POST"])
def signup():
    if request.method == "POST":
        return redirect("/login")
    return render_template("signup.html")

@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        session["user"] = request.form["email"]
        return redirect("/search")
    return render_template("login.html")

@app.route("/search", methods=["GET","POST"])
def search():
    trains = []
    if request.method == "POST":
        trains = [
            (1,"Express 101","Chennai","Bangalore","10:00 AM"),
            (2,"Superfast 202","Delhi","Mumbai","6:00 PM")
        ]
    return render_template("search.html", trains=trains)

@app.route("/booking/<int:train_id>")
def booking(train_id):
    return render_template("booking.html", train_id=train_id)

@app.route("/payment", methods=["POST"])
def payment():
    return render_template("payment.html",
        train_id=request.form["train_id"],
        name=request.form["name"],
        age=request.form["age"]
    )

@app.route("/ticket", methods=["POST"])
def ticket():
    return render_template("ticket.html",
        name=request.form["name"],
        age=request.form["age"],
        train_id=request.form["train_id"]
    )

@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect("/login")
    return render_template("dashboard.html", user=session["user"])

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

if __name__ == "__main__":
    app.run(debug=True)
