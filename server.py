from flask import Flask, render_template, redirect, request, url_for, session
from functools import wraps
import os
from db import *
from os import environ as env
from urllib.parse import quote_plus, urlencode

from authlib.integrations.flask_client import OAuth

app = Flask(__name__)
app.secret_key = os.environ["FLASK_SECRET_KEY"]
setup()


oauth = OAuth(app)

oauth.register(
    "auth0",
    client_id=env.get("AUTH0_CLIENT_ID"),
    client_secret=env.get("AUTH0_CLIENT_SECRET"),
    client_kwargs={
        "scope": "openid profile email",
    },
    server_metadata_url=f'https://{env.get("AUTH0_DOMAIN")}/.well-known/openid-configuration',
)


@app.route("/login")
def login():
    return oauth.auth0.authorize_redirect(
        redirect_uri=url_for("callback", _external=True)
    )


@app.route("/callback", methods=["GET", "POST"])
def callback():
    token = oauth.auth0.authorize_access_token()
    session["user"] = token
    print(token)
    return redirect("/")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(
        "https://"
        + env.get("AUTH0_DOMAIN")
        + "/v2/logout?"
        + urlencode(
            {
                "returnTo": url_for("hello", _external=True),
                "client_id": env.get("AUTH0_CLIENT_ID"),
            },
            quote_via=quote_plus,
        )
    )


@app.route("/")
def hello():
    colors = get_colors()
    last_color = session.get("last_color")

    return render_template("main.html", colors=colors, last_color=last_color)


@app.route("/new_color", methods=["POST"])
def new_color():
    color_code = request.form.get("color", "#ffffff")
    color_name = request.form.get("name", "black")
    create_color(color_code, color_name)
    session["last_color"] = color_name
    return redirect(url_for("hello"))

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'profile' not in session:
        # Redirect to Login page here
            return redirect('/')
        return f(*args, **kwargs) #do the normal behavior -- return as it does.

    return decorated