from extensions import db, login_manager
from flask import Blueprint, render_template, redirect, url_for, request, flash
from werkzeug.security import generate_password_hash, check_password_hash
from models import User
from flask_login import login_user, logout_user, login_required

auth_blueprint = Blueprint('auth', __name__)

# Your routes and logic for login, signup, logout...


@auth_blueprint.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Add your login logic here
        pass

    return render_template('login.html')

@auth_blueprint.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        # Add your signup logic here
        pass

    return render_template('signup.html')

@auth_blueprint.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))  # Redirect to login after logout

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
