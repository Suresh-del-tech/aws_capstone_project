import boto3
from flask import Flask, render_template, request, redirect, url_for, session
from db import get_db

app = Flask(__name__)
app.secret_key = "admin_secret_key"  # Change this in production

# Optional: create AWS client (example: S3)
# s3 = boto3.client('s3', region_name='ap-south-1')


# =======================
# ADMIN LOGIN
# =======================
@app.route('/admin', methods=['GET', 'POST'])
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        db = get_db()
        admin = db.execute(
            "SELECT * FROM admin WHERE username = ? AND password = ?",
            (username, password)
        ).fetchone()

        if admin:
            session['admin'] = admin['username']
            return redirect(url_for('admin_dashboard'))

        return render_template('admin_login.html', error="Invalid credentials")

    return render_template('admin_login.html')


# =======================
# ADMIN DASHBOARD
# =======================
@app.route('/admin/dashboard')
def admin_dashboard():
    if 'admin' not in session:
        return redirect(url_for('admin_login'))

    return render_template('admin_dashboard.html', admin=session['admin'])


# =======================
# ADD TRAIN
# =======================
@app.route('/admin/add-train', methods=['GET', 'POST'])
def add_train():
    if 'admin' not in session:
        return redirect(url_for('admin_login'))

    if request.method == 'POST':
        name = request.form.get('name')
        source = request.form.get('source')
        destination = request.form.get('destination')
        time = request.form.get('time')

        db = get_db()
        db.execute(
            "INSERT INTO trains (name, source, destination, time) VALUES (?, ?, ?, ?)",
            (name, source, destination, time)
        )
        db.commit()

        return redirect(url_for('view_trains'))

    return render_template('add_train.html')


# =======================
# VIEW TRAINS
# =======================
@app.route('/admin/trains')
def view_trains():
    if 'admin' not in session:
        return redirect(url_for('admin_login'))

    db = get_db()
    trains = db.execute("SELECT * FROM trains").fetchall()
    return render_template('admin_trains.html', trains=trains)


# =======================
# VIEW BOOKINGS
# =======================
@app.route('/admin/bookings')
def view_bookings():
    if 'admin' not in session:
        return redirect(url_for('admin_login'))

    db = get_db()
    bookings = db.execute("SELECT * FROM bookings").fetchall()
    return render_template('admin_bookings.html', bookings=bookings)


# =======================
# ADMIN LOGOUT
# =======================
@app.route('/admin/logout')
def admin_logout():
    session.pop('admin', None)
    return redirect(url_for('admin_login'))


if __name__ == "__main__":
    app.run(debug=True)
