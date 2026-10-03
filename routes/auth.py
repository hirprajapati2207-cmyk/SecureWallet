import functools
from flask import Blueprint, flash, g, redirect, render_template, request, session, url_for
from database.database import get_db
from security.authentication import hash_password, verify_password

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        db = get_db()
        error = None

        if not name or not email or not password:
            error = 'Name, email and password are required.'
        elif password != confirm_password:
            error = 'Passwords do not match.'

        if error is None:
            try:
                cur = db.execute(
                    "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
                    (name, email, hash_password(password)),
                )
                user_id = cur.lastrowid
                
                # Insert default categories
                default_categories = ['Personal', 'Work', 'Finance', 'Social Media']
                for cat in default_categories:
                    db.execute("INSERT INTO categories (user_id, category_name) VALUES (?, ?)", (user_id, cat))
                
                db.commit()
            except db.IntegrityError:
                error = f"Email {email} is already registered."
            else:
                flash("Registration successful. Please log in.")
                return redirect(url_for("auth.login"))

        flash(error)

    return render_template('auth/register.html')

@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        db = get_db()
        error = None
        user = db.execute(
            'SELECT * FROM users WHERE email = ?', (email,)
        ).fetchone()

        if user is None:
            error = 'Incorrect email or password.'
        elif not verify_password(user['password_hash'], password):
            error = 'Incorrect email or password.'

        if error is None:
            session.clear()
            session['user_id'] = user['user_id']
            # Log activity
            db.execute('INSERT INTO activity_logs (user_id, action, description) VALUES (?, ?, ?)',
                       (user['user_id'], 'LOGIN', 'User logged in successfully.'))
            db.commit()
            return redirect(url_for('dashboard.index'))

        flash(error)

    return render_template('auth/login.html')

@bp.route('/logout')
def logout():
    user_id = session.get('user_id')
    if user_id:
        db = get_db()
        db.execute('INSERT INTO activity_logs (user_id, action, description) VALUES (?, ?, ?)',
                   (user_id, 'LOGOUT', 'User logged out.'))
        db.commit()
    session.clear()
    return redirect(url_for('auth.login'))
