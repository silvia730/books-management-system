from flask import Flask, request, jsonify, send_file, abort
from flask_cors import CORS
from models import db, Resource, User, Payment
from config import Config
import requests
import os
import logging
import hashlib
import hmac
import time
import uuid
from datetime import datetime
from flask_migrate import Migrate
from functools import wraps
import json

# Configure logging
logging.basicConfig(
    level=getattr(logging, Config.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(Config.LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config.from_object(Config)
CORS(app)
db.init_app(app)
migrate = Migrate(app, db)

# Rate limiting decorator
def rate_limit(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if app.config['RATE_LIMIT_ENABLED']:
            # Simple rate limiting - in production, use Redis or similar
            client_ip = request.remote_addr
            # This is a basic implementation - consider using Flask-Limiter for production
            pass
        return f(*args, **kwargs)
    return decorated_function

# Security middleware
@app.before_request
def security_middleware():
    # Check allowed hosts
    if app.config['ALLOWED_HOSTS'] != ['*']:
        client_host = request.headers.get('Host', '').split(':')[0]
        if client_host not in app.config['ALLOWED_HOSTS']:
            logger.warning(f"Unauthorized access attempt from host: {client_host}")
            abort(403)
    
    # Log all requests for debugging
    logger.info(f"{request.method} {request.path} from {request.remote_addr}")

def ensure_admin_user():
    admin = User.query.filter_by(username='admin').first()
    if not admin:
        admin = User(username='admin', email='admin@somafy.co.ke')
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()

def get_pesapal_token():
    """Get PesaPal access token with caching"""
    try:
        logger.info("Attempting to get PesaPal token")
    auth_url = f"{app.config['PESAPAL_BASE_URL']}/Auth/RequestToken"
        logger.info(f"Auth URL: {auth_url}")
        
        auth_data = {
        'consumer_key': app.config['PESAPAL_CONSUMER_KEY'],
        'consumer_secret': app.config['PESAPAL_CONSUMER_SECRET']
        }
        logger.info(f"Auth data keys: {list(auth_data.keys())}")
        
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        
        auth_resp = requests.post(auth_url, json=auth_data, headers=headers, timeout=30)
        logger.info(f"PesaPal auth response status: {auth_resp.status_code}")
        logger.info(f"PesaPal auth response: {auth_resp.text}")
        
    if not auth_resp.ok:
        logger.error(f"Failed to authenticate with PesaPal: {auth_resp.text}")
            raise Exception(f"Failed to authenticate with PesaPal: {auth_resp.text}")
        
        try:
            auth_json = auth_resp.json()
        except Exception as e:
            logger.error(f"Failed to parse auth response as JSON: {auth_resp.text}")
            raise Exception(f"Invalid response from PesaPal auth: {auth_resp.text}")
        
        token = auth_json.get('token')
        if not token:
            logger.error(f"No token in auth response: {auth_json}")
            raise Exception("No access token received from PesaPal")
        
        logger.info(f"PesaPal token received successfully")
        return token
    except Exception as e:
        logger.error(f"Error getting PesaPal token: {str(e)}")
        raise

def generate_unique_order_id():
    """Generate a unique order tracking ID"""
    return str(uuid.uuid4())

def create_payment_record(order_tracking_id, resource_id, user_email, amount, status='PENDING'):
    """Create a payment record with retry logic for duplicate order_tracking_id"""
    max_retries = 5
    for attempt in range(max_retries):
        try:
            payment = Payment(
                order_tracking_id=order_tracking_id,
                resource_id=resource_id,
                user_email=user_email,
                amount=amount,
                status=status
                # currency will use default value from model
            )
            db.session.add(payment)
            db.session.commit()
            logger.info(f"Payment record created successfully: {order_tracking_id}")
            return payment
        except Exception as e:
            if "Duplicate entry" in str(e) and "order_tracking_id" in str(e) and attempt < max_retries - 1:
                logger.warning(f"Duplicate order_tracking_id detected, retrying with new UUID: {order_tracking_id}")
                db.session.rollback()
                order_tracking_id = generate_unique_order_id()
            else:
                logger.error(f"Failed to create payment record: {str(e)}")
                db.session.rollback()
                raise

@app.route('/')
def index():
    return "Welcome to the Books Management System API!"

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
            import os
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
        # Get filter parameters
        class_grade = request.args.get('class')
        subject = request.args.get('subject')
        
        # Build query
        query = Resource.query
        
        if class_grade:
            query = query.filter(Resource.class_grade.ilike(f'%{class_grade}%'))
        if subject:
            query = query.filter(Resource.subject.ilike(f'%{subject}%'))
        
        # Get all resources with filters
        all_resources = query.all()
        
        # Group by resource type
        books = [r for r in all_resources if r.resource_type == 'book']
        papers = [r for r in all_resources if r.resource_type == 'paper']
        setbooks = [r for r in all_resources if r.resource_type == 'setbook']
        
        return jsonify({
            'books': [b.to_dict() for b in books],
            'papers': [p.to_dict() for p in papers],
            'setbooks': [s.to_dict() for s in setbooks],
            'all': [r.to_dict() for r in all_resources]  # Add all resources for the new page
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
        
        # Check if there are any payments for this resource
        payments = Payment.query.filter_by(resource_id=resource_id).first()
        if payments:
            return jsonify({'success': False, 'error': 'Cannot delete resource with existing payments'}), 400
        
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
    # Check for existing username or email
    if User.query.filter((User.username == data['username']) | (User.email == data['email'])).first():
        return jsonify({'success': False, 'error': 'Username or email already exists'}), 400
    user = User(username=data['username'], email=data['email'])
    user.set_password(data['password'])
    db.session.add(user)
    db.session.commit()
    return jsonify({'success': True})

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    if not data or not data.get('username') or not data.get('password'):
        return jsonify({'success': False, 'error': 'Missing fields'}), 400
    user = User.query.filter_by(username=data['username']).first()
    if user and user.check_password(data['password']):
        return jsonify({'success': True, 'user': {'id': user.id, 'username': user.username, 'email': user.email}})
    return jsonify({'success': False, 'error': 'Invalid credentials'}), 401

@app.route('/api/change_password', methods=['POST'])
def change_password():
    data = request.json
    if not data or not data.get('username') or not data.get('old_password') or not data.get('new_password'):
        return jsonify({'success': False, 'error': 'Missing fields'}), 400
    from models import User
    user = User.query.filter_by(username=data['username']).first()
    if not user or not user.check_password(data['old_password']):
        return jsonify({'success': False, 'error': 'Old password is incorrect'}), 401
    user.set_password(data['new_password'])
    db.session.commit()
    return jsonify({'success': True})

@app.route('/api/users', methods=['GET'])
def get_user_count():
    from models import User
    count = User.query.count()
    return jsonify({'count': count})

@app.route('/api/pay', methods=['POST'])
@rate_limit
def pay():
    """PesaPal v3 API payment endpoint"""
    try:
        logger.info("Payment request received")
        data = request.json
        logger.info(f"Payment data: {data}")
        
        # Validate required fields
        required_fields = ['resource_id', 'email', 'name', 'phone']
        missing_fields = [field for field in required_fields if not data.get(field)]
        if missing_fields:
            logger.error(f"Missing required fields: {missing_fields}")
            return jsonify({'error': f'Missing required fields: {", ".join(missing_fields)}'}), 400
        
        resource_id = data.get('resource_id')
        user_email = data.get('email')
        amount = data.get('amount', 100)  # Default to 100 KES
        name = data.get('name', '')
        phone = data.get('phone', '')
        
        logger.info(f"Processing payment for resource {resource_id}, email {user_email}, amount {amount}")
        
        # Validate resource exists
        resource = Resource.query.get(resource_id)
        if not resource:
            logger.error(f"Resource {resource_id} not found")
            return jsonify({'error': 'Resource not found'}), 404
        
        logger.info(f"Resource found: {resource.title}")
        
        # Get PesaPal credentials
        pesapal_key = app.config['PESAPAL_CONSUMER_KEY']
        pesapal_secret = app.config['PESAPAL_CONSUMER_SECRET']
        pesapal_base_url = app.config['PESAPAL_BASE_URL']
        notification_id = app.config['PESAPAL_NOTIFICATION_ID']
        
        logger.info(f"PesaPal key exists: {bool(pesapal_key)}")
        logger.info(f"PesaPal secret exists: {bool(pesapal_secret)}")
        logger.info(f"PesaPal base URL: {pesapal_base_url}")
        logger.info(f"Notification ID: {notification_id}")
        
        # Check if PesaPal credentials are available
        if not pesapal_key or not pesapal_secret:
            logger.warning('PesaPal credentials missing - using test payment mode')
            # Create a test payment instead
            test_order_id = f"test_{generate_unique_order_id()}"
            payment = create_payment_record(test_order_id, resource_id, user_email, amount, 'COMPLETED')
            
            logger.info(f"Test payment created: {test_order_id}")
            
            return jsonify({
                'success': True,
                'message': 'Test payment successful (PesaPal not configured)',
                'orderTrackingId': test_order_id,
                'payment_id': payment.id,
                'payment_url': None
            })
        
        # Get access token
        try:
            access_token = get_pesapal_token()
            logger.info("PesaPal access token obtained successfully")
        except Exception as e:
            logger.error(f"Failed to get PesaPal token: {str(e)}")
            return jsonify({'error': f'Payment service unavailable: {str(e)}'}), 503
        
        # Create order using PesaPal v3 API
        order_url = f"{pesapal_base_url}/Transactions/SubmitOrderRequest"
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        
        # Compose return_url for auto-download
        base_url = app.config['API_BASE_URL'].replace('/api', '')
        return_url = (
            f'{base_url}/user/auto-download.html'
            f'?resource_id={resource_id}'
            f'&email={user_email}'
            f'&name={name}'
            f'&phone={phone}'
        )
        
        # PesaPal v3 API order data structure
        order_data = {
            'id': str(resource_id),
            'currency': 'KES',
            'amount': amount,
            'description': f'Download: {resource.title}',
            'callback_url': f"{app.config['API_BASE_URL']}/pesapal-callback",
            'notification_id': notification_id,
            'billing_address': {
                'email_address': user_email,
                'phone_number': phone,
                'first_name': name,
                'last_name': '',
                'line_1': '',
                'city': '',
                'state': '',
                'postal_code': '',
                'country_code': 'KE'
            },
            'return_url': return_url
        }
        
        logger.info(f"Submitting order to PesaPal: {order_url}")
        logger.info(f"Order data: {order_data}")
        
        order_resp = requests.post(order_url, json=order_data, headers=headers, timeout=30)
        logger.info(f"PesaPal response status: {order_resp.status_code}")
        logger.info(f"PesaPal response: {order_resp.text}")
        
        if not order_resp.ok:
            logger.error(f'Failed to create PesaPal order: {order_resp.text}')
            return jsonify({'error': f'Failed to create payment order: {order_resp.text}'}), 500
        
        try:
        order_response = order_resp.json()
        except Exception as e:
            logger.error(f"Failed to parse PesaPal response as JSON: {order_resp.text}")
            return jsonify({'error': 'Invalid response from payment service'}), 500
        
        payment_url = order_response.get('redirect_url')
        order_tracking_id = order_response.get('order_tracking_id')
        
        if not payment_url or not order_tracking_id:
            logger.error(f"Missing payment_url or order_tracking_id in response: {order_response}")
            return jsonify({'error': 'Invalid response from payment service'}), 500
        
        # Store payment record using the safe creation function
        payment = create_payment_record(order_tracking_id, resource_id, user_email, amount, 'PENDING')
        
        logger.info(f"Payment initiated: Order ID {order_tracking_id}, Resource {resource_id}, Email {user_email}")
        
        return jsonify({
            'success': True,
            'payment_url': payment_url, 
            'orderTrackingId': order_tracking_id,
            'payment_id': payment.id
        })
        
    except Exception as e:
        logger.exception('Unexpected error in /api/pay: %s', str(e))
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500

@app.route('/api/test-pay', methods=['POST'])
def test_pay():
    """Test payment endpoint without PesaPal integration"""
    try:
        logger.info("Test payment request received")
        data = request.json
        logger.info(f"Test payment data: {data}")
        
        resource_id = data.get('resource_id')
        user_email = data.get('email')
        amount = data.get('amount', 100)
        name = data.get('name', '')
        phone = data.get('phone', '')
        
        # Validate resource exists
        resource = Resource.query.get(resource_id)
        if not resource:
            return jsonify({'error': 'Resource not found'}), 404
        
        # Create a test payment record
        test_order_id = f"test_{generate_unique_order_id()}"
        payment = create_payment_record(test_order_id, resource_id, user_email, amount, 'COMPLETED')
        
        logger.info(f"Test payment created: {test_order_id}")
        
        return jsonify({
            'success': True,
            'message': 'Test payment successful',
            'orderTrackingId': test_order_id,
            'payment_id': payment.id
        })
        
    except Exception as e:
        logger.exception(f"Test payment error: {str(e)}")
        return jsonify({'error': f'Test payment failed: {str(e)}'}), 500

@app.route('/api/pesapal/ipn', methods=['GET', 'POST'])
@rate_limit
def pesapal_ipn():
    """
    PesaPal IPN (Instant Payment Notification) endpoint
    Handles payment status updates from PesaPal
    """
    try:
        # Log the incoming IPN
        logger.info(f"IPN received from {request.remote_addr}")
        logger.info(f"IPN Headers: {dict(request.headers)}")
        logger.info(f"IPN Query Params: {dict(request.args)}")
        logger.info(f"IPN Body: {request.get_data(as_text=True)}")
        
        # Extract IPN parameters
        transaction_tracking_id = request.args.get('transaction_tracking_id')
        merchant_reference = request.args.get('merchant_reference')
        status = request.args.get('status')
        
        # Validate required parameters
        if not transaction_tracking_id or not merchant_reference or not status:
            logger.error(f"Missing required IPN parameters: transaction_tracking_id={transaction_tracking_id}, merchant_reference={merchant_reference}, status={status}")
            return jsonify({'error': 'Missing required parameters'}), 400
        
        # Find the payment record
        payment = Payment.query.filter_by(order_tracking_id=merchant_reference).first()
        if not payment:
            logger.error(f"Payment not found for merchant_reference: {merchant_reference}")
            return jsonify({'error': 'Payment not found'}), 404
        
        # Verify payment status with PesaPal API
        try:
            access_token = get_pesapal_token()
            status_url = f"{app.config['PESAPAL_BASE_URL']}/Transactions/GetTransactionStatus?orderTrackingId={merchant_reference}"
            headers = {'Authorization': f'Bearer {access_token}'}
            
            status_resp = requests.get(status_url, headers=headers)
            if not status_resp.ok:
                logger.error(f"Failed to verify payment status: {status_resp.text}")
                return jsonify({'error': 'Failed to verify payment'}), 500
            
            api_status = status_resp.json()
            api_payment_status = api_status.get('payment_status')
            api_transaction_id = api_status.get('transaction_tracking_id')
            
            logger.info(f"PesaPal API Status: {api_status}")
            
            # Update payment record
            payment.transaction_tracking_id = api_transaction_id or transaction_tracking_id
            payment.merchant_reference = merchant_reference
            payment.status = api_payment_status or status
            payment.payment_method = api_status.get('payment_method', '')
            payment.ipn_received = True
            payment.ipn_received_at = datetime.utcnow()
            payment.updated_at = datetime.utcnow()
            
            db.session.commit()
            
            logger.info(f"Payment updated: Order {merchant_reference}, Status: {payment.status}")
            
            # Return success response to PesaPal
            return jsonify({'status': 'success'}), 200
            
        except Exception as e:
            logger.exception(f"Error verifying payment with PesaPal API: {str(e)}")
            return jsonify({'error': 'Payment verification failed'}), 500
            
    except Exception as e:
        logger.exception(f"Unexpected error in IPN handler: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/payments', methods=['GET'])
def get_payments():
    """Get all payments for admin dashboard"""
    payments = Payment.query.order_by(Payment.created_at.desc()).all()
    return jsonify({
        'payments': [payment.to_dict() for payment in payments]
    })

@app.route('/api/payment/<order_tracking_id>', methods=['GET'])
def get_payment_status(order_tracking_id):
    """Get payment status by order tracking ID"""
    payment = Payment.query.filter_by(order_tracking_id=order_tracking_id).first()
    if not payment:
        return jsonify({'error': 'Payment not found'}), 404
    
    return jsonify(payment.to_dict())

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

@app.route('/api/config', methods=['GET'])
def get_config():
    return jsonify({'API_BASE_URL': f"{app.config['API_BASE_URL']}/api"})

@app.route('/api/debug-config', methods=['GET'])
def debug_config():
    """Debug endpoint to check configuration (without exposing sensitive data)"""
    return jsonify({
        'pesapal_key_exists': bool(app.config.get('PESAPAL_CONSUMER_KEY')),
        'pesapal_secret_exists': bool(app.config.get('PESAPAL_CONSUMER_SECRET')),
        'pesapal_base_url': app.config.get('PESAPAL_BASE_URL'),
        'pesapal_notification_id': app.config.get('PESAPAL_NOTIFICATION_ID'),
        'api_base_url': app.config.get('API_BASE_URL'),
        'db_host': app.config.get('SQLALCHEMY_DATABASE_URI', '').split('@')[1].split('/')[0] if '@' in app.config.get('SQLALCHEMY_DATABASE_URI', '') else 'Not set'
    })

@app.route('/api/debug-pesapal', methods=['GET'])
def debug_pesapal():
    """Debug endpoint to check PesaPal configuration and test connection"""
    try:
        # Check environment variables
        config_status = {
            'pesapal_key_exists': bool(app.config.get('PESAPAL_CONSUMER_KEY')),
            'pesapal_secret_exists': bool(app.config.get('PESAPAL_CONSUMER_SECRET')),
            'pesapal_base_url': app.config.get('PESAPAL_BASE_URL'),
            'pesapal_notification_id': app.config.get('PESAPAL_NOTIFICATION_ID'),
            'api_base_url': app.config.get('API_BASE_URL'),
        }
        
        # Test PesaPal connection if credentials exist
        connection_test = None
        if config_status['pesapal_key_exists'] and config_status['pesapal_secret_exists']:
            try:
                logger.info("Testing PesaPal connection...")
                token = get_pesapal_token()
                connection_test = {
                    'status': 'success',
                    'message': 'Successfully obtained PesaPal access token',
                    'token_exists': bool(token)
                }
            except Exception as e:
                connection_test = {
                    'status': 'error',
                    'message': f'Failed to connect to PesaPal: {str(e)}'
                }
        else:
            connection_test = {
                'status': 'skipped',
                'message': 'PesaPal credentials not configured'
            }
        
        return jsonify({
            'config_status': config_status,
            'connection_test': connection_test,
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.exception(f"Error in debug endpoint: {str(e)}")
        return jsonify({'error': f'Debug endpoint error: {str(e)}'}), 500

@app.route('/api/test-db', methods=['GET'])
def test_database():
    """Test database connection"""
    try:
        # Try to query the database
        user_count = User.query.count()
        return jsonify({
            'status': 'success',
            'message': 'Database connection working',
            'user_count': user_count
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Database connection failed: {str(e)}'
        }), 500

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        ensure_admin_user()
    app.run(debug=True) 