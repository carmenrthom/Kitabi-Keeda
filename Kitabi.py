from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
import os

app = Flask("kitabi-keeda")
app.secret_key = os.urandom(24)

DATABASE = 'database.db'

def create_connection():
    return sqlite3.connect(DATABASE)

def create_table():
    conn = create_connection()
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
                 id INTEGER PRIMARY KEY AUTOINCREMENT,
                 email TEXT UNIQUE NOT NULL,
                 password TEXT NOT NULL)''')
    conn.commit()
    conn.close()

def card_create_table():
    conn = create_connection()
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS cards (
                 id INTEGER PRIMARY KEY AUTOINCREMENT,
                 text TEXT UNIQUE NOT NULL,
                 diff INTEGER NOT NULL,
                 auth TEXT NOT NULL)''')
    conn.commit()
    conn.close()


def register_user(email, password):
    conn = create_connection()
    c = conn.cursor()
    c.execute("INSERT INTO users (email, password) VALUES (?, ?)", (email, password))
    conn.commit()
    conn.close()

def get_user(email):
    conn = create_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE email=?", (email,))
    user = c.fetchone()
    conn.close()
    return user


# Check if user is logged in
def is_logged_in():
    return 'logged_in' in session

@app.route('/')
def index():
    return render_template('index.html', is_logged_in=is_logged_in())

@app.route('/dashboard', methods=['GET'])
def dashboard():
    if is_logged_in:
        return render_template('dashboard.html', is_logged_in=is_logged_in())
    else:
        return redirect(url_for('login'))
    
@app.route('/newText', methods=['GET', 'POST'])
def newText():
    if request.method == 'POST':
        return 
    if is_logged_in:
        return render_template('newText.html', is_logged_in=is_logged_in())
    return redirect(url_for('login'))
    
@app.route('/export', methods=['GET', 'POST'])
def export():
    if request.method == 'POST':
        return 
    if is_logged_in:
        return render_template('export.html', is_logged_in=is_logged_in())
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        if password != confirm_password:
            flash('Passwords do not match.', 'error')
            return redirect(url_for('register'))

        existing_user = get_user(email)
        if existing_user:
            flash('Email already exists. Please log in.', 'error')
            return redirect(url_for('login'))
        else:
            register_user(email, password)
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = get_user(email)
        if user and user[2] == password:  # user[2] is the password field
            session['logged_in'] = True
            flash('Login successful!', 'success')
            print("logged in as " + str(user))
            return redirect(url_for('index'))
        else:
            flash('Invalid email or password. Please try again.', 'error')

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You have been logged out.', 'success')
    return redirect(url_for('index'))

if __name__ == '__main__':
    create_table()
    card_create_table()
    app.run(debug=True)