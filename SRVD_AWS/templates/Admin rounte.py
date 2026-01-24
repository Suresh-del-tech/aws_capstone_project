from flask import Flask, render_template, request, redirect, url_for, session
from db import get_db

app = Flask(__name__)
app.secret_key = "admin_secret_key"

# --- ADMIN LOGIN ---
@app.route('/admin', methods=['GET','POST'])
@app.route('/admin/login', methods=['GET','POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        admin_dashboard = db.execute(
            "SELECT * FROM admin WHERE username=? AND password=?",
            (username, password)
        ).fetchone()

        if admin_dashboard:
            session['admin'] = admin_dashboard['username']
            return redirect(url_for('admin_dashboard'))

    return render_template('admin_login.html')


# --- ADMIN DASHBOARD ---
@app.route('/admin/dashboard')
def admin_dashboard():
    if 'admin' not in session:
        return redirect(url_for('admin_login'))
    return render_template('admin_dashboard.html', admin=session['admin'])


# --- ADD TRAIN ---
@app.route('/admin/add-train', methods=['GET','POST'])
def add_train():
    if 'admin' not in session:
        return redirect(url_for('admin_login'))

    if request.method == 'POST':
        name = request.form['name']
        source = request.form['source']
        destination = request.form['destination']
        time = request.form['time']

        db = get_db()
        db.execute(
            "INSERT INTO trains (name, source, destination, time) VALUES (?,?,?,?)",
            (name, source, destination, time)
        )
        db.commit()
        return redirect(url_for('view_trains'))

    return render_template('add_train.html')


# --- VIEW TRAINS ---
@app.route('/admin/trains')
def view_trains():
    if 'admin' not in session:
        return redirect(url_for('admin_login'))

    db = get_db()
    trains = db.execute("SELECT * FROM trains").fetchall()
    return render_template('admin_trains.html', trains=trains)


# --- VIEW BOOKINGS ---
@app.route('/admin/bookings')
def view_bookings():
    if 'admin' not in session:
        return redirect(url_for('admin_login'))

    db = get_db()
    bookings = db.execute("SELECT * FROM bookings").fetchall()
    return render_template('admin_bookings.html', bookings=bookings)


# --- ADMIN LOGOUT ---
@app.route('/admin/logout')
def admin_logout():
    session.pop('admin', None)
    return redirect(url_for('admin_login'))


if __name__ == "__main__":
    app.run(debug=True)
