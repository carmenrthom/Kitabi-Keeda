import flask
import createdb
import secrets


app = flask.Flask("kitabi-keeda")

app.secret_key = secrets.token_hex(16)


@app.before_request
def before_request():
    flask.session.permanet = True

@app.route("/")
def index():
    return flask.render_template("index.html")



if __name__ == '__main__':
    app.run()