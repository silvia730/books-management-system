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
        
        logger.info(f"Auth URL: {auth_url}")
        logger.info(f"Consumer key exists: {bool(app.config['PESAPAL_CONSUMER_KEY'])}")
        logger.info(f"Consumer secret exists: {bool(app.config['PESAPAL_CONSUMER_SECRET'])}")
        
        auth_resp = requests.post(auth_url, json=auth_data, timeout=30)
        
        logger.info(f"PesaPal auth response status: {auth_resp.status_code}")
        logger.info(f"PesaPal auth response: {auth_resp.text}")
        
        if not auth_resp.ok:
            logger.error(f"Failed to authenticate with PesaPal: {auth_resp.text}")
            raise Exception(f"Failed to authenticate with PesaPal: {auth_resp.text}")
        
        auth_response = auth_resp.json()
        access_token = auth_response.get('token')
        
        if not access_token:
            logger.error("No access token received from PesaPal")
            raise Exception("No access token received from PesaPal")
        
        logger.info("PesaPal token received successfully")
        return access_token
        
    except Exception as e:
        logger.error(f"Error getting PesaPal token: {str(e)}")
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
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        # Extract payment data
        resource_id = data.get('resource_id')
        email = data.get('email')
        amount = data.get('amount')
        name = data.get('name')
        phone = data.get('phone')
        if not all([resource_id, email, amount, name, phone]):
            return jsonify({'error': 'Missing required fields'}), 400
        resource = Resource.query.get(resource_id)
        if not resource:
            return jsonify({'error': 'Resource not found'}), 404
        order_tracking_id = f"ORDER_{int(time.time())}_{random.randint(1000, 9999)}"
        pesapal_key = app.config['PESAPAL_CONSUMER_KEY']
        pesapal_secret = app.config['PESAPAL_CONSUMER_SECRET']
        pesapal_base_url = app.config['PESAPAL_BASE_URL']
        if not pesapal_key or not pesapal_secret:
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
        try:
            access_token = get_pesapal_token()
        except Exception as e:
            return jsonify({'error': f'Payment service temporarily unavailable: {str(e)}'}), 503
        order_url = f"{pesapal_base_url}/Transactions/SubmitOrderRequest"
        pesapal_order = {
            'id': order_tracking_id,
            'currency': 'KES',
            'amount': float(amount),
            'description': f"Purchase: {resource.title}",
            'callback_url': 'https://books-management-system-bcr5.onrender.com/api/pesapal-callback',
            'notification_id': app.config.get('PESAPAL_NOTIFICATION_ID', '4ad16ada-f09b-4b45-8c18-db86b60a879d'),
            'billing_address': {
                'email_address': email,
                'phone_number': phone,
                'country_code': 'KE',
                'first_name': name.split()[0] if name else 'User',
                'last_name': name.split()[-1] if name and len(name.split()) > 1 else 'User'
            }
        }
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        order_resp = requests.post(order_url, json=pesapal_order, headers=headers)
        if order_resp.status_code != 200:
            # Try to extract error from PesaPal response
            try:
                error_json = order_resp.json()
                error_message = error_json.get('error', order_resp.text)
            except Exception:
                error_message = order_resp.text
            return jsonify({'error': f'Payment service error: {error_message}'}), 500
        try:
            order_response = order_resp.json()
        except json.JSONDecodeError:
            return jsonify({'error': f'Invalid response from payment service: {order_resp.text}'}), 500
        if 'order_tracking_id' not in order_response:
            return jsonify({'error': f'Invalid response from payment service: {order_response}'}), 500
        payment = create_payment_record(
            order_tracking_id=order_tracking_id,
            resource_id=resource_id,
            user_email=email,
            amount=amount
        )
        db.session.add(payment)
        db.session.commit()
        redirect_url = order_response.get('redirect_url')
        if not redirect_url:
            redirect_url = f"https://books-management-system-bcr5.onrender.com/user/download-success.html?resource_id={resource_id}&email={email}&orderTrackingId={order_tracking_id}"
        return jsonify({
            'success': True,
            'orderTrackingId': order_tracking_id,
            'redirectUrl': redirect_url,
            'message': 'Payment initiated successfully'
        })
    except Exception as e:
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