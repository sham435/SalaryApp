"""
Database Manager for Salary Calculator
Handles database operations, backups, and integrity checks
"""

import sqlite3
import os
import shutil
import datetime
import logging
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('salary_app.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


class DatabaseManager:
    """Manages database operations and maintenance"""

    def __init__(self, db_name='labor_salary.db', backup_dir='backups'):
        self.db_name = db_name
        self.backup_dir = backup_dir
        self.ensure_backup_directory()
        logger.info(f"DatabaseManager initialized with database: {db_name}")

    def ensure_backup_directory(self):
        """Ensure backup directory exists"""
        if not os.path.exists(self.backup_dir):
            os.makedirs(self.backup_dir)
            logger.info(f"Created backup directory: {self.backup_dir}")

    def init_database(self):
        """Initialize database with required tables"""
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()

            # Enable foreign keys
            cursor.execute('PRAGMA foreign_keys = ON')

            # Labor profiles table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS labor_profiles (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE,
                    base_daily_wage REAL NOT NULL CHECK(base_daily_wage > 0),
                    hourly_rate REAL NOT NULL CHECK(hourly_rate > 0),
                    position TEXT,
                    contact_info TEXT,
                    overtime_rate REAL DEFAULT 1.5 CHECK(overtime_rate > 0),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_active INTEGER DEFAULT 1
                )
            ''')

            # Salary records table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS salary_records (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    labor_name TEXT NOT NULL,
                    date DATE NOT NULL,
                    day_type TEXT DEFAULT 'Weekday',
                    daily_wage REAL NOT NULL CHECK(daily_wage >= 0),
                    hours_worked REAL DEFAULT 8 CHECK(hours_worked >= 0),
                    regular_hours REAL DEFAULT 8 CHECK(regular_hours >= 0),
                    overtime_hours REAL DEFAULT 0 CHECK(overtime_hours >= 0),
                    overtime_rate REAL DEFAULT 1.5 CHECK(overtime_rate > 0),
                    weekend_bonus REAL DEFAULT 0 CHECK(weekend_bonus >= 0),
                    holiday_bonus REAL DEFAULT 0 CHECK(holiday_bonus >= 0),
                    other_allowances REAL DEFAULT 0 CHECK(other_allowances >= 0),
                    deductions REAL DEFAULT 0 CHECK(deductions >= 0),
                    total_salary REAL NOT NULL CHECK(total_salary >= 0),
                    notes TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(labor_name, date)
                )
            ''')

            # Create indexes for better performance
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_salary_records_date
                ON salary_records(date)
            ''')

            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_salary_records_labor_name
                ON salary_records(labor_name)
            ''')

            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_salary_records_labor_date
                ON salary_records(labor_name, date)
            ''')

            # Application metadata table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS app_metadata (
                    key TEXT PRIMARY KEY,
                    value TEXT,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            # Set database version
            cursor.execute('''
                INSERT OR REPLACE INTO app_metadata (key, value, updated_at)
                VALUES ('db_version', '1.0', CURRENT_TIMESTAMP)
            ''')

            conn.commit()
            logger.info("Database initialized successfully")
            return True

        except sqlite3.Error as e:
            logger.error(f"Database initialization error: {e}")
            return False
        finally:
            if conn:
                conn.close()

    def backup_database(self, backup_name=None):
        """Create a backup of the database"""
        try:
            if not os.path.exists(self.db_name):
                logger.warning("Database file does not exist, nothing to backup")
                return None

            if backup_name is None:
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_name = f"labor_salary_backup_{timestamp}.db"

            backup_path = os.path.join(self.backup_dir, backup_name)
            shutil.copy2(self.db_name, backup_path)

            logger.info(f"Database backed up to: {backup_path}")
            return backup_path

        except Exception as e:
            logger.error(f"Backup failed: {e}")
            return None

    def restore_database(self, backup_path):
        """Restore database from backup"""
        try:
            if not os.path.exists(backup_path):
                logger.error(f"Backup file not found: {backup_path}")
                return False

            # Create a backup of current database before restoring
            current_backup = self.backup_database("pre_restore_backup.db")

            # Restore the backup
            shutil.copy2(backup_path, self.db_name)

            logger.info(f"Database restored from: {backup_path}")
            return True

        except Exception as e:
            logger.error(f"Restore failed: {e}")
            return False

    def list_backups(self):
        """List all available backups"""
        try:
            backups = []
            if os.path.exists(self.backup_dir):
                for file in os.listdir(self.backup_dir):
                    if file.endswith('.db'):
                        filepath = os.path.join(self.backup_dir, file)
                        size = os.path.getsize(filepath)
                        modified = datetime.datetime.fromtimestamp(
                            os.path.getmtime(filepath)
                        )
                        backups.append({
                            'name': file,
                            'path': filepath,
                            'size': size,
                            'modified': modified
                        })

            backups.sort(key=lambda x: x['modified'], reverse=True)
            return backups

        except Exception as e:
            logger.error(f"Error listing backups: {e}")
            return []

    def check_integrity(self):
        """Check database integrity"""
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()

            cursor.execute('PRAGMA integrity_check')
            result = cursor.fetchone()

            conn.close()

            if result[0] == 'ok':
                logger.info("Database integrity check passed")
                return True
            else:
                logger.error(f"Database integrity check failed: {result[0]}")
                return False

        except sqlite3.Error as e:
            logger.error(f"Integrity check error: {e}")
            return False

    def vacuum_database(self):
        """Optimize database by running VACUUM"""
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()

            cursor.execute('VACUUM')

            conn.close()
            logger.info("Database vacuum completed successfully")
            return True

        except sqlite3.Error as e:
            logger.error(f"Vacuum failed: {e}")
            return False

    def get_database_stats(self):
        """Get database statistics"""
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()

            stats = {}

            # Get table counts
            cursor.execute('SELECT COUNT(*) FROM labor_profiles WHERE is_active = 1')
            stats['active_laborers'] = cursor.fetchone()[0]

            cursor.execute('SELECT COUNT(*) FROM salary_records')
            stats['total_salary_records'] = cursor.fetchone()[0]

            # Get date range of records
            cursor.execute('SELECT MIN(date), MAX(date) FROM salary_records')
            date_range = cursor.fetchone()
            stats['earliest_record'] = date_range[0]
            stats['latest_record'] = date_range[1]

            # Get database file size
            if os.path.exists(self.db_name):
                stats['db_size_mb'] = os.path.getsize(self.db_name) / (1024 * 1024)
            else:
                stats['db_size_mb'] = 0

            conn.close()

            return stats

        except sqlite3.Error as e:
            logger.error(f"Error getting database stats: {e}")
            return {}

    def export_to_sql(self, output_file):
        """Export database to SQL file"""
        try:
            conn = sqlite3.connect(self.db_name)

            with open(output_file, 'w') as f:
                for line in conn.iterdump():
                    f.write(f'{line}\n')

            conn.close()

            logger.info(f"Database exported to SQL: {output_file}")
            return True

        except Exception as e:
            logger.error(f"SQL export failed: {e}")
            return False

    def cleanup_old_backups(self, keep_count=10):
        """Clean up old backups, keeping only the most recent ones"""
        try:
            backups = self.list_backups()

            if len(backups) > keep_count:
                backups_to_delete = backups[keep_count:]

                for backup in backups_to_delete:
                    # Don't delete pre_restore backups
                    if 'pre_restore' not in backup['name']:
                        os.remove(backup['path'])
                        logger.info(f"Deleted old backup: {backup['name']}")

                logger.info(f"Cleanup completed, kept {keep_count} most recent backups")
                return True
            else:
                logger.info("No cleanup needed")
                return True

        except Exception as e:
            logger.error(f"Backup cleanup failed: {e}")
            return False


def test_database_manager():
    """Test database manager functionality"""
    print("Testing Database Manager...")

    db_manager = DatabaseManager('test_production.db')

    # Test initialization
    print("\n1. Testing database initialization...")
    if db_manager.init_database():
        print("✓ Database initialized successfully")
    else:
        print("✗ Database initialization failed")
        return

    # Test integrity check
    print("\n2. Testing integrity check...")
    if db_manager.check_integrity():
        print("✓ Integrity check passed")
    else:
        print("✗ Integrity check failed")

    # Test backup
    print("\n3. Testing backup...")
    backup_path = db_manager.backup_database()
    if backup_path:
        print(f"✓ Backup created: {backup_path}")
    else:
        print("✗ Backup failed")

    # Test list backups
    print("\n4. Testing list backups...")
    backups = db_manager.list_backups()
    print(f"✓ Found {len(backups)} backup(s)")

    # Test stats
    print("\n5. Testing database stats...")
    stats = db_manager.get_database_stats()
    if stats:
        print(f"✓ Database stats retrieved:")
        for key, value in stats.items():
            print(f"  - {key}: {value}")
    else:
        print("✗ Failed to get stats")

    # Cleanup
    print("\n6. Cleaning up test files...")
    if os.path.exists('test_production.db'):
        os.remove('test_production.db')
    if os.path.exists('backups'):
        shutil.rmtree('backups')
    print("✓ Cleanup completed")

    print("\n✅ All database manager tests completed!")


if __name__ == "__main__":
    test_database_manager()

