from flask import Flask, render_template, request, redirect, url_for, session, flash, Response
import sqlite3
import csv
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
                 lang TEXT NOT NULL,
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

def print_all_cards():
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM cards")
    rows = cursor.fetchall()
    conn.close()

    if rows:
        print("All entries in the cards table:")
        for row in rows:
            print(row)
    else:
        print("No entries found in the cards table.")


# Check if user is logged in
def is_logged_in():
    return 'logged_in' in session

@app.route('/')
def index():
    return render_template('index.html', is_logged_in=is_logged_in())


"""    
@app.route('/newText', methods=['GET', 'POST'])
def newText():
    if request.method == 'POST':
        return 
    if is_logged_in:
        return render_template('newText.html', is_logged_in=is_logged_in())
    return redirect(url_for('login'))
"""

@app.route('/newText', methods=['GET', 'POST'])
def new_text():
    if request.method == 'POST':
        if not is_logged_in():
            flash('You need to login first.', 'error')
            return redirect(url_for('login'))

        user_text = request.form['userText']
        difficulty = request.form['diff']
        language = request.form['lang']
        author = session.get('email')  # Assuming you store user's email in session upon login

        
        if not author:
            flash('Unable to retrieve user information.', 'error')
            return redirect(url_for('login'))

        # Insert the new text into the cards table
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO cards (text, diff, lang, auth) VALUES (?, ?, ?, ?)",
                       (user_text, difficulty, language, author))
        conn.commit()
        conn.close()
        print("ADDED TEXT TO DATABASE")

        flash('Text added successfully!', 'success')
        return redirect(url_for('dashboard'))

    # Render the new_text.html template for GET requests
    return render_template('newText.html', is_logged_in=is_logged_in())

@app.route('/dashboard', methods=['GET'])
def dashboard():
    if is_logged_in():
        # Fetch data from the cards table
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT text, lang, diff FROM cards")
        cards_data = cursor.fetchall()
        conn.close()

        # Render the dashboard template with cards data
        return render_template('dashboard.html', is_logged_in=is_logged_in(), cards_data=cards_data)
    else:
        return redirect(url_for('login'))

@app.route('/export', methods=['GET', 'POST'])
def export():
    if request.method == 'POST':
        lang = request.form.get('lang')

        # Fetch data from the cards table based on the selected language
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT text, lang, diff FROM cards WHERE lang=?", (lang,))
        cards_data = cursor.fetchall()
        conn.close()

        # Create a CSV string with the fetched data
        csv_data = "Text,Language,Difficulty\n"
        for card in cards_data:
            text = card[0].replace("\n", " ").strip()  # Remove newline characters and leading/trailing spaces
            lang = card[1]
            diff = str(card[2])

            # Escape commas within the text field by enclosing in double quotes and doubling any existing double quotes
            text = text.replace('"', '""')
            text = f'"{text}"' if ',' in text else text

            print("THIS IS THE TEXT")
            print(text)

            csv_data += f'{text},{lang},{diff}\n'

        # Set up response headers for CSV download
        response = Response(csv_data, mimetype='text/csv')
        response.headers.set("Content-Disposition", "attachment", filename="cards.csv")

        return response

    # Render the export.html template for GET requests
    return render_template('export.html')


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
            session['email'] = email
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