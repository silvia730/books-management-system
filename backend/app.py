from flask import Flask, request, jsonify, send_file, abort
from flask_cors import CORS
from models import db, Resource, User, Payment
from config import Config
import requests
import os
import logging
import uuid
from datetime import datetime
from flask_migrate import Migrate
import time
import random
import json
import re

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

app = Flask(__name__)
app.config.from_object(Config)
CORS(app)
db.init_app(app)
migrate = Migrate(app, db)

def ensure_admin_user():
    admin = User.query.filter_by(username='admin').first()
    if not admin:
        admin = User(username='admin', email='admin@somafy.co.ke')
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()
        logger.info("Admin user created")

def get_pesapal_token():
    """Get PesaPal access token"""
    try:
        logger.info("=== PESAPAL TOKEN REQUEST START ===")
        auth_url = f"{app.config['PESAPAL_BASE_URL']}/Auth/RequestToken"
        
        auth_data = {
            'consumer_key': app.config['PESAPAL_CONSUMER_KEY'],
            'consumer_secret': app.config['PESAPAL_CONSUMER_SECRET']
        }
        
        logger.info(f"Auth URL: {auth_url}")
        logger.info(f"Consumer key exists: {bool(app.config['PESAPAL_CONSUMER_KEY'])}")
        logger.info(f"Consumer secret exists: {bool(app.config['PESAPAL_CONSUMER_SECRET'])}")
        
        # Log request details (without exposing secrets)
        logger.info(f"Request method: POST")
        logger.info(f"Request headers: Content-Type: application/json")
        logger.info(f"Request timeout: 30 seconds")
        
        auth_resp = requests.post(auth_url, json=auth_data, timeout=30)
        
        logger.info(f"PesaPal auth response status: {auth_resp.status_code}")
        logger.info(f"PesaPal auth response headers: {dict(auth_resp.headers)}")
        logger.info(f"PesaPal auth response body: {auth_resp.text}")
        
        if not auth_resp.ok:
            error_details = {
                'status_code': auth_resp.status_code,
                'response_text': auth_resp.text,
                'response_headers': dict(auth_resp.headers)
            }
            logger.error(f"PesaPal authentication failed: {error_details}")
            
            # Try to parse error response
            try:
                error_json = auth_resp.json()
                error_message = error_json.get('error', error_json.get('message', auth_resp.text))
            except json.JSONDecodeError:
                error_message = auth_resp.text
            
            raise Exception(f"PesaPal authentication failed (Status: {auth_resp.status_code}): {error_message}")
        
        try:
            auth_response = auth_resp.json()
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse PesaPal auth response as JSON: {auth_resp.text}")
            raise Exception(f"Invalid JSON response from PesaPal: {str(e)}")
        
        access_token = auth_response.get('token')
        
        if not access_token:
            logger.error(f"No access token in PesaPal response: {auth_response}")
            raise Exception("No access token received from PesaPal")
        
        logger.info("PesaPal token received successfully")
        logger.info("=== PESAPAL TOKEN REQUEST END ===")
        return access_token
        
    except requests.exceptions.Timeout:
        logger.error("PesaPal authentication request timed out")
        raise Exception("PesaPal authentication request timed out")
    except requests.exceptions.ConnectionError as e:
        logger.error(f"Connection error during PesaPal authentication: {str(e)}")
        raise Exception(f"Unable to connect to PesaPal: {str(e)}")
    except requests.exceptions.RequestException as e:
        logger.error(f"Request error during PesaPal authentication: {str(e)}")
        raise Exception(f"PesaPal request failed: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error getting PesaPal token: {str(e)}")
        raise e

def generate_unique_order_id():
    """Generate a unique order tracking ID"""
    return str(uuid.uuid4())

def create_payment_record(order_tracking_id, resource_id, user_email, amount, status='PENDING'):
    """Create a payment record"""
    try:
        payment = Payment(
            order_tracking_id=order_tracking_id,
            resource_id=resource_id,
            user_email=user_email,
            amount=amount,
            status=status
        )
        db.session.add(payment)
        db.session.commit()
        logger.info(f"Payment record created successfully: {order_tracking_id}")
        return payment
    except Exception as e:
        logger.error(f"Failed to create payment record: {str(e)}")
        db.session.rollback()
        raise

def is_strong_password(password):
    """Check if password meets strength requirements"""
    if len(password) < 8:
        return False
    if not re.search(r"[A-Z]", password):
        return False
    if not re.search(r"[a-z]", password):
        return False
    if not re.search(r"[0-9]", password):
        return False
    return True

@app.route('/')
def index():
    return "Welcome to the Books Management System API!"

@app.route('/admin')
def admin_dashboard():
    """Serve the admin dashboard"""
    try:
        admin_path = os.path.join(os.path.dirname(__file__), '..', 'admin', 'index.html')
        if os.path.exists(admin_path):
            return send_file(admin_path)
        else:
            return "Admin dashboard not found. Please check the file path.", 404
    except Exception as e:
        logger.error(f"Error serving admin dashboard: {str(e)}")
        return "Error serving admin dashboard", 500

@app.route('/admin/<path:filename>')
def admin_static(filename):
    """Serve admin static files (CSS, JS, images)"""
    try:
        admin_dir = os.path.join(os.path.dirname(__file__), '..', 'admin')
        file_path = os.path.join(admin_dir, filename)
        
        # Security check - ensure file is within admin directory
        if not os.path.abspath(file_path).startswith(os.path.abspath(admin_dir)):
            return "Access denied", 403
            
        if os.path.exists(file_path):
            return send_file(file_path)
        else:
            return f"File not found: {filename}", 404
    except Exception as e:
        logger.error(f"Error serving admin static file {filename}: {str(e)}")
        return "Error serving file", 500

@app.route('/user')
def user_dashboard():
    """Serve the user dashboard"""
    try:
        user_path = os.path.join(os.path.dirname(__file__), '..', 'user', 'index.html')
        if os.path.exists(user_path):
            return send_file(user_path)
        else:
            return "User dashboard not found. Please check the file path.", 404
    except Exception as e:
        logger.error(f"Error serving user dashboard: {str(e)}")
        return "Error serving user dashboard", 500

@app.route('/user/<path:filename>')
def user_static(filename):
    """Serve user static files (CSS, JS, images)"""
    try:
        user_dir = os.path.join(os.path.dirname(__file__), '..', 'user')
        file_path = os.path.join(user_dir, filename)
        
        # Security check - ensure file is within user directory
        if not os.path.abspath(file_path).startswith(os.path.abspath(user_dir)):
            return "Access denied", 403
            
        if os.path.exists(file_path):
            return send_file(file_path)
        else:
            return f"File not found: {filename}", 404
    except Exception as e:
        logger.error(f"Error serving user static file {filename}: {str(e)}")
        return "Error serving file", 500

@app.route('/api/upload', methods=['POST'])
def upload_resource():
    resource_type = request.form.get('resourceType')
    class_grade = request.form.get('classGrade')
    subject = request.form.get('subject')
    title = request.form.get('title')
    description = request.form.get('description')
    cover_path = None

    if 'cover' in request.files:
        cover_file = request.files['cover']
        if cover_file.filename:
            from werkzeug.utils import secure_filename
            filename = secure_filename(cover_file.filename)
            covers_dir = os.path.join(os.path.dirname(__file__), 'static', 'covers')
            os.makedirs(covers_dir, exist_ok=True)
            file_path = os.path.join(covers_dir, filename)
            cover_file.save(file_path)
            cover_path = f'static/covers/{filename}'

    resource = Resource(
        resource_type=resource_type,
        class_grade=class_grade,
        subject=subject,
        title=title,
        description=description,
        cover=cover_path
    )
    db.session.add(resource)
    db.session.commit()
    return jsonify({'success': True, 'id': resource.id})

@app.route('/api/resources', methods=['GET'])
def get_resources():
    try:
        # Get query parameters for filtering
        selected_class = request.args.get('class')
        selected_subject = request.args.get('subject')
        
        # Start with base query
        query = Resource.query
        
        # Apply filters if provided
        if selected_class:
            query = query.filter(Resource.class_grade == selected_class)
        if selected_subject:
            # Handle different subject name formats (with underscores, hyphens, spaces)
            # Convert the selected subject to match the stored format
            subject_variations = [
                selected_subject,
                selected_subject.replace('_', ' ').replace('-', ' '),
                selected_subject.replace('_', '-'),
                selected_subject.replace('-', '_'),
                selected_subject.replace(' ', '_'),
                selected_subject.replace(' ', '-')
            ]
            query = query.filter(Resource.subject.in_(subject_variations))
        
        # Get all filtered resources
        all_resources = query.all()
        
        # Only show limited resources if no filters are applied
        if not selected_class and not selected_subject:
            books = Resource.query.filter_by(resource_type='book').limit(3).all()
            papers = Resource.query.filter_by(resource_type='paper').limit(2).all()
            setbooks = Resource.query.filter_by(resource_type='setbook').limit(2).all()
        else:
            books = []
            papers = []
            setbooks = []
        
        return jsonify({
            'all': [r.to_dict() for r in all_resources],  # New filtered results
            'books': [b.to_dict() for b in books],
            'papers': [p.to_dict() for p in papers],
            'setbooks': [s.to_dict() for s in setbooks]
        })
    except Exception as e:
        logger.error(f"Error fetching resources: {str(e)}")
        return jsonify({'error': f'Failed to fetch resources: {str(e)}'}), 500

@app.route('/api/resource/<int:resource_id>', methods=['DELETE'])
def delete_resource(resource_id):
    try:
        resource = Resource.query.get(resource_id)
        if not resource:
            return jsonify({'success': False, 'error': 'Resource not found'}), 404
        
        db.session.delete(resource)
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error deleting resource {resource_id}: {str(e)}")
        return jsonify({'success': False, 'error': f'Failed to delete resource: {str(e)}'}), 500

@app.route('/api/register', methods=['POST'])
def register():
    data = request.json
    if not data or not data.get('username') or not data.get('email') or not data.get('password'):
        return jsonify({'success': False, 'error': 'Missing fields'}), 400
    
    username = data['username']
    email = data['email']
    password = data['password']
    
    logger.info(f"Registration attempt for username: {username}, email: {email}")
    
    # Check password strength
    if not is_strong_password(password):
        return jsonify({
            'success': False,
            'error': 'Password must be at least 8 characters with uppercase, lowercase, and numbers'
        }), 400
    
    # Check if user already exists
    existing_user = User.query.filter((User.username == username) | (User.email == email)).first()
    if existing_user:
        logger.warning(f"User already exists: {username} or {email}")
        return jsonify({'success': False, 'error': 'Username or email already exists'}), 400
    
    # Create new user
    user = User(username=username, email=email)
    user.set_password(password)
    
    logger.info(f"Password hash generated: {bool(user.password_hash)}")
    logger.info(f"Password hash length: {len(user.password_hash) if user.password_hash else 0}")
    
    try:
        db.session.add(user)
        db.session.commit()
        logger.info(f"User registered successfully: {username} (ID: {user.id})")
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error registering user: {str(e)}")
        return jsonify({'success': False, 'error': 'Failed to register user'}), 500

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    if not data or not data.get('username') or not data.get('password'):
        return jsonify({'success': False, 'error': 'Missing fields'}), 400
    
    username = data['username']
    password = data['password']
    
    logger.info(f"Login attempt for username: {username}")
    
    user = User.query.filter_by(username=username).first()
    
    if not user:
        logger.warning(f"User not found: {username}")
        return jsonify({'success': False, 'error': 'Invalid credentials'}), 401
    
    logger.info(f"User found: {username} (ID: {user.id})")
    logger.info(f"Password hash exists: {bool(user.password_hash)}")
    
    # Check password
    password_valid = user.check_password(password)
    logger.info(f"Password check result: {password_valid}")
    
    if password_valid:
        logger.info(f"Login successful for user: {username}")
        return jsonify({'success': True, 'user': {'id': user.id, 'username': user.username, 'email': user.email}})
    else:
        logger.warning(f"Invalid password for user: {username}")
        return jsonify({'success': False, 'error': 'Invalid credentials'}), 401

@app.route('/api/change_password', methods=['POST'])
def change_password():
    data = request.json
    if not data or not data.get('username') or not data.get('old_password') or not data.get('new_password'):
        return jsonify({'success': False, 'error': 'Missing fields'}), 400
    
    # Check password strength
    if not is_strong_password(data['new_password']):
        return jsonify({
            'success': False,
            'error': 'Password must be at least 8 characters with uppercase, lowercase, and numbers'
        }), 400
    
    user = User.query.filter_by(username=data['username']).first()
    if not user or not user.check_password(data['old_password']):
        return jsonify({'success': False, 'error': 'Old password is incorrect'}), 401
    
    user.set_password(data['new_password'])
    db.session.commit()
    return jsonify({'success': True})

@app.route('/api/reset_password', methods=['POST'])
def reset_password():
    data = request.json
    email = data.get('email')
    if not email:
        return jsonify({'success': False, 'error': 'Missing email'}), 400
    
    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({'success': False, 'error': 'User not found'}), 404
    
    # Implement actual password reset logic here
    # (Send email with reset token, etc.)
    
    return jsonify({'success': True, 'message': 'Password reset instructions sent'})

@app.route('/api/users', methods=['GET'])
def get_user_count():
    count = User.query.count()
    return jsonify({'count': count})

@app.route('/api/debug/pesapal-config', methods=['GET'])
def debug_pesapal_config():
    """Debug endpoint to check PesaPal configuration (for development only)"""
    try:
        config_info = {
            'pesapal_base_url': app.config.get('PESAPAL_BASE_URL'),
            'consumer_key_exists': bool(app.config.get('PESAPAL_CONSUMER_KEY')),
            'consumer_secret_exists': bool(app.config.get('PESAPAL_CONSUMER_SECRET')),
            'notification_id': app.config.get('PESAPAL_NOTIFICATION_ID'),
            'callback_url': 'https://books-management-system-bcr5.onrender.com/api/pesapal-callback'
        }
        
        # Test PesaPal connectivity if credentials are configured
        if app.config.get('PESAPAL_CONSUMER_KEY') and app.config.get('PESAPAL_CONSUMER_SECRET'):
            try:
                logger.info("Testing PesaPal connectivity...")
                access_token = get_pesapal_token()
                config_info['pesapal_connectivity'] = 'SUCCESS'
                config_info['access_token_received'] = bool(access_token)
            except Exception as e:
                config_info['pesapal_connectivity'] = 'FAILED'
                config_info['connectivity_error'] = str(e)
        else:
            config_info['pesapal_connectivity'] = 'NOT_CONFIGURED'
        
        return jsonify(config_info)
        
    except Exception as e:
        logger.error(f"Error in debug endpoint: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/pay', methods=['POST'])
def pay():
    """PesaPal v3 API payment endpoint"""
    try:
        logger.info("=== PESAPAL PAYMENT REQUEST START ===")
        
        # Validate request data
        data = request.get_json()
        if not data:
            logger.error("No JSON data provided in payment request")
            return jsonify({'error': 'No data provided'}), 400
        
        logger.info(f"Payment request data: {data}")
        
        # Extract and validate payment data
        resource_id = data.get('resource_id')
        email = data.get('email')
        amount = data.get('amount')
        name = data.get('name')
        phone = data.get('phone')
        
        # Detailed validation with specific error messages
        missing_fields = []
        if not resource_id:
            missing_fields.append('resource_id')
        if not email:
            missing_fields.append('email')
        if not amount:
            missing_fields.append('amount')
        if not name:
            missing_fields.append('name')
        if not phone:
            missing_fields.append('phone')
        
        if missing_fields:
            error_msg = f"Missing required fields: {', '.join(missing_fields)}"
            logger.error(f"Payment validation failed: {error_msg}")
            return jsonify({'error': error_msg}), 400
        
        # Validate amount format
        try:
            amount_float = float(amount)
            if amount_float <= 0:
                logger.error(f"Invalid amount: {amount} (must be positive)")
                return jsonify({'error': 'Amount must be a positive number'}), 400
        except (ValueError, TypeError):
            logger.error(f"Invalid amount format: {amount}")
            return jsonify({'error': 'Amount must be a valid number'}), 400
        
        # Validate email format
        if '@' not in email or '.' not in email:
            logger.error(f"Invalid email format: {email}")
            return jsonify({'error': 'Invalid email format'}), 400
        
        # Check if resource exists
        resource = Resource.query.get(resource_id)
        if not resource:
            logger.error(f"Resource not found: {resource_id}")
            return jsonify({'error': 'Resource not found'}), 404
        
        logger.info(f"Resource found: {resource.title} (ID: {resource_id})")
        
        # Generate order tracking ID
        order_tracking_id = f"ORDER_{int(time.time())}_{random.randint(1000, 9999)}"
        logger.info(f"Generated order tracking ID: {order_tracking_id}")
        
        # Check PesaPal configuration
        pesapal_key = app.config['PESAPAL_CONSUMER_KEY']
        pesapal_secret = app.config['PESAPAL_CONSUMER_SECRET']
        pesapal_base_url = app.config['PESAPAL_BASE_URL']
        
        if not pesapal_key or not pesapal_secret:
            logger.warning("PesaPal credentials not configured, using test mode")
            payment = create_payment_record(
                order_tracking_id=order_tracking_id,
                resource_id=resource_id,
                user_email=email,
                amount=amount,
                status='COMPLETED'
            )
            db.session.add(payment)
            db.session.commit()
            return jsonify({
                'success': True,
                'orderTrackingId': order_tracking_id,
                'redirectUrl': f"https://books-management-system-bcr5.onrender.com/user/download-success.html?resource_id={resource_id}&email={email}&orderTrackingId={order_tracking_id}",
                'message': 'Test payment successful (PesaPal not configured)'
            })
        
        # Get PesaPal access token
        try:
            logger.info("Requesting PesaPal access token...")
            access_token = get_pesapal_token()
            logger.info("PesaPal access token received successfully")
        except Exception as e:
            logger.error(f"Failed to get PesaPal access token: {str(e)}")
            return jsonify({'error': f'Payment service temporarily unavailable: {str(e)}'}), 503
        
        # Prepare PesaPal order request
        order_url = f"{pesapal_base_url}/Transactions/SubmitOrderRequest"
        
        # Parse name into first and last name
        name_parts = name.split()
        first_name = name_parts[0] if name_parts else 'User'
        last_name = name_parts[-1] if len(name_parts) > 1 else 'User'
        
        pesapal_order = {
            'id': order_tracking_id,
            'currency': 'KES',
            'amount': amount_float,
            'description': f"Purchase: {resource.title}",
            'callback_url': 'https://books-management-system-bcr5.onrender.com/api/pesapal-callback',
            'notification_id': app.config.get('PESAPAL_NOTIFICATION_ID', '4ad16ada-f09b-4b45-8c18-db86b60a879d'),
            'billing_address': {
                'email_address': email,
                'phone_number': phone,
                'country_code': 'KE',
                'first_name': first_name,
                'last_name': last_name
            }
        }
        
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        
        logger.info(f"PesaPal order URL: {order_url}")
        logger.info(f"PesaPal order data: {pesapal_order}")
        logger.info(f"Request headers: {headers}")
        
        # Submit order to PesaPal
        try:
            logger.info("Submitting order to PesaPal...")
            order_resp = requests.post(order_url, json=pesapal_order, headers=headers, timeout=30)
            
            logger.info(f"PesaPal order response status: {order_resp.status_code}")
            logger.info(f"PesaPal order response headers: {dict(order_resp.headers)}")
            logger.info(f"PesaPal order response body: {order_resp.text}")
            
        except requests.exceptions.Timeout:
            logger.error("PesaPal order request timed out")
            return jsonify({'error': 'Payment service request timed out'}), 503
        except requests.exceptions.ConnectionError as e:
            logger.error(f"Connection error during PesaPal order request: {str(e)}")
            return jsonify({'error': f'Unable to connect to payment service: {str(e)}'}), 503
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error during PesaPal order request: {str(e)}")
            return jsonify({'error': f'Payment service request failed: {str(e)}'}), 503
        
        # Handle PesaPal response
        if order_resp.status_code != 200:
            error_details = {
                'status_code': order_resp.status_code,
                'response_text': order_resp.text,
                'response_headers': dict(order_resp.headers)
            }
            logger.error(f"PesaPal order request failed: {error_details}")
            
            # Try to extract detailed error from PesaPal response
            try:
                error_json = order_resp.json()
                error_message = error_json.get('error', error_json.get('message', error_json.get('error_description', order_resp.text)))
                error_code = error_json.get('error_code', 'UNKNOWN')
                logger.error(f"PesaPal error code: {error_code}, message: {error_message}")
            except json.JSONDecodeError:
                error_message = order_resp.text
                logger.error(f"Could not parse PesaPal error response as JSON: {order_resp.text}")
            
            return jsonify({
                'error': f'Payment service error: {error_message}',
                'status_code': order_resp.status_code,
                'details': error_details
            }), 500
        
        # Parse successful response
        try:
            order_response = order_resp.json()
            logger.info(f"PesaPal order response parsed: {order_response}")
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse PesaPal order response as JSON: {order_resp.text}")
            return jsonify({'error': f'Invalid response from payment service: {str(e)}'}), 500
        
        # Validate response structure
        if 'order_tracking_id' not in order_response:
            logger.error(f"Missing order_tracking_id in PesaPal response: {order_response}")
            return jsonify({'error': f'Invalid response from payment service: missing order_tracking_id'}), 500
        
        # Create payment record
        try:
            payment = create_payment_record(
                order_tracking_id=order_tracking_id,
                resource_id=resource_id,
                user_email=email,
                amount=amount
            )
            db.session.add(payment)
            db.session.commit()
            logger.info(f"Payment record created successfully: {order_tracking_id}")
        except Exception as e:
            logger.error(f"Failed to create payment record: {str(e)}")
            db.session.rollback()
            return jsonify({'error': f'Failed to create payment record: {str(e)}'}), 500
        
        # Prepare response
        redirect_url = order_response.get('redirect_url')
        if not redirect_url:
            redirect_url = f"https://books-management-system-bcr5.onrender.com/user/download-success.html?resource_id={resource_id}&email={email}&orderTrackingId={order_tracking_id}"
            logger.warning(f"No redirect_url in PesaPal response, using fallback: {redirect_url}")
        
        logger.info(f"Payment initiated successfully. Redirect URL: {redirect_url}")
        logger.info("=== PESAPAL PAYMENT REQUEST END ===")
        
        return jsonify({
            'success': True,
            'orderTrackingId': order_tracking_id,
            'payment_url': redirect_url,  # Changed from redirectUrl to payment_url
            'redirectUrl': redirect_url,  # Keep for backward compatibility
            'message': 'Payment initiated successfully'
        })
        
    except Exception as e:
        logger.exception(f"Unexpected error in payment endpoint: {str(e)}")
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500

@app.route('/api/pesapal-callback', methods=['POST'])
def pesapal_callback():
    """Handle PesaPal IPN (Instant Payment Notification)"""
    try:
        logger.info("PesaPal callback received")
        data = request.json
        logger.info(f"Callback data: {data}")
        
        # Extract payment information
        order_tracking_id = data.get('order_tracking_id')
        transaction_tracking_id = data.get('transaction_tracking_id')
        payment_status = data.get('payment_status')
        
        if not order_tracking_id:
            logger.error("No order_tracking_id in callback")
            return jsonify({'error': 'Missing order_tracking_id'}), 400
        
        # Find the payment record
        payment = Payment.query.filter_by(order_tracking_id=order_tracking_id).first()
        if not payment:
            logger.error(f"Payment record not found for order: {order_tracking_id}")
            return jsonify({'error': 'Payment record not found'}), 404
        
        # Update payment status
        if payment_status == 'COMPLETED':
            payment.status = 'COMPLETED'
            payment.transaction_tracking_id = transaction_tracking_id
            payment.ipn_received = True
            payment.ipn_received_at = datetime.utcnow()
            db.session.commit()
            logger.info(f"Payment completed: {order_tracking_id}")
        elif payment_status in ['FAILED', 'CANCELLED']:
            payment.status = payment_status
            payment.ipn_received = True
            payment.ipn_received_at = datetime.utcnow()
            db.session.commit()
            logger.info(f"Payment {payment_status}: {order_tracking_id}")
        
        return jsonify({'success': True, 'message': 'Callback processed'})
        
    except Exception as e:
        logger.exception('Error processing PesaPal callback: %s', str(e))
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/check-payment', methods=['GET'])
def check_payment():
    """Check payment status for a resource and email"""
    try:
        resource_id = request.args.get('resource_id')
        email = request.args.get('email')
        
        if not resource_id or not email:
            return jsonify({'error': 'Missing resource_id or email'}), 400
        
        # Find the most recent payment for this resource and email
        payment = Payment.query.filter_by(
            resource_id=resource_id,
            user_email=email
        ).order_by(Payment.created_at.desc()).first()
        
        if not payment:
            return jsonify({'error': 'Payment record not found'}), 404
        
        return jsonify({
            'success': True,
            'payment_status': payment.status,
            'order_tracking_id': payment.order_tracking_id,
            'amount': payment.amount,
            'created_at': payment.created_at.isoformat() if payment.created_at else None
        })
        
    except Exception as e:
        logger.exception('Error checking payment: %s', str(e))
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/download/<int:resource_id>', methods=['GET'])
def download_resource(resource_id):
    email = request.args.get('email')
    order_tracking_id = request.args.get('orderTrackingId')
    
    if not email or not order_tracking_id:
        return abort(403, 'Missing email or orderTrackingId')
    
    # Find payment record
    payment = Payment.query.filter_by(
        order_tracking_id=order_tracking_id,
        user_email=email,
        resource_id=resource_id
    ).first()
    
    if not payment:
        return abort(403, 'Payment record not found')
    
    # Check if payment is completed
    if payment.status != 'COMPLETED':
        return abort(403, f'Payment not completed. Status: {payment.status}')
    
    # Get resource
    resource = Resource.query.get(resource_id)
    if not resource:
        return abort(404, 'Resource not found')
    
    # Send the file (for demo, using a test PDF)
    test_pdf_path = os.path.join(os.path.dirname(__file__), 'static', 'test.pdf')
    if not os.path.exists(test_pdf_path):
        return abort(404, 'Resource file not found')
    
    logger.info(f"Resource downloaded: Resource {resource_id}, User {email}, Order {order_tracking_id}")
    return send_file(test_pdf_path, as_attachment=True, download_name=f'{resource.title}.pdf')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        ensure_admin_user()
    app.run(debug=True)
update this with the fixes
