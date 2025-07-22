from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class Resource(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    resource_type = db.Column(db.String(20), nullable=False)  # book, paper, setbook
    class_grade = db.Column(db.String(20), nullable=False)
    subject = db.Column(db.String(100), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    cover = db.Column(db.Text, nullable=True)  # store as base64 or file path

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