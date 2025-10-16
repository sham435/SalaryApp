#!/usr/bin/env python3
"""
Production Launcher for Labor Salary Calculator (PostgreSQL Version)
Handles initialization, error handling, and logging
"""

import sys
import os
import logging
import tkinter as tk
from tkinter import messagebox
import traceback

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('salary_app.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


def check_dependencies():
    """Check if all required dependencies are installed"""
    required_modules = [
        ('pandas', 'pandas'),
        ('reportlab', 'reportlab'),
        ('openpyxl', 'openpyxl'),
        ('psycopg2', 'psycopg2-binary'),
    ]

    missing = []
    for module_name, package_name in required_modules:
        try:
            __import__(module_name)
        except ImportError:
            missing.append(package_name)

    if missing:
        error_msg = f"Missing required packages: {', '.join(missing)}\n\n"
        error_msg += f"Please install them using:\n"
        error_msg += f"pip install {' '.join(missing)}"
        logger.error(error_msg)
        return False, error_msg

    return True, "All dependencies satisfied"


def check_database_config():
    """Check if database configuration exists"""
    if os.path.exists('.env'):
        logger.info("Database configuration found in .env file")
        return True
    else:
        logger.warning("No .env file found, will use defaults or prompt for configuration")
        return False


def create_default_env():
    """Create default .env file if it doesn't exist"""
    if not os.path.exists('.env'):
        with open('.env', 'w') as f:
            f.write("# PostgreSQL Database Configuration\n")
            f.write("# Update these values with your actual database credentials\n\n")
            f.write("DB_HOST=localhost\n")
            f.write("DB_PORT=5432\n")
            f.write("DB_NAME=labor_salary_db\n")
            f.write("DB_USER=postgres\n")
            f.write("DB_PASSWORD=password\n")
        logger.info("Created default .env file - please update with your credentials")
        return True
    return False


def main():
    """Main application entry point"""
    logger.info("=" * 80)
    logger.info("Starting Jatan Jewellery Salary Management System (PostgreSQL)")
    logger.info("=" * 80)

    try:
        # Check dependencies
        logger.info("Checking dependencies...")
        deps_ok, deps_msg = check_dependencies()
        if not deps_ok:
            messagebox.showerror("Missing Dependencies", deps_msg)
            sys.exit(1)
        logger.info("✓ All dependencies satisfied")

        # Check/create database configuration
        if not check_database_config():
            logger.info("Creating default .env file...")
            create_default_env()
            messagebox.showinfo(
                "Database Configuration",
                "A default .env file has been created.\n\n"
                "Please update it with your PostgreSQL credentials before running the application."
            )

        # Import application modules
        logger.info("Importing application modules...")
        try:
            from salary_calculator_postgres import LaborSalaryCalculatorGUI
            logger.info("✓ Application modules loaded successfully")
        except ImportError as e:
            logger.error(f"Failed to import application modules: {e}")
            messagebox.showerror(
                "Import Error",
                f"Failed to load application:\n{str(e)}\n\n"
                "Please ensure all files are present and dependencies are installed."
            )
            sys.exit(1)

        # Create and run GUI
        logger.info("Initializing GUI...")
        root = tk.Tk()

        # Set application icon (if available)
        try:
            if sys.platform.startswith('win'):
                root.iconbitmap('icon.ico')
        except:
            pass  # Icon not critical

        # Initialize application
        try:
            app = LaborSalaryCalculatorGUI(root)
            logger.info("✓ Application initialized successfully")
            logger.info("Application is now running...")

            # Run mainloop
            root.mainloop()

        except Exception as e:
            logger.error(f"Error during application initialization: {e}")
            logger.error(traceback.format_exc())
            messagebox.showerror(
                "Initialization Error",
                f"Failed to initialize application:\n{str(e)}\n\n"
                "Please check the log file for details."
            )
            sys.exit(1)

        logger.info("Application closed normally")

    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        logger.error(traceback.format_exc())
        messagebox.showerror(
            "Unexpected Error",
            f"An unexpected error occurred:\n{str(e)}\n\n"
            "Please check the log file for details."
        )
        sys.exit(1)


if __name__ == "__main__":
    main()

