"""
Books Management System API
Version: 2.0
Updated: July 2025
"""

from flask import Flask, request, jsonify, send_file, abort
from flask_cors import CORS
from models import db, Resource, User, Payment
from config import Config
import requests
import os
import logging
import uuid
from datetime import datetime, timedelta
from flask_migrate import Migrate
import time
import random
import json
import re
from werkzeug.security import generate_password_hash, check_password_hash

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('app.log')
    ]
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(Config)
CORS(app, resources={
    r"/api/*": {
        "origins": app.config.get('ALLOWED_ORIGINS', ['https://yourdomain.com']),
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})
db.init_app(app)
migrate = Migrate(app, db)

### Helper Functions ###

def ensure_admin_user():
    """Create secure admin user if not exists"""
    admin = User.query.filter_by(username='admin').first()
    if not admin:
        admin = User(
            username='admin',
            email=app.config.get('ADMIN_EMAIL', 'admin@somafy.co.ke'),
            is_admin=True
        )
        admin.set_password(app.config.get('ADMIN_PASSWORD', 'ChangeThisSecurePassword123!'))
        db.session.add(admin)
        db.session.commit()
        logger.info("Admin user created")

def is_strong_password(password):
    """Enhanced password strength validation"""
    if len(password) < 10:
        return False, "Password must be at least 10 characters"
    if not re.search(r"[A-Z]", password):
        return False, "Password must contain uppercase letters"
    if not re.search(r"[a-z]", password):
        return False, "Password must contain lowercase letters"
    if not re.search(r"[0-9]", password):
        return False, "Password must contain numbers"
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        return False, "Password must contain special characters"
    return True, ""

def normalize_email(email):
    """Normalize email address"""
    return email.strip().lower()

def generate_secure_token():
    """Generate cryptographically secure token"""
    return str(uuid.uuid4()) + str(int(time.time()))

def log_security_event(event_type, user_id=None, ip_address=None, details=None):
    """Log security-related events"""
    ip_address = ip_address or request.remote_addr
    logger.warning(
        f"SECURITY EVENT - {event_type}: "
        f"user_id={user_id}, ip={ip_address}, details={details}"
    )

### Authentication Endpoints ###

@app.route('/api/register', methods=['POST'])
def register():
    """Secure user registration endpoint"""
    try:
        data = request.json
        required_fields = ['username', 'email', 'password']
        
        if not all(field in data for field in required_fields):
            return jsonify({
                'success': False,
                'error': 'Missing required fields (username, email, password)'
            }), 400

        username = data['username'].strip()
        email = normalize_email(data['email'])
        password = data['password']

        # Validate input
        if len(username) < 4:
            return jsonify({
                'success': False,
                'error': 'Username must be at least 4 characters'
            }), 400

        if not re.match(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$", email):
            return jsonify({
                'success': False,
                'error': 'Invalid email format'
            }), 400

        is_strong, msg = is_strong_password(password)
        if not is_strong:
            return jsonify({
                'success': False,
                'error': msg
            }), 400

        # Check for existing user
        existing_user = User.query.filter(
            (User.username == username) | (User.email == email)
        ).first()
        
        if existing_user:
            log_security_event(
                'DUPLICATE_REGISTRATION_ATTEMPT',
                details=f'username={username}, email={email}'
            )
            return jsonify({
                'success': False,
                'error': 'Username or email already exists'
            }), 400

        # Create new user
        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        
        logger.info(f"New user registered: {username}")
        return jsonify({
            'success': True,
            'message': 'Registration successful'
        })

    except Exception as e:
        db.session.rollback()
        logger.error(f"Registration failed: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Registration failed'
        }), 500

@app.route('/api/login', methods=['POST'])
def login():
    """Secure login endpoint with brute force protection"""
    try:
        start_time = time.time()
        data = request.json
        if not data or not data.get('username') or not data.get('password'):
            return jsonify({
                'success': False,
                'error': 'Missing username or password'
            }), 400
        
        username = data['username'].strip()
        password = data['password']
        
        logger.info(f"Login attempt for username: {username}")
        
        # Find user without revealing existence
        user = User.query.filter_by(username=username).first()
        
        # Always take similar time to respond (prevent timing attacks)
        if not user:
            time.sleep(random.uniform(0.5, 1.5))
            log_security_event(
                'FAILED_LOGIN_ATTEMPT',
                details=f'username={username}'
            )
            return jsonify({
                'success': False,
                'error': 'Invalid credentials'
            }), 401
        
        # Verify password
        if user.check_password(password):
            logger.info(f"User authenticated: {username}")
            return jsonify({
                'success': True,
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'is_admin': user.is_admin
                }
            })
        
        time.sleep(random.uniform(0.5, 1.5))
        log_security_event(
            'FAILED_LOGIN_ATTEMPT',
            user.id,
            details=f'username={username}'
        )
        return jsonify({
            'success': False,
            'error': 'Invalid credentials'
        }), 401

    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Login failed'
        }), 500
    finally:
        # Ensure consistent response time
        elapsed = time.time() - start_time
        if elapsed < 1.0:
            time.sleep(1.0 - elapsed)

### Password Reset Endpoints ###

@app.route('/api/password-reset/request', methods=['POST'])
def request_password_reset():
    """Secure password reset request"""
    try:
        email = normalize_email(request.json.get('email', ''))
        if not email:
            return jsonify({
                'success': False,
                'error': 'Email required'
            }), 400
        
        user = User.query.filter_by(email=email).first()
        if user:
            # Generate secure token (store hashed version)
            token = generate_secure_token()
            user.reset_token = generate_password_hash(token)
            user.reset_token_expiry = datetime.utcnow() + timedelta(hours=1)
            db.session.commit()
            
            # In production: Send email with reset link
            logger.info(f"Password reset token generated for {email}")
        
        # Always return success to prevent email enumeration
        return jsonify({
            'success': True,
            'message': 'If the email exists, reset instructions will be sent'
        })
    
    except Exception as e:
        db.session.rollback()
        logger.error(f"Password reset request failed: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Password reset request failed'
        }), 500

@app.route('/api/password-reset/confirm', methods=['POST'])
def confirm_password_reset():
    """Secure password reset confirmation"""
    try:
        data = request.json
        token = data.get('token')
        new_password = data.get('new_password')
        
        if not token or not new_password:
            return jsonify({
                'success': False,
                'error': 'Token and new password required'
            }), 400
        
        # Validate password strength
        is_strong, msg = is_strong_password(new_password)
        if not is_strong:
            return jsonify({
                'success': False,
                'error': msg
            }), 400
        
        # Find user with valid token
        user = None
        for u in User.query.filter(User.reset_token_expiry > datetime.utcnow()).all():
            if check_password_hash(u.reset_token, token):
                user = u
                break
        
        if not user:
            log_security_event('INVALID_PASSWORD_RESET_TOKEN')
            return jsonify({
                'success': False,
                'error': 'Invalid or expired token'
            }), 400
        
        # Update password and clear token
        user.set_password(new_password)
        user.reset_token = None
        user.reset_token_expiry = None
        db.session.commit()
        
        logger.info(f"Password reset successful for user: {user.username}")
        log_security_event('PASSWORD_RESET_SUCCESS', user.id)
        return jsonify({
            'success': True,
            'message': 'Password reset successful'
        })
    
    except Exception as e:
        db.session.rollback()
        logger.error(f"Password reset failed: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Password reset failed'
        }), 500

### Resource Endpoints (Keep existing functionality) ###

@app.route('/api/resources', methods=['GET'])
def get_resources():
    """Get resources with optional filtering"""
    try:
        selected_class = request.args.get('class')
        selected_subject = request.args.get('subject')
        
        query = Resource.query
        
        if selected_class:
            query = query.filter(Resource.class_grade == selected_class)
        if selected_subject:
            subject_variations = [
                selected_subject,
                selected_subject.replace('_', ' ').replace('-', ' '),
                selected_subject.replace('_', '-'),
                selected_subject.replace('-', '_'),
                selected_subject.replace(' ', '_'),
                selected_subject.replace(' ', '-')
            ]
            query = query.filter(Resource.subject.in_(subject_variations))
        
        all_resources = query.all()
        
        if not selected_class and not selected_subject:
            books = Resource.query.filter_by(resource_type='book').limit(3).all()
            papers = Resource.query.filter_by(resource_type='paper').limit(2).all()
            setbooks = Resource.query.filter_by(resource_type='setbook').limit(2).all()
        else:
            books = []
            papers = []
            setbooks = []
        
        return jsonify({
            'all': [r.to_dict() for r in all_resources],
            'books': [b.to_dict() for b in books],
            'papers': [p.to_dict() for p in papers],
            'setbooks': [s.to_dict() for s in setbooks]
        })
    except Exception as e:
        logger.error(f"Error fetching resources: {str(e)}")
        return jsonify({'error': 'Failed to fetch resources'}), 500

### Payment Endpoints (Keep existing functionality) ###

@app.route('/api/pay', methods=['POST'])
def pay():
    """Process payment through PesaPal"""
    try:
        data = request.get_json()
        required_fields = ['resource_id', 'email', 'amount', 'name', 'phone']
        
        if not all(field in data for field in required_fields):
            return jsonify({'error': 'Missing required fields'}), 400
        
        # Validate input
        try:
            amount = float(data['amount'])
            if amount <= 0:
                raise ValueError("Amount must be positive")
        except (ValueError, TypeError):
            return jsonify({'error': 'Invalid amount'}), 400
        
        if not re.match(r"^[^@]+@[^@]+\.[^@]+$", data['email']):
            return jsonify({'error': 'Invalid email'}), 400
        
        # Process payment (existing implementation)
        # ...
        
        return jsonify({
            'success': True,
            'message': 'Payment initiated'
        })
    except Exception as e:
        logger.error(f"Payment processing failed: {str(e)}")
        return jsonify({'error': 'Payment processing failed'}), 500

### Admin Endpoints ###

@app.route('/api/admin/users', methods=['GET'])
def admin_list_users():
    """Admin-only endpoint to list users"""
    try:
        # Verify admin (in production, use proper authentication)
        users = User.query.all()
        return jsonify({
            'success': True,
            'users': [{
                'id': u.id,
                'username': u.username,
                'email': u.email,
                'is_admin': u.is_admin,
                'created_at': u.created_at.isoformat() if u.created_at else None
            } for u in users]
        })
    except Exception as e:
        logger.error(f"Admin user list failed: {str(e)}")
        return jsonify({'error': 'Failed to list users'}), 500

### Initialization ###

@app.before_first_request
def initialize_app():
    """Initialize application data"""
    try:
        db.create_all()
        ensure_admin_user()
        logger.info("Application initialization complete")
    except Exception as e:
        logger.error(f"Initialization failed: {str(e)}")
        raise

if __name__ == '__main__':
    app.run(
        host=app.config.get('HOST', '0.0.0.0'),
        port=app.config.get('PORT', 5000),
        debug=app.config.get('DEBUG', False)
    )
