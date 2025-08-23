from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_user, logout_user, login_required
from .models import User
from . import db
from email_validator import validate_email, EmailNotValidError
from werkzeug.security import generate_password_hash, check_password_hash
import secrets, json

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

def make_backup_codes(n=8):
    # generate n short hex codes (8 chars)
    return [secrets.token_hex(4) for _ in range(n)]

@auth_bp.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username','').strip()
        password = request.form.get('password','')
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('main.chat'))
        flash('Invalid credentials', 'error')
    return render_template('login.html')

@auth_bp.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username','').strip()
        email = request.form.get('email','').strip()
        password = request.form.get('password','')

        if not (3 <= len(username) <= 32):
            flash('Username must be 3-32 chars', 'error')
            return render_template('register.html')
        try:
            validate_email(email)
        except EmailNotValidError:
            flash('Invalid email', 'error')
            return render_template('register.html')
        if len(password) < 6:
            flash('Password must be at least 6 chars', 'error')
            return render_template('register.html')
        if User.query.filter((User.username==username) | (User.email==email)).first():
            flash('User already exists', 'error')
            return render_template('register.html')

        u = User(username=username, email=email)
        u.set_password(password)
        # generate backup codes and store hashed
        raw_codes = make_backup_codes(8)
        u.set_backup_codes(raw_codes)
        db.session.add(u)
        db.session.commit()
        # show the raw codes to the user on a page and instruct them to save
        return render_template('backup_codes.html', codes=raw_codes, username=username)
    return render_template('register.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

@auth_bp.route('/forgot', methods=['GET','POST'])
def forgot():
    # Flow: user submits username + one backup code + new password
    if request.method == 'POST':
        username = request.form.get('username','').strip()
        code = request.form.get('code','').strip()
        password = request.form.get('password','')
        if not (username and code and password and len(password) >= 6):
            flash('Please provide username, a backup code and a new password (>=6 chars)', 'error')
            return render_template('forgot.html')
        user = User.query.filter_by(username=username).first()
        if not user:
            flash('Unknown username', 'error')
            return render_template('forgot.html')
        # verify and consume code
        if user.consume_backup_code(code):
            user.set_password(password)
            db.session.commit()
            flash('Password reset successful. You can now login.', 'success')
            return redirect(url_for('auth.login'))
        else:
            flash('Invalid backup code', 'error')
    return render_template('forgot.html')
