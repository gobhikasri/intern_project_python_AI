from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify
from flask_login import login_user, logout_user, login_required, current_user
import requests
import json

from backend.config import Config
from backend.database.models import (
    create_user, get_user_by_email, get_user_by_google_id, get_user_by_id
)
from backend.auth.password_utils import hash_password, verify_password
from backend.auth.user_model import User

auth_bp = Blueprint('auth', __name__, template_folder='../../frontend/templates')

# Google OAuth setup helper
def get_google_provider_cfg():
    try:
        return requests.get(Config.GOOGLE_DISCOVERY_URL).json()
    except Exception:
        return None

@auth_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('weather.dashboard_view'))
        
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        
        if not name or not email or not password:
            flash('All fields are required.', 'danger')
            return render_template('signup.html')
            
        existing_user = get_user_by_email(email)
        if existing_user:
            flash('An account with that email already exists.', 'danger')
            return render_template('signup.html')
            
        hashed = hash_password(password)
        # Default avatar picture URL
        avatar = f"https://api.dicebear.com/7.x/adventurer/svg?seed={name}"
        
        new_db_user = create_user(email=email, name=name, password_hash=hashed, profile_pic=avatar)
        
        if new_db_user:
            user_obj = User.get(new_db_user['id'])
            login_user(user_obj)
            flash('Registration successful! Welcome to NinoSense.', 'success')
            return redirect(url_for('weather.dashboard_view'))
        else:
            flash('Error creating account. Please try again.', 'danger')
            
    return render_template('signup.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('weather.dashboard_view'))
        
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user_row = get_user_by_email(email)
        if not user_row or not user_row['password_hash']:
            flash('Invalid email or password.', 'danger')
            return render_template('login.html')
            
        if verify_password(password, user_row['password_hash']):
            user_obj = User.get(user_row['id'])
            login_user(user_obj, remember=True)
            flash('Successfully logged in!', 'success')
            return redirect(url_for('weather.dashboard_view'))
        else:
            flash('Invalid email or password.', 'danger')
            
    return render_template('login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('weather.index_view'))

# ==========================================
# Google OAuth2 Login & Mock Flow
# ==========================================

@auth_bp.route('/auth/google')
def google_login():
    # If Google Client ID is configured, run actual Google OAuth
    if Config.GOOGLE_CLIENT_ID and Config.GOOGLE_CLIENT_SECRET:
        # Implementation of genuine Google OAuth Redirect
        google_provider_cfg = get_google_provider_cfg()
        if not google_provider_cfg:
            flash("Failed to reach Google configuration. Using mock Google sign-in instead.", "warning")
            return redirect(url_for('auth.google_mock'))
            
        authorization_endpoint = google_provider_cfg["authorization_endpoint"]
        
        # Build OAuth URL manually
        redirect_uri = request.base_url + "/callback"
        scope = "openid email profile"
        
        # In a real app we'd use oauthlib/authlib. Since we want standard flow:
        # Redirect the user
        from urllib.parse import urlencode
        params = {
            "client_id": Config.GOOGLE_CLIENT_ID,
            "redirect_uri": redirect_uri,
            "scope": scope,
            "response_type": "code",
            "access_type": "offline",
            "prompt": "select_account"
        }
        return redirect(f"{authorization_endpoint}?{urlencode(params)}")
    else:
        # If credentials are not set, redirect to mock consent screen
        return redirect(url_for('auth.google_mock'))

@auth_bp.route('/auth/google/mock')
def google_mock():
    """Renders a simulated Google Account Chooser screen."""
    return render_template('google_chooser.html')

@auth_bp.route('/auth/google/mock/submit', methods=['POST'])
def google_mock_submit():
    """Handles the selection in the mock Google accounts list."""
    email = request.form.get('email')
    name = request.form.get('name')
    google_id = request.form.get('google_id')
    profile_pic = request.form.get('profile_pic')
    
    # Check if this Google user already exists
    user_row = get_user_by_google_id(google_id)
    if not user_row:
        # Maybe check if email already exists
        existing_email = get_user_by_email(email)
        if existing_email:
            # Connect google_id to existing email user
            conn = sqlite3 = get_db_connection()
            conn.execute('UPDATE users SET google_id = ?, profile_pic = ? WHERE email = ?', (google_id, profile_pic, email))
            conn.commit()
            conn.close()
            user_row = get_user_by_email(email)
        else:
            # Create brand new user
            user_row = create_user(
                email=email,
                name=name,
                google_id=google_id,
                profile_pic=profile_pic
            )
            
    user_obj = User.get(user_row['id'])
    login_user(user_obj)
    
    flash(f"Logged in with Google as {name} ({email})!", 'success')
    return redirect(url_for('weather.dashboard_view'))

@auth_bp.route('/auth/google/callback')
def google_callback():
    """Actual Google OAuth callback handler."""
    code = request.args.get("code")
    google_provider_cfg = get_google_provider_cfg()
    if not google_provider_cfg:
        flash("Could not get Google discovery config during callback.", "danger")
        return redirect(url_for('auth.login'))
        
    token_endpoint = google_provider_cfg["token_endpoint"]
    redirect_uri = request.base_url # callback URL
    
    # Exchange code for tokens
    data = {
        "code": code,
        "client_id": Config.GOOGLE_CLIENT_ID,
        "client_secret": Config.GOOGLE_CLIENT_SECRET,
        "redirect_uri": redirect_uri,
        "grant_type": "authorization_code"
    }
    
    token_response = requests.post(token_endpoint, data=data)
    token_json = token_response.json()
    
    # Verify and parse ID Token
    # For a real app, verify the token signature. Here, we parse the user info from userinfo endpoint
    userinfo_endpoint = google_provider_cfg["userinfo_endpoint"]
    access_token = token_json.get("access_token")
    
    headers = {"Authorization": f"Bearer {access_token}"}
    userinfo_response = requests.get(userinfo_endpoint, headers=headers)
    userinfo = userinfo_response.json()
    
    google_id = userinfo.get("sub")
    email = userinfo.get("email")
    name = userinfo.get("name")
    profile_pic = userinfo.get("picture")
    
    if not email:
        flash("Google did not return an email address.", "danger")
        return redirect(url_for('auth.login'))
        
    # Check if user exists
    user_row = get_user_by_google_id(google_id)
    if not user_row:
        # Check if email is present
        existing = get_user_by_email(email)
        if existing:
            # Link Google account
            conn = get_db_connection()
            conn.execute('UPDATE users SET google_id = ?, profile_pic = ? WHERE email = ?', (google_id, profile_pic, email))
            conn.commit()
            conn.close()
            user_row = get_user_by_email(email)
        else:
            # Create user
            user_row = create_user(
                email=email,
                name=name,
                google_id=google_id,
                profile_pic=profile_pic
            )
            
    user_obj = User.get(user_row['id'])
    login_user(user_obj)
    flash(f"Successfully logged in with Google as {name}!", "success")
    return redirect(url_for('weather.dashboard_view'))
