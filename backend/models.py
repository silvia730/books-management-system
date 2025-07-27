from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()

class Resource(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    resource_type = db.Column(db.String(20), nullable=False)  # book, paper, setbook
    class_grade = db.Column(db.String(20), nullable=False)
    subject = db.Column(db.String(100), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    cover = db.Column(db.String(300), nullable=True)  # store file path

    def to_dict(self):
        return {
            'id': self.id,
            'resource_type': self.resource_type,
            'class_grade': self.class_grade,
            'subject': self.subject,
            'title': self.title,
            'description': self.description,
            'cover': self.cover
        }

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(512), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Payment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_tracking_id = db.Column(db.String(100), unique=True, nullable=False, index=True)
    transaction_tracking_id = db.Column(db.String(100), nullable=True)
    merchant_reference = db.Column(db.String(100), nullable=True)
    resource_id = db.Column(db.Integer, db.ForeignKey('resource.id'), nullable=False)
    user_email = db.Column(db.String(120), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    currency = db.Column(db.String(3), default='KES')
    status = db.Column(db.String(20), default='PENDING')  # PENDING, COMPLETED, FAILED, CANCELLED
    payment_method = db.Column(db.String(50), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    ipn_received = db.Column(db.Boolean, default=False)
    ipn_received_at = db.Column(db.DateTime, nullable=True)
    
    # Relationship
    resource = db.relationship('Resource', backref='payments')

    def to_dict(self):
        return {
            'id': self.id,
            'order_tracking_id': self.order_tracking_id,
            'transaction_tracking_id': self.transaction_tracking_id,
            'merchant_reference': self.merchant_reference,
            'resource_id': self.resource_id,
            'user_email': self.user_email,
            'amount': self.amount,
            'currency': self.currency,
            'status': self.status,
            'payment_method': self.payment_method,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'ipn_received': self.ipn_received,
            'ipn_received_at': self.ipn_received_at.isoformat() if self.ipn_received_at else None
        } 