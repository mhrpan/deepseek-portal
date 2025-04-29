from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, logout_user, current_user
import uuid

# Import from db_utils instead of app
from db_utils import get_db_connection

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

# User class for flask-login
class User:
    def __init__(self, id, email, phone, first_name, last_name, role):
        self.id = id
        self.email = email
        self.phone = phone
        self.first_name = first_name
        self.last_name = last_name
        self.role = role
        self.is_authenticated = True
        self.is_active = True
        self.is_anonymous = False

    def get_id(self):
        return str(self.id)
    
    def is_admin(self):
        return self.role == 'admin'
    
    @staticmethod
    def get(user_id):
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('SELECT id, email, phone, first_name, last_name, role FROM users WHERE id = %s', (user_id,))
        user_data = cur.fetchone()
        cur.close()
        conn.close()
        
        if user_data:
            return User(
                id=user_data['id'],
                email=user_data['email'],
                phone=user_data['phone'],
                first_name=user_data['first_name'],
                last_name=user_data['last_name'],
                role=user_data['role']
            )
        return None
    
    @staticmethod
    def get_by_email(email):
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('SELECT id, email, phone, first_name, last_name, password_hash, role FROM users WHERE email = %s', (email,))
        user_data = cur.fetchone()
        cur.close()
        conn.close()
        
        if not user_data:
            return None
        
        user = User(
            id=user_data['id'],
            email=user_data['email'],
            phone=user_data['phone'],
            first_name=user_data['first_name'],
            last_name=user_data['last_name'],
            role=user_data['role']
        )
        user.password_hash = user_data['password_hash']
        return user
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

# Traditional login routes
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = User.get_by_email(email)
        
        if user and user.check_password(password):
            login_user(user)
            
            if user.is_admin():
                return redirect(url_for('admin.dashboard'))
            else:
                return redirect(url_for('index'))
        
        flash('Invalid email or password', 'danger')
    
    return render_template('admin/login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

# API routes for frontend
@auth_bp.route('/api/login', methods=['POST'])
def api_login():
    """API endpoint for login from frontend"""
    if not request.is_json:
        return jsonify({'status': 'error', 'message': 'JSON request expected'}), 400
        
    data = request.json
    email = data.get('email')
    password = data.get('password')
    
    user = User.get_by_email(email)
    
    if user and user.check_password(password):
        login_user(user)
        return jsonify({
            'status': 'success',
            'message': 'Login successful',
            'user': {
                'id': str(user.id),
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'role': user.role
            }
        })
    
    return jsonify({'status': 'error', 'message': 'Invalid email or password'}), 401


@auth_bp.route('/api/register', methods=['POST'])
def api_register():
    """API endpoint for user registration"""
    if not request.is_json:
        return jsonify({'status': 'error', 'message': 'JSON request expected'}), 400
        
    data = request.json
    email = data.get('email')
    password = data.get('password')
    first_name = data.get('first_name')
    last_name = data.get('last_name')
    phone = data.get('phone')
    
    if not email or not password or not first_name or not last_name:
        return jsonify({'status': 'error', 'message': 'Required fields missing'}), 400
    
    # Check if user already exists
    existing_user = User.get_by_email(email)
    if existing_user:
        return jsonify({'status': 'error', 'message': 'Email already registered'}), 409
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        # Hash password
        password_hash = generate_password_hash(password)
        
        # Insert new user
        cur.execute("""
            INSERT INTO users (email, phone, password_hash, first_name, last_name, role)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING id
        """, (email, phone, password_hash, first_name, last_name, 'user'))
        
        result = cur.fetchone()
        user_id = result['id']  # Access by key name
        
        # Create a default family for this user
        family_name = f"{first_name}'s Family"
        cur.execute("""
            INSERT INTO families (name, created_by_user_id)
            VALUES (%s, %s)
            RETURNING id
        """, (family_name, user_id))
        
        result = cur.fetchone()
        family_id = result['id']  # Access by key name
        
        # Add user as admin of their family
        cur.execute("""
            INSERT INTO family_members (family_id, user_id, role)
            VALUES (%s, %s, %s)
        """, (family_id, user_id, 'admin'))
        
        conn.commit()
        
        # Create a user object and log them in
        user = User(
            id=user_id,
            email=email,
            phone=phone,
            first_name=first_name,
            last_name=last_name,
            role='user'
        )
        login_user(user)
        
        return jsonify({
            'status': 'success',
            'message': 'Registration successful',
            'user': {
                'id': str(user_id),
                'email': email,
                'first_name': first_name,
                'last_name': last_name,
                'role': 'user'
            }
        })
        
    except Exception as e:
        conn.rollback()
        print(f"Registration error: {str(e)}")  # Add debug print
        return jsonify({'status': 'error', 'message': str(e)}), 500
    finally:
        cur.close()
        conn.close()


@auth_bp.route('/api/logout', methods=['POST'])
def api_logout():
    """API endpoint for logout"""
    logout_user()
    return jsonify({'status': 'success', 'message': 'Logged out successfully'})


@auth_bp.route('/api/user', methods=['GET'])
def get_current_user():
    """API endpoint to get current user data"""
    if current_user.is_authenticated:
        return jsonify({
            'id': str(current_user.id),
            'email': current_user.email,
            'first_name': current_user.first_name,
            'last_name': current_user.last_name,
            'role': current_user.role
        })
    else:
        return jsonify({'status': 'error', 'message': 'Not authenticated'}), 401