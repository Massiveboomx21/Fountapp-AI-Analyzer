"""
AI Document Analyzer - Κύριο αρχείο εκκίνησης
"""
import sys
from pathlib import Path

# Προσθήκη του project directory στο Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from config import config
from utils.logger import setup_logger
from app.dash_app import create_app
from core.database import DatabaseManager

def initialize_app():
    """Αρχικοποίηση εφαρμογής"""
    # Δημιουργία directories
    config.create_directories()
    
    # Setup logging
    logger = setup_logger()
    logger.info("Εκκίνηση AI Document Analyzer...")
    
    # Αρχικοποίηση database
    db_manager = DatabaseManager()
    db_manager.initialize_database()
    logger.info("Database αρχικοποιήθηκε επιτυχώς")
    
    return logger

def main():
    """Κύρια συνάρτηση εκκίνησης"""
    try:
        # Αρχικοποίηση
        logger = initialize_app()
        
        # Δημιουργία και εκκίνηση Dash app
        app = create_app()
        
        logger.info(f"Εκκίνηση server στο http://{config.HOST}:{config.PORT}")
        
        # Εκκίνηση εφαρμογής
        app.run(
            debug=config.DEBUG,
            host=config.HOST,
            port=config.PORT
        )
        
    except KeyboardInterrupt:
        logger.info("Τερματισμός εφαρμογής από χρήστη")
    except Exception as e:
        logger.error(f"Σφάλμα εκκίνησης: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
