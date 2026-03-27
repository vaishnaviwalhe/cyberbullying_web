from flask import Flask, render_template, request, redirect, session
import sqlite3
from model import predict
import os
if not os.path.exists("model.pkl"):
    import model

app = Flask(__name__)
app.secret_key = "secret123"

def connect():
    conn = sqlite3.connect("database.db")
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        password TEXT,
        role TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS records(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        text TEXT,
        result TEXT
    )
    """)

    conn.commit()
    conn.close()

connect()

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = sqlite3.connect("database.db")
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE username=? AND password=?",
                    (username, password))
        user = cur.fetchone()
        conn.close()

        if user:
            session['user'] = username
            session['role'] = user[3]

            if user[3] == "admin":
                return redirect('/admin')
            else:
                return redirect('/dashboard')
        else:
            return "Invalid Login ❌"

    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']

        conn = sqlite3.connect("database.db")
        cur = conn.cursor()
        cur.execute("INSERT INTO users(username,password,role) VALUES(?,?,?)",
                    (username, password, role))
        conn.commit()
        conn.close()

        return redirect('/')

    return render_template('register.html')

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'user' not in session:
        return redirect('/')

    result = None

    if request.method == 'POST':
        text = request.form['text']
        result = predict(text)

        conn = sqlite3.connect("database.db")
        cur = conn.cursor()
        cur.execute("INSERT INTO records(username,text,result) VALUES(?,?,?)",
                    (session['user'], text, result))
        conn.commit()
        conn.close()

    return render_template('dashboard.html', result=result)

@app.route('/admin')
def admin():
    if 'role' not in session or session['role'] != 'admin':
        return redirect('/')

    conn = sqlite3.connect("database.db")
    cur = conn.cursor()
    cur.execute("SELECT * FROM records")
    records = cur.fetchall()
    conn.close()

    return render_template('admin.html', records=records)

@app.route('/delete/<int:id>')
def delete(id):
    conn = sqlite3.connect("database.db")
    cur = conn.cursor()
    cur.execute("DELETE FROM records WHERE id=?", (id,))
    conn.commit()
    conn.close()

    return redirect('/admin')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

if __name__ == '__main__':
    app.run(host="0.0.0.0",port=10000)