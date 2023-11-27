# ANPR Software for M.Sc. Project Summer 2023
# Developed by Emmanuel Begah (w1935132)

# File stores routes that user can navigate to

# Import Libraries
from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import User
from werkzeug.security import generate_password_hash, check_password_hash  # For password storage
from . import db
from flask_login import login_user, login_required, logout_user, current_user

auth = Blueprint('auth', __name__)


# Defining login route
@auth.route('/', methods=['GET', 'POST'])
def access():
    if request.method == 'POST':
        userkey = request.form.get('userkey')
        pin = request.form.get('password')

        user = User.query.filter_by(userkey=userkey).first()

        if user:
            if check_password_hash(user.pin, pin):
                flash('Access Granted', category='success')
                login_user(user, remember=True)
                return redirect(url_for('view.index'))
            else:
                flash('Access Denied', category='error')
        else:
            flash('UserKey not recognised', category='error')

    return render_template("access.html", user=current_user)


# Defining end-session route
@auth.route('/end-session')
@login_required
def end_session():
    logout_user()
    flash('Session Ended', category='success')
    return redirect(url_for('auth.access'))


# Defining register route
@auth.route('/register', methods=['GET', 'POST'])
@login_required
def register():
    # Fetch user input
    if request.method == 'POST':
        forename = request.form.get('forename')
        surname = request.form.get('surname')
        email1 = request.form.get('email1')
        email2 = request.form.get('email2')
        userkey = request.form.get('userkey')
        pin1 = request.form.get('password1')
        pin2 = request.form.get('password2')

        # Data Validation

        userEmail = User.query.filter_by(email=email1).first()
        userKey = User.query.filter_by(userkey=userkey).first()

        if userEmail:
            flash('Account already exists with this email.', category='error')
        elif userKey:
            flash('UserKey is already taken.', category='error')
        elif len(forename) < 2:
            flash('Forename must be greater than 2 characters.', category='error')
        elif len(surname) < 2:
            flash('Surname must be greater than 2 characters.', category='error')
        elif len(email1) < 4:
            flash('Email must be greater than 4 characters.', category='error')
        elif email1 != email2:
            flash('Email addresses do not match.', category='error')
        elif len(userkey) < 3:
            flash('UserKey must be greater than 3 characters.', category='error')
        elif pin1 != pin2:
            flash('Pins entered do not match.', category='error')
        elif len(pin1) != 4:
            flash('PIN must be 4-digits.', category='error')
        else:
            newUser = User(forename=forename, surname=surname, email=email1, userkey=userkey,
                           pin=generate_password_hash(pin1, method='sha256'))
            db.session.add(newUser)
            db.session.commit()
            flash('Account Registered', category='success')
            return redirect(url_for('view.index'))

    return render_template("register.html", user=current_user)
