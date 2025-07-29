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

# Configure logging
logging.basicConfig(level=logging.INFO)
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

def get_pesapal_token():
    """Get PesaPal access token"""
    try:
        logger.info("Attempting to get PesaPal token")
        auth_url = f"{app.config['PESAPAL_BASE_URL']}/Auth/RequestToken"
        
        auth_data = {
            'consumer_key': app.config['PESAPAL_CONSUMER_KEY'],
            'consumer_secret': app.config['PESAPAL_CONSUMER_SECRET']
        }
        
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        
        auth_resp = requests.post(auth_url, json=auth_data, headers=headers, timeout=30)
        logger.info(f"PesaPal auth response status: {auth_resp.status_code}")
        
        if not auth_resp.ok:
            logger.error(f"Failed to authenticate with PesaPal: {auth_resp.text}")
            raise Exception(f"Failed to authenticate with PesaPal: {auth_resp.text}")
        
        auth_json = auth_resp.json()
        token = auth_json.get('token')
        if not token:
            raise Exception("No access token received from PesaPal")
        
        logger.info("PesaPal token received successfully")
        return token
    except Exception as e:
        logger.error(f"Error getting PesaPal token: {str(e)}")
        raise

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
        books = Resource.query.filter_by(resource_type='book').all()
        papers = Resource.query.filter_by(resource_type='paper').all()
        setbooks = Resource.query.filter_by(resource_type='setbook').all()
        
        return jsonify({
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
    user = User.query.filter_by(username=data['username']).first()
    if not user or not user.check_password(data['old_password']):
        return jsonify({'success': False, 'error': 'Old password is incorrect'}), 401
    user.set_password(data['new_password'])
    db.session.commit()
    return jsonify({'success': True})

@app.route('/api/users', methods=['GET'])
def get_user_count():
    count = User.query.count()
    return jsonify({'count': count})

@app.route('/api/pay', methods=['POST'])
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
        
        logger.info(f"PesaPal key exists: {bool(pesapal_key)}")
        logger.info(f"PesaPal secret exists: {bool(pesapal_secret)}")
        logger.info(f"PesaPal base URL: {pesapal_base_url}")
        
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
        return_url = (
            'http://localhost:5500/user/auto-download.html'
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
            'callback_url': 'http://localhost:5000/api/pesapal-callback',
            'notification_id': '',
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
        
        # Store payment record
        payment = create_payment_record(order_tracking_id, resource_id, user_email, amount, 'PENDING')
        
        logger.info(f"Payment initiated: Order ID {order_tracking_id}, Resource {resource_id}, Email {user_email}")
        
        return jsonify({
            'success': True,
            'payment_url': payment_url, 
            'orderTrackingId': order_tracking_id,
            'payment_id': payment.id
        })
        
    except Exception as e:
        print('Unexpected error in /api/pay:', str(e))  # Print error to terminal
        logger.exception('Unexpected error in /api/pay: %s', str(e))
        return jsonify({'error': 'Internal server error'}), 500

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