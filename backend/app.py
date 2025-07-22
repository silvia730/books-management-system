from flask import Flask, request, jsonify, send_file, abort
from flask_cors import CORS
from models import db, Resource, User
from config import Config
import requests
import os

app = Flask(__name__)
app.config.from_object(Config)
CORS(app)
db.init_app(app)

def ensure_admin_user():
    admin = User.query.filter_by(username='admin').first()
    if not admin:
        admin = User(username='admin', email='admin@somafy.co.ke')
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()


@app.route('/api/upload', methods=['POST'])
def upload_resource():
    resource_type = request.form.get('resourceType')
    class_grade = request.form.get('classGrade')
    subject = request.form.get('subject')
    title = request.form.get('title')
    description = request.form.get('description')
    cover = None
    if 'cover' in request.files:
        cover_file = request.files['cover']
        cover = cover_file.read().hex()  # Store as hex string for demo; use file storage in prod
    elif request.form.get('cover'):
        cover = request.form.get('cover')
    resource = Resource(
        resource_type=resource_type,
        class_grade=class_grade,
        subject=subject,
        title=title,
        description=description,
        cover=cover
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
def pay():
    try:
        data = request.json
        resource_id = data.get('resource_id')
        user_email = data.get('email')
        amount = data.get('amount', 100)  # Default to 100 KES
        name = data.get('name', '')
        phone = data.get('phone', '')
        pesapal_key = app.config['PESAPAL_CONSUMER_KEY']
        pesapal_secret = app.config['PESAPAL_CONSUMER_SECRET']
        if not pesapal_key or not pesapal_secret:
            app.logger.error('PesaPal credentials missing. Key: %s, Secret: %s', pesapal_key, pesapal_secret)
            return jsonify({'error': 'PesaPal credentials not configured'}), 500
        auth_url = 'https://pay.pesapal.com/v3/api/Auth/RequestToken'
        auth_resp = requests.post(auth_url, json={
            'consumer_key': pesapal_key,
            'consumer_secret': pesapal_secret
        })
        if not auth_resp.ok:
            app.logger.error('Failed to authenticate with PesaPal: %s', auth_resp.text)
            return jsonify({'error': 'Failed to authenticate with PesaPal'}), 500
        access_token = auth_resp.json().get('token')
        order_url = 'https://pay.pesapal.com/v3/api/Transactions/SubmitOrderRequest'
        headers = {'Authorization': f'Bearer {access_token}'}
        # Compose return_url for auto-download
        return_url = (
            'http://127.0.0.1:5500/user/auto-download.html'
            f'?resource_id={resource_id}'
            f'&email={user_email}'
            f'&name={name}'
            f'&phone={phone}'
            # orderTrackingId will be appended after order creation
        )
        order_data = {
            'id': resource_id,
            'currency': 'KES',
            'amount': amount,
            'description': 'Resource Download',
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
        order_resp = requests.post(order_url, json=order_data, headers=headers)
        if not order_resp.ok:
            app.logger.error('Failed to create PesaPal order: %s', order_resp.text)
            return jsonify({'error': 'Failed to create PesaPal order'}), 500
        payment_url = order_resp.json().get('redirect_url')
        order_tracking_id = order_resp.json().get('order_tracking_id')
        # Append orderTrackingId to return_url for frontend auto-download
        payment_url_with_return = payment_url
        if payment_url and order_tracking_id:
            # Some gateways require you to append the return_url param yourself
            # If not, the return_url above already has all info except orderTrackingId
            # So, the frontend page will need to get orderTrackingId from the query or from the backend
            pass
        return jsonify({'payment_url': payment_url, 'orderTrackingId': order_tracking_id})
    except Exception as e:
        app.logger.exception('Unexpected error in /api/pay: %s', str(e))
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/download/<int:resource_id>', methods=['GET'])
def download_resource(resource_id):
    email = request.args.get('email')
    resource = Resource.query.get(resource_id)
    if not resource:
        return abort(403)
    # 1. Get OAuth token
    pesapal_key = app.config['PESAPAL_CONSUMER_KEY']
    pesapal_secret = app.config['PESAPAL_CONSUMER_SECRET']
    auth_url = 'https://pay.pesapal.com/v3/api/Auth/RequestToken'
    auth_resp = requests.post(auth_url, json={
        'consumer_key': pesapal_key,
        'consumer_secret': pesapal_secret
    })
    if not auth_resp.ok:
        return abort(403)
    access_token = auth_resp.json().get('token')
    # 2. Find the latest order for this resource and email (for demo, assume order ID is resource_id)
    # In a real system, you should store the order tracking ID when creating the order in /api/pay
    # For now, ask the user to provide orderTrackingId as a query param (for demo)
    order_tracking_id = request.args.get('orderTrackingId')
    if not order_tracking_id:
        return abort(403, 'Missing orderTrackingId')
    # 3. Verify payment status
    status_url = f'https://pay.pesapal.com/v3/api/Transactions/GetTransactionStatus?orderTrackingId={order_tracking_id}'
    headers = {'Authorization': f'Bearer {access_token}'}
    status_resp = requests.get(status_url, headers=headers)
    if not status_resp.ok:
        return abort(403)
    status = status_resp.json().get('payment_status')
    if status != 'COMPLETED':
        return abort(403, 'Payment not completed')
    # 4. Send the file
    test_pdf_path = os.path.join(os.path.dirname(__file__), 'static', 'test.pdf')
    if not os.path.exists(test_pdf_path):
        return abort(404)
    return send_file(test_pdf_path, as_attachment=True, download_name='resource.pdf')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        ensure_admin_user()
    app.run(debug=True) 