"""Movie Ratings."""

from jinja2 import StrictUndefined
from flask_debugtoolbar import DebugToolbarExtension
from flask import (Flask, render_template, redirect, request, flash,
                   session)
from model import User, Rating, Movie, connect_to_db, db


app = Flask(__name__)
# Required to use Flask sessions and the debug toolbar
app.secret_key = "ABC"

# Normally, if you use an undefined variable in Jinja2, it fails
# silently. This is horrible. Fix this so that, instead, it raises an
# error.
app.jinja_env.undefined = StrictUndefined


@app.route('/')
def index():
    """Homepage."""

    return render_template("homepage.html")

@app.route("/users")
def user_list():
    """Show list of users."""

    users = User.query.all()
    return render_template("user_list.html", users=users)

@app.route("/register", methods= ["GET"])
def register_form():
    """Show registeration form to put in email address and password"""

    return render_template("register_form.html")

@app.route("/register_process", methods= ["POST"])
def register_process():
    """Process the registration form, checking to see if user exists"""

    email = request.form.get("email")
    password = request.form.get("password")
    if User.query.filter_by(email=email).first()==[]:
        user = User(email=email,
                    password=password)
        db.session.add(user)
    else:
        flash("You've already registered. Please login.")

    db.session.commit()

    return redirect("/")

@app.route("/login", methods = ['GET','POST'])
def login():
    """Get and process login info"""

    if request.method == 'POST':
        email = request.form.get("email")
        password = request.form.get("password")
        user = User.query.filter_by(email=email).first()

        if user == None: # handling exception when the user doesn't exist
            flash("You have not yet registered. Please register")
            return redirect("/register")
        else:
            sql_password = user.password
            if password == sql_password:
                session['user_id'] = user.user_id
                flash("Logged in.")
                return redirect("/")
            else:
                flash("Invalid credentials")

    return render_template('login.html')

@app.route("/logout", methods = ['POST'])
def logout():
    """Get and process logout info"""

    session.pop('user_id')
    flash("Logged out.")
    return redirect("/")

@app.route("/users/<user_id>")
def user_info(user_id):

    user = User.query.filter_by(user_id=user_id).first()
    age = user.age
    zipcode = user.zipcode
    info = []
    for rating in user.ratings:
        movie_id = rating.movie_id
        title = Movie.query.filter_by(movie_id=movie_id).first().title
        score = rating.score
        info.append((title, score))

    print(info)

    return render_template("/")

if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the
    # point that we invoke the DebugToolbarExtension
    app.debug = True
    # make sure templates, etc. are not cached in debug mode
    app.jinja_env.auto_reload = app.debug

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)
    app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
    app.run(port=5000, host='0.0.0.0')
