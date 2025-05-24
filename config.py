"""
Ρυθμίσεις εφαρμογής AI Document Analyzer
"""
import os
from pathlib import Path

# Βασικές ρυθμίσεις
class Config:
    # Paths
    BASE_DIR = Path(__file__).parent
    DATA_DIR = BASE_DIR / "data"
    DATABASE_DIR = DATA_DIR / "database"
    LOGS_DIR = DATA_DIR / "logs"
    TEMP_DIR = DATA_DIR / "temp"
    
    # Database
    DATABASE_PATH = DATABASE_DIR / "documents.db"
    
    # AI Model Settings
    AI_MODEL_NAME = "llama3.1:8b"  # Default Ollama model
    AI_API_URL = "http://localhost:11434"  # Ollama default URL
    MAX_CHUNK_SIZE = 4000  # Μέγιστο μέγεθος chunk για AI
    
    # Document Processing
    SUPPORTED_FORMATS = {'.pdf', '.docx', '.txt', '.png', '.jpg', '.jpeg'}
    MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
    MAX_DEPTH = 5  # Μέγιστο βάθος φακέλων
    
    # Dash App Settings
    DEBUG = True
    HOST = "127.0.0.1"
    PORT = 8050
    
    # UI Settings
    ITEMS_PER_PAGE = 20
    REFRESH_INTERVAL = 1000  # ms
    
    # Logging
    LOG_LEVEL = "INFO"
    LOG_FORMAT = "{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}"
    
    @classmethod
    def create_directories(cls):
        """Δημιουργία απαραίτητων φακέλων"""
        for directory in [cls.DATA_DIR, cls.DATABASE_DIR, 
                         cls.LOGS_DIR, cls.TEMP_DIR]:
            directory.mkdir(parents=True, exist_ok=True)

# Environment-specific configurations
class DevelopmentConfig(Config):
    DEBUG = True
    LOG_LEVEL = "DEBUG"

class ProductionConfig(Config):
    DEBUG = False
    LOG_LEVEL = "WARNING"

# Default configuration
config = DevelopmentConfig()
