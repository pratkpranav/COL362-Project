from flask import Blueprint, render_template, request, flash, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, logout_user, current_user
from website.database import db_get_user_with_handle, db_insert_user
import website
import logging
import json


auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method ==  'POST':
        handle = request.form.get('handle')
        password = request.form.get('password')
        logging.debug('POST request received with Handle:%s, Password:%s', handle, password)

        user = db_get_user_with_handle(website.db, website.dbConn, handle)
        if user: #if user exist
            logging.debug("User %s found in database, matching password", handle)

            is_admin = False
            if handle == "col362_ta":
                is_admin = True

            user = website.User(user, is_admin)
            if check_password_hash(user.password, password):
                logging.debug("Login for user %s sucessful, redirecting to home", handle)
                flash('Logged in sucessfuly!', category='success')

                login_user(user, remember=True)

                return redirect(url_for('views.home'))
            else:
                logging.debug("User %s entered incorrect password.", handle)
                flash('Incorrect password, try again.', category='error')
        else:
            logging.debug("Handle does not exist")
            flash('Handle does not exist.', category='error')
    return render_template("login.html", user=current_user)

@auth.route('/logout')
@login_required
def logout():
    user = current_user
    logging.debug("Logging out user with handle: %s", user.handle)
    logout_user()
    logging.debug("Logout Successful, redirecting to login page")
    return redirect(url_for('auth.login'))

@auth.route('/sign-up' , methods=['GET', 'POST']) 
def sign_up():
    if request.method == 'POST':
        firstname = request.form.get('firstname')
        lastname = request.form.get('lastname')
        handle = request.form.get('handle')
        country = request.form.get('country')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        assert len(handle) > 0
        assert len(password1) > 0
        assert len(password2) > 0
        assert len(firstname) > 0

        logging.debug("Got Sign Up request with handle: %s, firstname: %s, lastname: %s, country: %s, password1: %s, password2: %s", handle, firstname, lastname, country, password1, password2)

        user = db_get_user_with_handle(website.db, website.dbConn, handle)
        if user:
            logging.debug("Handle already Existed")
            flash('Handle already exists.', category = 'error')
        elif len(handle) < 4:
            logging.debug("User entered a small handle")
            flash("Handle must be greater than 4 characters", category='error')
        elif len(firstname) < 2:
            logging.debug("User entered a small firstname")
            flash("First Name must be greater than 2 characters", category='error')
        elif password1 != password2:
            logging.debug("User entred non-matching passwords")
            flash("Password don't match", category='error')
        elif len(password1) < 7:
            logging.debug("User entred a small password")
            flash("Password must be greater than 7 characters", category='error')
        else:

            password = generate_password_hash(password1, method='sha256')
            def_rating = int(website.parser['users']['default_rating'])
            def_contribution = int(website.parser['users']['default_contribution'])
            new_user = website.User((handle, firstname, lastname, country, def_rating, def_contribution, password))

            db_insert_user(website.db, website.dbConn, new_user)
            flash('Account Created!', category='success')
            login_user(new_user, remember=True)

            return redirect(url_for('views.home'))
        
    return render_template("sign_up.html", user=current_user)


