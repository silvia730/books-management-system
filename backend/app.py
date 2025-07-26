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
    auth_url = f"{app.config['PESAPAL_BASE_URL']}/Auth/RequestToken"
    auth_resp = requests.post(auth_url, json={
        'consumer_key': app.config['PESAPAL_CONSUMER_KEY'],
        'consumer_secret': app.config['PESAPAL_CONSUMER_SECRET']
    })
    if not auth_resp.ok:
        logger.error(f"Failed to authenticate with PesaPal: {auth_resp.text}")
        raise Exception("Failed to authenticate with PesaPal")
    return auth_resp.json().get('token')

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
    books = Resource.query.filter_by(resource_type='book').all()
    papers = Resource.query.filter_by(resource_type='paper').all()
    setbooks = Resource.query.filter_by(resource_type='setbook').all()
    return jsonify({
        'books': [b.to_dict() for b in books],
        'papers': [p.to_dict() for p in papers],
        'setbooks': [s.to_dict() for s in setbooks]
    })

@app.route('/api/resource/<int:resource_id>', methods=['DELETE'])
def delete_resource(resource_id):
    resource = Resource.query.get(resource_id)
    if not resource:
        return jsonify({'success': False, 'error': 'Resource not found'}), 404
    db.session.delete(resource)
    db.session.commit()
    return jsonify({'success': True})

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
    try:
        data = request.json
        resource_id = data.get('resource_id')
        user_email = data.get('email')
        amount = data.get('amount', 100)  # Default to 100 KES
        name = data.get('name', '')
        phone = data.get('phone', '')
        
        # Validate resource exists
        resource = Resource.query.get(resource_id)
        if not resource:
            return jsonify({'error': 'Resource not found'}), 404
        
        # Get PesaPal credentials
        pesapal_key = app.config['PESAPAL_CONSUMER_KEY']
        pesapal_secret = app.config['PESAPAL_CONSUMER_SECRET']
        if not pesapal_key or not pesapal_secret:
            logger.error('PesaPal credentials missing')
            return jsonify({'error': 'PesaPal credentials not configured'}), 500
        
        # Get access token
        try:
            access_token = get_pesapal_token()
        except Exception as e:
            logger.error(f"Failed to get PesaPal token: {str(e)}")
            return jsonify({'error': 'Payment service unavailable'}), 503
        
        # Create order
        order_url = f"{app.config['PESAPAL_BASE_URL']}/Transactions/SubmitOrderRequest"
        headers = {'Authorization': f'Bearer {access_token}'}
        
        # Compose return_url for auto-download
        base_url = app.config['API_BASE_URL'].replace('/api', '')
        return_url = (
            f'{base_url}/user/auto-download.html'
            f'?resource_id={resource_id}'
            f'&email={user_email}'
            f'&name={name}'
            f'&phone={phone}'
        )
        
        order_data = {
            'id': str(resource_id),
            'currency': 'KES',
            'amount': amount,
            'description': f'Download: {resource.title}',
            'callback_url': f"{app.config['API_BASE_URL']}/pesapal-callback",
            'notification_id': app.config['PESAPAL_NOTIFICATION_ID'],
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
        
        order_resp = requests.post(order_url, json=order_data, headers=headers)
        if not order_resp.ok:
            logger.error(f'Failed to create PesaPal order: {order_resp.text}')
            return jsonify({'error': 'Failed to create payment order'}), 500
        
        order_response = order_resp.json()
        payment_url = order_response.get('redirect_url')
        order_tracking_id = order_response.get('order_tracking_id')
        
        # Store payment record
        payment = Payment(
            order_tracking_id=order_tracking_id,
            resource_id=resource_id,
            user_email=user_email,
            amount=amount,
            status='PENDING'
        )
        db.session.add(payment)
        db.session.commit()
        
        logger.info(f"Payment initiated: Order ID {order_tracking_id}, Resource {resource_id}, Email {user_email}")
        
        return jsonify({
            'payment_url': payment_url, 
            'orderTrackingId': order_tracking_id,
            'payment_id': payment.id
        })
        
    except Exception as e:
        logger.exception('Unexpected error in /api/pay: %s', str(e))
        return jsonify({'error': 'Internal server error'}), 500

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

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        ensure_admin_user()
    app.run(debug=True) 