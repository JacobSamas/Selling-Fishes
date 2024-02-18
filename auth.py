from flask import Blueprint, render_template, redirect, url_for, request, flash
from werkzeug.security import generate_password_hash, check_password_hash
from extensions import db
from models import User
from extensions import db, login_manager
from flask_login import login_user, logout_user, login_required

auth_blueprint = Blueprint('auth', __name__)

@auth_blueprint.route('/login', methods=['GET', 'POST'])
def login():
    # login logic
    pass

@auth_blueprint.route('/signup', methods=['GET', 'POST'])
def signup():
    # signup logic
    pass

@auth_blueprint.route('/logout')
@login_required
def logout():
    # logout logic
    pass

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
