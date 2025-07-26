#!/usr/bin/env python3
"""
Database initialization script for the PesaPal IPN system
Run this script to create all necessary tables including the Payment table
"""

from app import app, db
from models import Resource, User, Payment

def init_database():
    """Initialize the database with all tables"""
    with app.app_context():
        print("Creating database tables...")
        db.create_all()
        print("Database tables created successfully!")
        
        # Create admin user if it doesn't exist
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            admin = User(username='admin', email='admin@somafy.co.ke')
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
            print("Admin user created!")
        else:
            print("Admin user already exists!")
        
        print("Database initialization completed!")

if __name__ == '__main__':
    init_database() 