"""
Logging utility for Smart CSV Health Checker
"""
import logging
import sys
from datetime import datetime
from typing import Optional


class CSVHealthLogger:
    """Singleton logger for the application"""
    
    _instance: Optional['CSVHealthLogger'] = None
    _logger: Optional[logging.Logger] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._setup_logger()
        return cls._instance
    
    def _setup_logger(self):
        """Initialize the logger"""
        self._logger = logging.getLogger('csv_health_checker')
        self._logger.setLevel(logging.INFO)
        
        # Prevent duplicate handlers
        if not self._logger.handlers:
            # Console handler
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(logging.INFO)
            
            # Format
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            console_handler.setFormatter(formatter)
            
            self._logger.addHandler(console_handler)
    
    @property
    def logger(self) -> logging.Logger:
        return self._logger
    
    def info(self, message: str):
        """Log info message"""
        self._logger.info(message)
    
    def warning(self, message: str):
        """Log warning message"""
        self._logger.warning(message)
    
    def error(self, message: str):
        """Log error message"""
        self._logger.error(message)
    
    def debug(self, message: str):
        """Log debug message"""
        self._logger.debug(message)
    
    def log_analysis_start(self, rows: int, cols: int):
        """Log analysis start"""
        self.info(f"Starting analysis: {rows:,} rows x {cols} columns")
    
    def log_analysis_complete(self, health_score: float, elapsed: float):
        """Log analysis completion"""
        self.info(f"Analysis complete: Health Score={health_score}, Time={elapsed:.2f}s")
    
    def log_pii_detected(self, count: int, risk_level: str):
        """Log PII detection"""
        self.warning(f"PII Detected: {count} columns, Risk Level: {risk_level}")
    
    def log_file_upload(self, filename: str, size_mb: float):
        """Log file upload"""
        self.info(f"File uploaded: {filename} ({size_mb:.2f} MB)")
    
    def log_error_with_context(self, error: Exception, context: str):
        """Log error with context"""
        self._logger.error(f"{context}: {type(error).__name__} - {str(error)}")


def get_logger() -> CSVHealthLogger:
    """Get the singleton logger instance"""
    return CSVHealthLogger()