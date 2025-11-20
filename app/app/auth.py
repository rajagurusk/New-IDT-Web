from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_user, UserMixin

auth_bp = Blueprint('auth', __name__, url_prefix="/auth")

class DummyUser(UserMixin):
    id = 1

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = DummyUser()
        login_user(user)
        return redirect(url_for('main.home'))
    return render_template('login.html')

from app import login_manager

@login_manager.user_loader
def load_user(user_id):
    return DummyUser()
