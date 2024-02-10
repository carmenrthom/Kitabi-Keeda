import flask
import sqlite3
import secrets

app = flask.Flask("kitabi-keeda")

app.secret_key = secrets.token_hex(16)

DATABASE = 'database.db'

def get_db():
    db = getattr(flask.g, '_database', None)
    if db is None:
        db = flask.g._database = sqlite3.connect(DATABASE)
    return db

def init_db():
    with app.app_context():
        db = get_db()
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(flask.g, '_database', None)
    if db is not None:
        db.close()

@app.route("/")
def index():
    return flask.render_template("index.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if flask.request.method == "POST":
        email = flask.request.form.get("email")
        password = flask.request.form.get("password")
        user = query_db('SELECT * FROM users WHERE email = ? AND password = ?', (email, password), one=True)
        if user:
            flask.session['user_id'] = user['id']
            return flask.redirect(flask.url_for("index"))
        else:
            return "Invalid email or password"
    else:
        return flask.render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if flask.request.method == "POST":
        email = flask.request.form.get("email")
        password = flask.request.form.get("password")
        confirm_password = flask.request.form.get("confirm_password")
        
        if password != confirm_password:
            return "Passwords do not match"
        
        db = get_db()
        cursor = db.cursor()
        cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
        existing_user = cursor.fetchone()
        
        if existing_user:
            return "Email already exists"
        
        cursor.execute('INSERT INTO users (email, password) VALUES (?, ?)', (email, password))
        db.commit()
        
        return flask.redirect(flask.url_for("login"))
    else:
        return flask.render_template("register.html")

def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv

if __name__ == '__main__':
    app.run()
