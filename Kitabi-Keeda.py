import flask
import createdb
import secrets

app = flask.Flask("kitabi-keeda")

app.secret_key = secrets.token_hex(16)

# Mock user database
users_db = {
    "user1": {"password": "password1"},
    "user2": {"password": "password2"}
}

@app.before_request
def before_request():
    flask.session.permanent = True

@app.route("/")
def index():
    return flask.render_template("index.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if flask.request.method == "POST":
        username = flask.request.form.get("username")
        password = flask.request.form.get("password")
        
        # Check if username exists and passwords match
        if username in users_db and users_db[username]["password"] == password:
            # Authentication successful, create session ID
            flask.session["username"] = username
            return flask.redirect(flask.url_for("index"))
        else:
            return "Invalid username or password"
    else:
        return flask.render_template("login.html")

if __name__ == '__main__':
    app.run()
