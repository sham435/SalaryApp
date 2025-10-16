"""
Celery Tasks for Asynchronous Processing
Handles CRM synchronization, reports, and maintenance tasks
"""

from celery_app import celery
import os
import psycopg2
import requests
import logging
from datetime import datetime, timedelta
from typing import Dict, List
import subprocess

logger = logging.getLogger(__name__)

# Configuration
CRM_API_BASE = os.getenv("CRM_API_BASE", "https://crm.jatan.com/api/v1")
CRM_API_KEY = os.getenv("CRM_API_KEY", "")
CRM_ENABLED = os.getenv("CRM_ENABLED", "false").lower() == "true"

def get_db_connection():
    """Get PostgreSQL database connection"""
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "postgres"),
        port=os.getenv("DB_PORT", "5432"),
        dbname=os.getenv("DB_NAME", "labor_salary_db"),
        user=os.getenv("DB_USER", "salary_admin"),
        password=os.getenv("DB_PASSWORD", "password"),
    )

def get_auth_headers() -> Dict[str, str]:
    """Get authentication headers for CRM API"""
    return {
        "Authorization": f"Bearer {CRM_API_KEY}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }


@celery.task(name="tasks.sync_employees_to_crm", bind=True, max_retries=3)
def sync_employees_to_crm(self):
    """Sync employee/labor profiles to CRM"""
    if not CRM_ENABLED:
        logger.info("CRM sync disabled, skipping employee sync")
        return {"status": "skipped", "reason": "CRM disabled"}
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get recently added/updated employees
        cursor.execute("""
            SELECT id, name, base_daily_wage, position, contact_info, overtime_rate
            FROM labor_profiles
            WHERE created_at >= NOW() - INTERVAL '7 days'
            ORDER BY created_at DESC
        """)
        
        employees = []
        for row in cursor.fetchall():
            employees.append({
                "employee_id": row[0],
                "name": row[1],
                "daily_wage": float(row[2]),
                "position": row[3],
                "contact": row[4],
                "overtime_rate": float(row[5])
            })
        
        cursor.close()
        conn.close()
        
        if not employees:
            logger.info("No new employees to sync")
            return {"status": "success", "synced": 0}
        
        # Send to CRM
        response = requests.post(
            f"{CRM_API_BASE}/employees/sync",
            json={"employees": employees},
            headers=get_auth_headers(),
            timeout=30
        )
        
        if response.status_code in [200, 201]:
            logger.info(f"Synced {len(employees)} employees to CRM")
            return {"status": "success", "synced": len(employees)}
        else:
            logger.error(f"CRM sync failed: {response.status_code} - {response.text}")
            raise Exception(f"CRM API error: {response.status_code}")
            
    except Exception as e:
        logger.error(f"Employee sync error: {e}")
        # Retry with exponential backoff
        self.retry(exc=e, countdown=60 * (2 ** self.request.retries))


@celery.task(name="tasks.sync_salaries_to_crm", bind=True, max_retries=3)
def sync_salaries_to_crm(year: int, month: int):
    """Sync salary records for a specific month to CRM"""
    if not CRM_ENABLED:
        logger.info("CRM sync disabled, skipping salary sync")
        return {"status": "skipped", "reason": "CRM disabled"}
    
    try:
        conn = get_db_connection()
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
                "employee_name": row[0],
                "date": row[1].isoformat(),
                "day_type": row[2],
                "daily_wage": float(row[3]),
                "hours_worked": float(row[4]),
                "overtime_hours": float(row[5]),
                "weekend_bonus": float(row[6]),
                "holiday_bonus": float(row[7]),
                "allowances": float(row[8]),
                "deductions": float(row[9]),
                "total_salary": float(row[10])
            })
        
        cursor.close()
        conn.close()
        
        if not salaries:
            logger.info(f"No salaries to sync for {year}-{month:02d}")
            return {"status": "success", "synced": 0}
        
        # Send to CRM
        response = requests.post(
            f"{CRM_API_BASE}/salaries/sync",
            json={
                "year": year,
                "month": month,
                "salaries": salaries
            },
            headers=get_auth_headers(),
            timeout=60
        )
        
        if response.status_code in [200, 201]:
            logger.info(f"Synced {len(salaries)} salary records to CRM")
            return {"status": "success", "synced": len(salaries), "year": year, "month": month}
        else:
            logger.error(f"Salary sync failed: {response.status_code}")
            raise Exception(f"CRM API error: {response.status_code}")
            
    except Exception as e:
        logger.error(f"Salary sync error: {e}")
        raise


@celery.task(name="tasks.sync_reports_to_crm", bind=True, max_retries=3)
def sync_reports_to_crm(year: int, month: int):
    """Sync monthly summary report to CRM"""
    if not CRM_ENABLED:
        return {"status": "skipped", "reason": "CRM disabled"}
    
    try:
        conn = get_db_connection()
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
                "employee_name": row[0],
                "working_days": row[1],
                "total_hours": float(row[2]),
                "total_overtime": float(row[3]),
                "total_salary": float(row[4])
            })
        
        cursor.close()
        conn.close()
        
        if not summary:
            return {"status": "success", "synced": 0}
        
        response = requests.post(
            f"{CRM_API_BASE}/reports/summary",
            json={"year": year, "month": month, "summary": summary},
            headers=get_auth_headers(),
            timeout=30
        )
        
        if response.status_code in [200, 201]:
            logger.info(f"Synced summary report to CRM")
            return {"status": "success", "synced": len(summary)}
        else:
            raise Exception(f"CRM API error: {response.status_code}")
            
    except Exception as e:
        logger.error(f"Report sync error: {e}")
        raise


@celery.task(name="tasks.periodic_crm_sync")
def periodic_crm_sync():
    """Periodic task to sync all data to CRM"""
    if not CRM_ENABLED:
        logger.info("CRM sync disabled")
        return {"status": "disabled"}
    
    now = datetime.now()
    
    # Sync employees
    sync_employees_to_crm.delay()
    
    # Sync current month salaries
    sync_salaries_to_crm.delay(now.year, now.month)
    
    # Sync reports if enabled
    if os.getenv("CRM_SYNC_REPORTS", "false").lower() == "true":
        sync_reports_to_crm.delay(now.year, now.month)
    
    logger.info("Periodic CRM sync tasks queued")
    return {"status": "queued", "timestamp": now.isoformat()}


@celery.task(name="tasks.generate_monthly_report")
def generate_monthly_report(year: int = None, month: int = None):
    """Generate monthly salary report"""
    if year is None or month is None:
        now = datetime.now()
        year = now.year
        month = now.month - 1 if now.month > 1 else 12
        if month == 12:
            year -= 1
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                labor_name,
                COUNT(*) as days,
                SUM(total_salary) as total
            FROM salary_records
            WHERE EXTRACT(YEAR FROM date) = %s AND EXTRACT(MONTH FROM date) = %s
            GROUP BY labor_name
        """, (year, month))
        
        results = cursor.fetchall()
        cursor.close()
        conn.close()
        
        logger.info(f"Generated monthly report for {year}-{month:02d}")
        return {
            "status": "success",
            "year": year,
            "month": month,
            "records": len(results)
        }
        
    except Exception as e:
        logger.error(f"Report generation error: {e}")
        raise


@celery.task(name="tasks.backup_database")
def backup_database():
    """Create database backup"""
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = f"/app/backups/backup_{timestamp}.sql"
        
        # Use pg_dump to create backup
        db_host = os.getenv("DB_HOST", "postgres")
        db_name = os.getenv("DB_NAME", "labor_salary_db")
        db_user = os.getenv("DB_USER", "salary_admin")
        
        cmd = f"pg_dump -h {db_host} -U {db_user} -d {db_name} -f {backup_file}"
        
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            env={**os.environ, "PGPASSWORD": os.getenv("DB_PASSWORD")}
        )
        
        if result.returncode == 0:
            logger.info(f"Database backup created: {backup_file}")
            return {"status": "success", "file": backup_file}
        else:
            logger.error(f"Backup failed: {result.stderr}")
            raise Exception(f"Backup failed: {result.stderr}")
            
    except Exception as e:
        logger.error(f"Backup error: {e}")
        raise


@celery.task(name="tasks.cleanup_old_files")
def cleanup_old_files(days: int = 30):
    """Cleanup old backup files and exports"""
    try:
        cutoff_date = datetime.now() - timedelta(days=days)
        deleted_count = 0
        
        # Cleanup backups
        backup_dir = "/app/backups"
        if os.path.exists(backup_dir):
            for filename in os.listdir(backup_dir):
                filepath = os.path.join(backup_dir, filename)
                if os.path.isfile(filepath):
                    file_time = datetime.fromtimestamp(os.path.getmtime(filepath))
                    if file_time < cutoff_date:
                        os.remove(filepath)
                        deleted_count += 1
                        logger.info(f"Deleted old backup: {filename}")
        
        # Cleanup exports
        export_dir = "/app/exports"
        if os.path.exists(export_dir):
            for filename in os.listdir(export_dir):
                filepath = os.path.join(export_dir, filename)
                if os.path.isfile(filepath):
                    file_time = datetime.fromtimestamp(os.path.getmtime(filepath))
                    if file_time < cutoff_date:
                        os.remove(filepath)
                        deleted_count += 1
                        logger.info(f"Deleted old export: {filename}")
        
        logger.info(f"Cleanup completed: {deleted_count} files deleted")
        return {"status": "success", "deleted": deleted_count}
        
    except Exception as e:
        logger.error(f"Cleanup error: {e}")
        raise


# Test task for monitoring
@celery.task(name="tasks.health_check")
def health_check():
    """Health check task"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "worker": "celery"
    }


