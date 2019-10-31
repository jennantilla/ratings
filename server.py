"""Movie Ratings."""

from jinja2 import StrictUndefined

from flask import (Flask, render_template, redirect, request, flash, session)
from flask_debugtoolbar import DebugToolbarExtension

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

    return render_template('homepage.html')

@app.route('/register', methods=['GET'])
def register():
    """Shows user registration form"""

    return render_template('register_form.html')

@app.route('/register', methods=['POST'])
def register_process():
    """Saving new user info to database"""

    email_address = request.form.get('email')
    password = request.form.get('password')

    user = User.query.filter_by(email=email_address).first()

    if user.email==email_address:
        print("YAY! You're already in our system! Please head to the login page. :D")

        return redirect('/login')
    
    else:
        new_user = User(email=email_address, password=password)
        db.session.add(new_user)
        db.session.commit()

        return redirect('/')


@app.route('/login', methods=["GET"])
def login():
    """Logs in a current user"""

    return render_template('login.html')

@app.route('/login', methods=["POST"])
def login_process():
    """Handles login"""

    email_address = request.form.get('email')
    password = request.form.get('password')

    user = User.query.filter_by(email=email_address, password=password).first()

    if user == None: 
        flash('Your email or password is incorrect. Please try again.')
        return redirect('/login')

    if user.email == email_address and user.password == password:
        session["user"] = user.email
        flash('You were successfully logged in!')
        return redirect(f'/users/{user.user_id}')


@app.route('/logout')
def logout():
    """Handles user log out"""

    session.clear()
    flash('You were successfully logged out. SEE YOU LATER ALLIGATOR!')
    return redirect('/')
    
@app.route('/users/<int:user_id>')
def user_info(user_id):
    """Display user information: age, zipcode, ratings"""

    user_obj = User.query.filter_by(user_id = user_id).first()
    rating_obj = user_obj.ratings

    return render_template("user_page.html", user=user_obj, ratings=rating_obj)



@app.route('/users')
def user_list():
    """Show list of users"""

    users = User.query.all()
    return render_template('user_list.html', users=users)


if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the
    # point that we invoke the DebugToolbarExtension
    app.debug = True
    # make sure templates, etc. are not cached in debug mode
    app.jinja_env.auto_reload = app.debug

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)

    app.run(port=5000, host='0.0.0.0')
