"""
CRM Integration Module
Syncs salary data with JatanCRM Portal
"""

import os
import requests
import json
import logging
from typing import Dict, List, Optional
from datetime import datetime
import psycopg2
from db_config import DatabaseConfig

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class CRMIntegration:
    """Handles integration with JatanCRM Portal"""

    def __init__(self):
        self.enabled = os.getenv('CRM_ENABLED', 'false').lower() == 'true'
        self.api_base = os.getenv('CRM_API_BASE', 'https://crm.jatan.com/api/v1')
        self.api_key = os.getenv('CRM_API_KEY', '')
        self.client_id = os.getenv('CRM_CLIENT_ID', 'jatan_salary_app')
        self.client_secret = os.getenv('CRM_CLIENT_SECRET', '')
        self.sync_interval = int(os.getenv('CRM_SYNC_INTERVAL', '10'))
        self.timeout = int(os.getenv('CRM_TIMEOUT', '30'))

        self.db_config = DatabaseConfig.from_file()

        if self.enabled:
            logger.info("CRM Integration enabled")
        else:
            logger.info("CRM Integration disabled")

    def get_auth_headers(self) -> Dict[str, str]:
        """Get authentication headers"""
        return {
            'Authorization': f'Bearer {self.api_key}',
            'X-Client-ID': self.client_id,
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }

    def test_connection(self) -> bool:
        """Test connection to CRM API"""
        if not self.enabled:
            logger.warning("CRM Integration is disabled")
            return False

        try:
            response = requests.get(
                f"{self.api_base}/health",
                headers=self.get_auth_headers(),
                timeout=self.timeout
            )

            if response.status_code == 200:
                logger.info("CRM connection successful")
                return True
            else:
                logger.error(f"CRM connection failed: {response.status_code}")
                return False

        except Exception as e:
            logger.error(f"CRM connection error: {e}")
            return False

    def sync_employees(self) -> bool:
        """Sync employee/labor profiles to CRM"""
        if not self.enabled:
            return False

        try:
            # Get employees from local database
            conn = psycopg2.connect(self.db_config.get_connection_string())
            cursor = conn.cursor()

            cursor.execute("""
                SELECT id, name, base_daily_wage, position, contact_info, overtime_rate
                FROM labor_profiles
                WHERE created_at >= NOW() - INTERVAL '7 days'
                ORDER BY created_at DESC
            """)

            employees = []
            for row in cursor.fetchall():
                employees.append({
                    'employee_id': row[0],
                    'name': row[1],
                    'daily_wage': float(row[2]),
                    'position': row[3],
                    'contact': row[4],
                    'overtime_rate': float(row[5])
                })

            cursor.close()
            conn.close()

            if not employees:
                logger.info("No new employees to sync")
                return True

            # Send to CRM
            response = requests.post(
                f"{self.api_base}/employees/sync",
                json={'employees': employees},
                headers=self.get_auth_headers(),
                timeout=self.timeout
            )

            if response.status_code in [200, 201]:
                logger.info(f"Synced {len(employees)} employees to CRM")
                return True
            else:
                logger.error(f"Employee sync failed: {response.status_code} - {response.text}")
                return False

        except Exception as e:
            logger.error(f"Employee sync error: {e}")
            return False

    def sync_salaries(self, year: int, month: int) -> bool:
        """Sync salary records for a specific month to CRM"""
        if not self.enabled:
            return False

        try:
            # Get salary records from local database
            conn = psycopg2.connect(self.db_config.get_connection_string())
            cursor = conn.cursor()

            cursor.execute("""
                SELECT labor_name, date, day_type, daily_wage, hours_worked,
                       overtime_hours, weekend_bonus, holiday_bonus,
                       other_allowances, deductions, total_salary
                FROM salary_records
                WHERE EXTRACT(YEAR FROM date) = %s AND EXTRACT(MONTH FROM date) = %s
                ORDER BY date, labor_name
            """, (year, month))

            salaries = []
            for row in cursor.fetchall():
                salaries.append({
                    'employee_name': row[0],
                    'date': row[1].isoformat(),
                    'day_type': row[2],
                    'daily_wage': float(row[3]),
                    'hours_worked': float(row[4]),
                    'overtime_hours': float(row[5]),
                    'weekend_bonus': float(row[6]),
                    'holiday_bonus': float(row[7]),
                    'allowances': float(row[8]),
                    'deductions': float(row[9]),
                    'total_salary': float(row[10])
                })

            cursor.close()
            conn.close()

            if not salaries:
                logger.info(f"No salaries to sync for {year}-{month:02d}")
                return True

            # Send to CRM
            response = requests.post(
                f"{self.api_base}/salaries/sync",
                json={
                    'year': year,
                    'month': month,
                    'salaries': salaries
                },
                headers=self.get_auth_headers(),
                timeout=self.timeout
            )

            if response.status_code in [200, 201]:
                logger.info(f"Synced {len(salaries)} salary records to CRM for {year}-{month:02d}")
                return True
            else:
                logger.error(f"Salary sync failed: {response.status_code} - {response.text}")
                return False

        except Exception as e:
            logger.error(f"Salary sync error: {e}")
            return False

    def sync_summary_report(self, year: int, month: int) -> bool:
        """Sync monthly summary report to CRM"""
        if not self.enabled:
            return False

        try:
            # Generate summary from local database
            conn = psycopg2.connect(self.db_config.get_connection_string())
            cursor = conn.cursor()

            cursor.execute("""
                SELECT
                    labor_name,
                    COUNT(*) as working_days,
                    SUM(hours_worked) as total_hours,
                    SUM(overtime_hours) as total_overtime,
                    SUM(total_salary) as total_salary
                FROM salary_records
                WHERE EXTRACT(YEAR FROM date) = %s AND EXTRACT(MONTH FROM date) = %s
                GROUP BY labor_name
                ORDER BY labor_name
            """, (year, month))

            summary = []
            for row in cursor.fetchall():
                summary.append({
                    'employee_name': row[0],
                    'working_days': row[1],
                    'total_hours': float(row[2]),
                    'total_overtime': float(row[3]),
                    'total_salary': float(row[4])
                })

            cursor.close()
            conn.close()

            if not summary:
                logger.info(f"No summary data for {year}-{month:02d}")
                return True

            # Send to CRM
            response = requests.post(
                f"{self.api_base}/reports/summary",
                json={
                    'year': year,
                    'month': month,
                    'summary': summary
                },
                headers=self.get_auth_headers(),
                timeout=self.timeout
            )

            if response.status_code in [200, 201]:
                logger.info(f"Synced summary report to CRM for {year}-{month:02d}")
                return True
            else:
                logger.error(f"Summary sync failed: {response.status_code} - {response.text}")
                return False

        except Exception as e:
            logger.error(f"Summary sync error: {e}")
            return False

    def get_employee_from_crm(self, employee_id: str) -> Optional[Dict]:
        """Get employee details from CRM"""
        if not self.enabled:
            return None

        try:
            response = requests.get(
                f"{self.api_base}/employees/{employee_id}",
                headers=self.get_auth_headers(),
                timeout=self.timeout
            )

            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Failed to get employee from CRM: {response.status_code}")
                return None

        except Exception as e:
            logger.error(f"Error getting employee from CRM: {e}")
            return None

    def webhook_handler(self, event_type: str, data: Dict) -> bool:
        """Handle webhook events from CRM"""
        if not self.enabled:
            return False

        logger.info(f"Received webhook: {event_type}")

        try:
            if event_type == "employee.created":
                # Handle new employee created in CRM
                return self._handle_employee_created(data)
            elif event_type == "employee.updated":
                # Handle employee updated in CRM
                return self._handle_employee_updated(data)
            elif event_type == "salary.requested":
                # Handle salary calculation request from CRM
                return self._handle_salary_requested(data)
            else:
                logger.warning(f"Unknown webhook event type: {event_type}")
                return False

        except Exception as e:
            logger.error(f"Webhook handling error: {e}")
            return False

    def _handle_employee_created(self, data: Dict) -> bool:
        """Handle employee created webhook"""
        # Implement employee creation logic
        logger.info(f"Handling employee created: {data.get('name')}")
        return True

    def _handle_employee_updated(self, data: Dict) -> bool:
        """Handle employee updated webhook"""
        # Implement employee update logic
        logger.info(f"Handling employee updated: {data.get('name')}")
        return True

    def _handle_salary_requested(self, data: Dict) -> bool:
        """Handle salary calculation request"""
        # Implement salary calculation request logic
        logger.info(f"Handling salary request for: {data.get('employee_name')}")
        return True


def run_periodic_sync():
    """Run periodic sync (can be called from scheduler)"""
    logger.info("Starting periodic CRM sync")

    crm = CRMIntegration()

    if not crm.enabled:
        logger.info("CRM integration disabled, skipping sync")
        return

    # Test connection
    if not crm.test_connection():
        logger.error("CRM connection test failed, skipping sync")
        return

    # Sync employees
    if os.getenv('CRM_SYNC_EMPLOYEES', 'true').lower() == 'true':
        crm.sync_employees()

    # Sync current month salaries
    if os.getenv('CRM_SYNC_SALARIES', 'true').lower() == 'true':
        now = datetime.now()
        crm.sync_salaries(now.year, now.month)

    logger.info("Periodic CRM sync completed")


if __name__ == "__main__":
    # Test CRM integration
    print("Testing CRM Integration...")

    crm = CRMIntegration()

    print(f"CRM Enabled: {crm.enabled}")
    print(f"API Base: {crm.api_base}")
    print(f"Sync Interval: {crm.sync_interval} minutes")

    if crm.enabled:
        print("\nTesting connection...")
        if crm.test_connection():
            print("✓ Connection successful")
        else:
            print("✗ Connection failed")
    else:
        print("\n⚠ CRM Integration is disabled")
        print("Set CRM_ENABLED=true in .env to enable")


