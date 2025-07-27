#!/usr/bin/env python3
"""
Safe database migration script
This script adds missing columns without dropping existing data
"""

from app import app, db
from models import Resource, User, Payment
import logging

logger = logging.getLogger(__name__)

def safe_migrate_database():
    """Safely migrate database by adding missing columns"""
    with app.app_context():
        try:
            logger.info("Starting safe database migration...")
            
            # Get database connection
            connection = db.engine.connect()
            
            # Check if currency column exists in payment table
            result = connection.execute("""
                SELECT COUNT(*) as count 
                FROM information_schema.columns 
                WHERE table_name = 'payment' AND column_name = 'currency'
            """)
            
            currency_exists = result.fetchone()[0] > 0
            
            if not currency_exists:
                logger.info("Adding currency column to payment table...")
                connection.execute("ALTER TABLE payment ADD COLUMN currency VARCHAR(3) DEFAULT 'KES'")
                logger.info("Currency column added successfully!")
            else:
                logger.info("Currency column already exists!")
            
            # Check if other missing columns exist
            missing_columns = []
            
            # Check for ipn_received column
            result = connection.execute("""
                SELECT COUNT(*) as count 
                FROM information_schema.columns 
                WHERE table_name = 'payment' AND column_name = 'ipn_received'
            """)
            if result.fetchone()[0] == 0:
                missing_columns.append("ipn_received")
            
            # Check for ipn_received_at column
            result = connection.execute("""
                SELECT COUNT(*) as count 
                FROM information_schema.columns 
                WHERE table_name = 'payment' AND column_name = 'ipn_received_at'
            """)
            if result.fetchone()[0] == 0:
                missing_columns.append("ipn_received_at")
            
            # Add missing columns
            for column in missing_columns:
                if column == "ipn_received":
                    logger.info("Adding ipn_received column to payment table...")
                    connection.execute("ALTER TABLE payment ADD COLUMN ipn_received BOOLEAN DEFAULT FALSE")
                elif column == "ipn_received_at":
                    logger.info("Adding ipn_received_at column to payment table...")
                    connection.execute("ALTER TABLE payment ADD COLUMN ipn_received_at DATETIME NULL")
            
            connection.close()
            logger.info("Safe database migration completed successfully!")
            
        except Exception as e:
            logger.error(f"Error in safe migration: {str(e)}")
            raise

if __name__ == '__main__':
    safe_migrate_database() 