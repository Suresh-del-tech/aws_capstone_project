from flask import Flask, render_template, request, redirect, url_for, session
import boto3
import uuid
from botocore.exceptions import ClientError

app = Flask(__name__)
app.secret_key = "train_secret_key"

# AWS Config
REGION = "us-east-1"
dynamodb = boto3.resource("dynamodb", region_name=REGION)
sns = boto3.client("sns", region_name=REGION)

# Tables
users_table = dynamodb.Table("Users")
trains_table = dynamodb.Table("Trains")
bookings_table = dynamodb.Table("Bookings")

SNS_TOPIC_ARN = "arn:aws:sns:us-east-1:604665149129:aws_train_topic"

def send_notification(subject, message):
    try:
        sns.publish(TopicArn=SNS_TOPIC_ARN, Subject=subject, Message=message)
    except ClientError as e:
        print("SNS Error:", e)

# ---------------- USER ---------------- #

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/signup", methods=["GET","POST"])
def signup():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if "Item" in users_table.get_item(Key={"username": username}):
            return "User already exists!"

        users_table.put_item(Item={"username": username, "password": password})
        send_notification("New Signup", f"{username} registered.")
        return redirect(url_for("login"))

    return render_template("signup.html")

@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        res = users_table.get_item(Key={"username": username})
        if "Item" in res and res["Item"]["password"] == password:
            session["username"] = username
            send_notification("User Login", f"{username} logged in.")
            return redirect(url_for("search_trains"))

        return "Invalid Login!"

    return render_template("login.html")

@app.route("/search", methods=["GET","POST"])
def search_trains():
    if "username" not in session:
        return redirect(url_for("login"))

    trains = []
    if request.method == "POST":
        source = request.form["source"]
        destination = request.form["destination"]

        res = trains_table.scan()
        trains = [t for t in res["Items"] if t["source"] == source and t["destination"] == destination]

    return render_template("search.html", trains=trains)

@app.route("/book/<train_id>")
def book_train(train_id):
    if "username" not in session:
        return redirect(url_for("login"))

    booking_id = str(uuid.uuid4())
    bookings_table.put_item(Item={
        "booking_id": booking_id,
        "username": session["username"],
        "train_id": train_id
    })

    send_notification("Train Booking", f"{session['username']} booked train {train_id}")
    return redirect(url_for("my_bookings"))

@app.route("/my-bookings")
def my_bookings():
    if "username" not in session:
        return redirect(url_for("login"))

    res = bookings_table.scan()
    my = [b for b in res["Items"] if b["username"] == session["username"]]
    return render_template("my_bookings.html", bookings=my)

@app.route("/logout")
def logout():
    session.pop("username", None)
    return redirect(url_for("index"))

# ---------------- ADMIN ---------------- #

@app.route("/admin/login", methods=["GET","POST"])
def admin_login():
    if request.method == "POST":
        if request.form["username"] == "admin" and request.form["password"] == "admin123":
            session["admin"] = "admin"
            return redirect(url_for("admin_dashboard"))
        return "Invalid Admin!"
    return render_template("admin_login.html")

@app.route("/admin/dashboard")
def admin_dashboard():
    if "admin" not in session:
        return redirect(url_for("admin_login"))

    trains = trains_table.scan().get("Items", [])
    return render_template("admin_dashboard.html", trains=trains)

@app.route("/admin/add-train", methods=["GET","POST"])
def add_train():
    if "admin" not in session:
        return redirect(url_for("admin_login"))

    if request.method == "POST":
        train_id = str(uuid.uuid4())
        train = {
            "train_id": train_id,
            "name": request.form["name"],
            "source": request.form["source"],
            "destination": request.form["destination"],
            "time": request.form["time"],
            "price": request.form["price"]
        }
        trains_table.put_item(Item=train)
        return redirect(url_for("admin_dashboard"))

    return render_template("add_train.html")

@app.route("/admin/logout")
def admin_logout():
    session.pop("admin", None)
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True)
