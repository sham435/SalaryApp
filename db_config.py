"""
Database Configuration Management
Handles PostgreSQL connection settings with environment variable support
"""

import os
from typing import Optional


class DatabaseConfig:
    """PostgreSQL database configuration"""
    
    def __init__(self):
        # Load from environment variables or use defaults
        self.host = os.getenv('DB_HOST', 'localhost')
        self.port = int(os.getenv('DB_PORT', '5432'))
        self.database = os.getenv('DB_NAME', 'labor_salary_db')
        self.user = os.getenv('DB_USER', 'postgres')
        self.password = os.getenv('DB_PASSWORD', 'password')
        
    def get_connection_string(self) -> str:
        """Get PostgreSQL connection string"""
        return f"host={self.host} port={self.port} dbname={self.database} user={self.user} password={self.password}"
    
    def get_connection_params(self) -> dict:
        """Get connection parameters as dictionary"""
        return {
            'host': self.host,
            'port': self.port,
            'database': self.database,
            'user': self.user,
            'password': self.password
        }
    
    @classmethod
    def from_file(cls, config_file: str = '.env'):
        """Load configuration from .env file"""
        config = cls()
        
        if os.path.exists(config_file):
            with open(config_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        try:
                            key, value = line.split('=', 1)
                            key = key.strip()
                            value = value.strip().strip('"').strip("'")
                            
                            if key == 'DB_HOST':
                                config.host = value
                            elif key == 'DB_PORT':
                                config.port = int(value)
                            elif key == 'DB_NAME':
                                config.database = value
                            elif key == 'DB_USER':
                                config.user = value
                            elif key == 'DB_PASSWORD':
                                config.password = value
                        except ValueError:
                            continue
        
        return config
    
    def save_to_file(self, config_file: str = '.env'):
        """Save configuration to .env file"""
        with open(config_file, 'w') as f:
            f.write("# PostgreSQL Database Configuration\n")
            f.write("# DO NOT commit this file to version control!\n\n")
            f.write(f"DB_HOST={self.host}\n")
            f.write(f"DB_PORT={self.port}\n")
            f.write(f"DB_NAME={self.database}\n")
            f.write(f"DB_USER={self.user}\n")
            f.write(f"DB_PASSWORD={self.password}\n")
    
    def __repr__(self):
        return f"DatabaseConfig(host={self.host}, port={self.port}, database={self.database}, user={self.user})"


