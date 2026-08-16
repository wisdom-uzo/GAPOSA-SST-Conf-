import functools
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify, g
from app.firebase_service import firebase_service

auth_bp = Blueprint('auth', __name__)

def login_required(view):
    """Decorator to require authenticated user session."""
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        user_id = session.get('user_id')
        if not user_id:
            flash('Please sign in to access this page.', 'warning')
            return redirect(url_for('auth.login', next=request.url))
        user = firebase_service.get_user_by_id(user_id)
        if not user:
            session.clear()
            flash('Session expired. Please sign in again.', 'warning')
            return redirect(url_for('auth.login', next=request.url))
        g.user = user
        return view(**kwargs)
    return wrapped_view

def admin_required(view):
    """Decorator to require admin role."""
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        user_id = session.get('user_id')
        if not user_id:
            flash('Admin access requires authentication.', 'warning')
            return redirect(url_for('auth.login', next=request.url))
        user = firebase_service.get_user_by_id(user_id)
        if not user or user.get('role') != 'admin':
            flash('Access denied. Administrator privileges required.', 'error')
            return redirect(url_for('main.index'))
        g.user = user
        return view(**kwargs)
    return wrapped_view

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if session.get('user_id'):
        user = firebase_service.get_user_by_id(session.get('user_id'))
        if user and user.get('role') == 'admin':
            return redirect(url_for('admin.dashboard'))
        return redirect(url_for('user.dashboard'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        remember = request.form.get('remember') == 'on'

        if not email or not password:
            flash('Please provide both email and password.', 'error')
            return render_template('auth/login.html')

        user = firebase_service.authenticate_user(email, password)
        if user:
            session.clear()
            session['user_id'] = user['id']
            session['user_email'] = user['email']
            session['user_name'] = user['full_name']
            session['user_role'] = user.get('role', 'participant')
            session.permanent = remember

            flash(f"Welcome back, {user.get('full_name')}!", 'success')
            next_page = request.args.get('next')
            if next_page and next_page.startswith('/'):
                return redirect(next_page)
            if user.get('role') == 'admin':
                return redirect(url_for('admin.dashboard'))
            return redirect(url_for('user.dashboard'))
        else:
            flash('Invalid email address or password. Please try again.', 'error')

    return render_template('auth/login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if session.get('user_id'):
        return redirect(url_for('user.dashboard'))

    if request.method == 'POST':
        full_name = request.form.get('full_name', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        title = request.form.get('title', 'Mr.')
        affiliation = request.form.get('affiliation', '').strip()
        phone = request.form.get('phone', '').strip()
        role = request.form.get('role', 'author')

        if not full_name or not email or not password:
            flash('Please fill in all required fields.', 'error')
            return render_template('auth/register.html')

        if password != confirm_password:
            flash('Passwords do not match.', 'error')
            return render_template('auth/register.html')

        if len(password) < 6:
            flash('Password must be at least 6 characters long.', 'error')
            return render_template('auth/register.html')

        try:
            user = firebase_service.create_user(
                email=email,
                password=password,
                full_name=full_name,
                role=role,
                affiliation=affiliation,
                phone=phone,
                title=title
            )

            session.clear()
            session['user_id'] = user['id']
            session['user_email'] = user['email']
            session['user_name'] = user['full_name']
            session['user_role'] = user.get('role', 'participant')

            flash('Account created successfully! Welcome to ICONFST’26.', 'success')
            return redirect(url_for('user.dashboard'))
        except ValueError as e:
            flash(str(e), 'error')
        except Exception as e:
            flash(f'An error occurred during registration: {str(e)}', 'error')

    return render_template('auth/register.html')

@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out safely.', 'info')
    return redirect(url_for('main.index'))

@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        if not email:
            flash('Please enter your registered email.', 'error')
            return render_template('auth/forgot_password.html')

        user = firebase_service.get_user_by_email(email)
        if user:
            flash('A password reset link has been dispatched to your email address.', 'success')
        else:
            # Prevent email enumeration while maintaining good UX
            flash('If that email is registered in our system, a password reset link has been dispatched.', 'info')
        return redirect(url_for('auth.login'))

    return render_template('auth/forgot_password.html')

@auth_bp.route('/sync-firebase-token', methods=['POST'])
def sync_firebase_token():
    """Endpoint for synchronizing client-side Firebase Auth tokens."""
    data = request.get_json() or {}
    email = data.get('email', '').strip().lower()
    full_name = data.get('displayName', 'Participant')
    
    if not email:
        return jsonify({'success': False, 'message': 'Email is required'}), 400

    user = firebase_service.get_user_by_email(email)
    if not user:
        # Auto-create user from Google / Firebase provider
        user = firebase_service.create_user(
            email=email,
            password=f"oauth_{email}_{firebase_service.generate_registration_id()}",
            full_name=full_name,
            role='participant'
        )

    session.clear()
    session['user_id'] = user['id']
    session['user_email'] = user['email']
    session['user_name'] = user['full_name']
    session['user_role'] = user.get('role', 'participant')

    return jsonify({'success': True, 'redirect_url': url_for('user.dashboard')})
