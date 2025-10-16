#!/usr/bin/env python3
"""
Setup script for PostgreSQL database
Creates database and initializes tables
"""

import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import sys
import os

def load_config_from_env():
    """Load database configuration from .env file"""
    config = {
        'host': 'localhost',
        'port': 5432,
        'database': 'labor_salary_db',
        'user': 'postgres',
        'password': 'password'
    }

    if os.path.exists('.env'):
        with open('.env', 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    try:
                        key, value = line.split('=', 1)
                        key = key.strip()
                        value = value.strip().strip('"').strip("'")

                        if key == 'DB_HOST':
                            config['host'] = value
                        elif key == 'DB_PORT':
                            config['port'] = int(value)
                        elif key == 'DB_NAME':
                            config['database'] = value
                        elif key == 'DB_USER':
                            config['user'] = value
                        elif key == 'DB_PASSWORD':
                            config['password'] = value
                    except ValueError:
                        continue

    return config


def create_database(config):
    """Create database if it doesn't exist"""
    try:
        # Connect to PostgreSQL server (not to specific database)
        conn = psycopg2.connect(
            host=config['host'],
            port=config['port'],
            user=config['user'],
            password=config['password'],
            database='postgres'  # Connect to default database
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()

        # Check if database exists
        cursor.execute(
            "SELECT 1 FROM pg_database WHERE datname = %s",
            (config['database'],)
        )

        if cursor.fetchone():
            print(f"✓ Database '{config['database']}' already exists")
        else:
            # Create database
            cursor.execute(f"CREATE DATABASE {config['database']}")
            print(f"✓ Created database '{config['database']}'")

        cursor.close()
        conn.close()
        return True

    except psycopg2.Error as e:
        print(f"✗ Error creating database: {e}")
        return False


def initialize_tables(config):
    """Initialize database tables"""
    try:
        conn = psycopg2.connect(
            host=config['host'],
            port=config['port'],
            user=config['user'],
            password=config['password'],
            database=config['database']
        )
        cursor = conn.cursor()

        # Create labor_profiles table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS labor_profiles (
                id SERIAL PRIMARY KEY,
                name VARCHAR(255) NOT NULL UNIQUE,
                base_daily_wage DECIMAL(10,2) NOT NULL,
                hourly_rate DECIMAL(10,2) NOT NULL,
                position VARCHAR(255),
                contact_info TEXT,
                overtime_rate DECIMAL(3,2) DEFAULT 1.5,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print("✓ Created labor_profiles table")

        # Create salary_records table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS salary_records (
                id SERIAL PRIMARY KEY,
                labor_name VARCHAR(255) NOT NULL,
                date DATE NOT NULL,
                day_type VARCHAR(50) DEFAULT 'Weekday',
                daily_wage DECIMAL(10,2) NOT NULL,
                hours_worked DECIMAL(4,2) DEFAULT 8.00,
                regular_hours DECIMAL(4,2) DEFAULT 8.00,
                overtime_hours DECIMAL(4,2) DEFAULT 0.00,
                overtime_rate DECIMAL(3,2) DEFAULT 1.50,
                weekend_bonus DECIMAL(10,2) DEFAULT 0.00,
                holiday_bonus DECIMAL(10,2) DEFAULT 0.00,
                other_allowances DECIMAL(10,2) DEFAULT 0.00,
                deductions DECIMAL(10,2) DEFAULT 0.00,
                total_salary DECIMAL(10,2) NOT NULL,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(labor_name, date)
            )
        """)
        print("✓ Created salary_records table")

        # Create indexes
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_salary_records_date
            ON salary_records (date)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_salary_records_labor_name
            ON salary_records (labor_name)
        """)
        print("✓ Created indexes")

        conn.commit()
        cursor.close()
        conn.close()

        print("\n✅ Database setup completed successfully!")
        return True

    except psycopg2.Error as e:
        print(f"✗ Error initializing tables: {e}")
        return False


def main():
    """Main setup function"""
    print("=" * 60)
    print("PostgreSQL Database Setup for Salary Calculator")
    print("=" * 60)
    print()

    # Load configuration
    print("Loading configuration from .env...")
    config = load_config_from_env()
    print(f"✓ Configuration loaded")
    print(f"  Host: {config['host']}")
    print(f"  Port: {config['port']}")
    print(f"  Database: {config['database']}")
    print(f"  User: {config['user']}")
    print()

    # Test connection
    print("Testing connection to PostgreSQL server...")
    try:
        conn = psycopg2.connect(
            host=config['host'],
            port=config['port'],
            user=config['user'],
            password=config['password'],
            database='postgres'
        )
        conn.close()
        print("✓ Successfully connected to PostgreSQL server")
        print()
    except psycopg2.Error as e:
        print(f"✗ Failed to connect to PostgreSQL server")
        print(f"  Error: {e}")
        print()
        print("Please check your configuration in .env file and ensure PostgreSQL is running.")
        sys.exit(1)

    # Create database
    print("Creating database...")
    if not create_database(config):
        sys.exit(1)
    print()

    # Initialize tables
    print("Initializing database tables...")
    if not initialize_tables(config):
        sys.exit(1)
    print()

    print("=" * 60)
    print("Setup completed! You can now run the application.")
    print("=" * 60)


if __name__ == "__main__":
    main()

