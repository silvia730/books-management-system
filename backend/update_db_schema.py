#!/usr/bin/env python3
"""
Database schema update script
This script will update your database tables to match the current models
"""

from app import app, db
from models import Resource, User, Payment
import logging

logger = logging.getLogger(__name__)

def update_database_schema():
    """Update database schema to match current models"""
    with app.app_context():
        try:
            logger.info("Starting database schema update...")
            
            # Drop all tables and recreate them
            logger.info("Dropping all tables...")
            db.drop_all()
            
            logger.info("Creating all tables...")
            db.create_all()
            
            # Create admin user
            logger.info("Creating admin user...")
            admin = User(username='admin', email='admin@somafy.co.ke')
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
            
            logger.info("Database schema update completed successfully!")
            logger.info("Admin user created: username=admin, password=admin123")
            
        except Exception as e:
            logger.error(f"Error updating database schema: {str(e)}")
            db.session.rollback()
            raise

if __name__ == '__main__':
    update_database_schema() 