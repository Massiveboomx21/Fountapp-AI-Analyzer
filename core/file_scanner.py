"""
File Scanner για AI Document Analyzer
"""
import os
from pathlib import Path
from typing import List, Dict, Generator
import mimetypes
from config import config
from utils.logger import setup_logger

logger = setup_logger()

class FileScanner:
    """Σάρωση και εντοπισμός αρχείων"""
    
    def __init__(self):
        self.supported_formats = config.SUPPORTED_FORMATS
        self.max_file_size = config.MAX_FILE_SIZE
        self.max_depth = config.MAX_DEPTH
    
    def scan_directory(self, directory_path: str, recursive: bool = True) -> Generator[Dict, None, None]:
        """
        Σάρωση φακέλου για υποστηριζόμενα αρχεία
        
        Args:
            directory_path: Μονοπάτι φακέλου
            recursive: Αν θα σαρώσει υποφακέλους
            
        Yields:
            Dict με πληροφορίες αρχείου
        """
        directory = Path(directory_path)
        
        if not directory.exists():
            logger.error(f"Ο φάκελος δεν υπάρχει: {directory_path}")
            return
        
        if not directory.is_dir():
            logger.error(f"Το μονοπάτι δεν είναι φάκελος: {directory_path}")
            return
        
        logger.info(f"Έναρξη σάρωσης φακέλου: {directory_path}")
        
        try:
            if recursive:
                files = self._scan_recursive(directory, 0)
            else:
                files = self._scan_single_directory(directory)
            
            total_files = 0
            for file_info in files:
                total_files += 1
                yield file_info
            
            logger.info(f"Σάρωση ολοκληρώθηκε. Βρέθηκαν {total_files} αρχεία")
            
        except PermissionError as e:
            logger.error(f"Δεν υπάρχει άδεια πρόσβασης: {e}")
        except Exception as e:
            logger.error(f"Σφάλμα κατά τη σάρωση: {e}")
    
    def _scan_recursive(self, directory: Path, current_depth: int) -> Generator[Dict, None, None]:
        """Recursive σάρωση φακέλου"""
        if current_depth >= self.max_depth:
            logger.warning(f"Συμπλήρωση μέγιστου βάθους ({self.max_depth}) σε: {directory}")
            return
        
        try:
            # Σάρωση αρχείων στον τρέχοντα φάκελο
            for file_info in self._scan_single_directory(directory):
                yield file_info
            
            # Σάρωση υποφακέλων
            for item in directory.iterdir():
                if item.is_dir() and not self._is_hidden_directory(item):
                    yield from self._scan_recursive(item, current_depth + 1)
                    
        except PermissionError:
            logger.warning(f"Δεν υπάρχει άδεια πρόσβασης στον φάκελο: {directory}")
        except Exception as e:
            logger.error(f"Σφάλμα σάρωσης φακέλου {directory}: {e}")
    
    def _scan_single_directory(self, directory: Path) -> Generator[Dict, None, None]:
        """Σάρωση ενός φακέλου (όχι recursive)"""
        try:
            for file_path in directory.iterdir():
                if file_path.is_file():
                    file_info = self._get_file_info(file_path)
                    if file_info and self._is_supported_file(file_info):
                        yield file_info
                        
        except PermissionError:
            logger.warning(f"Δεν υπάρχει άδεια πρόσβασης στον φάκελο: {directory}")
        except Exception as e:
            logger.error(f"Σφάλμα ανάγνωσης φακέλου {directory}: {e}")
    
    def _get_file_info(self, file_path: Path) -> Dict:
        """Εξαγωγή πληροφοριών αρχείου"""
        try:
            stat = file_path.stat()
            
            file_info = {
                'filepath': str(file_path.absolute()),
                'filename': file_path.name,
                'file_size': stat.st_size,
                'file_extension': file_path.suffix.lower(),
                'modified_time': stat.st_mtime,
                'created_time': stat.st_ctime,
                'is_readable': os.access(file_path, os.R_OK),
                'mime_type': self._get_mime_type(file_path)
            }
            
            return file_info
            
        except (OSError, PermissionError) as e:
            logger.warning(f"Δεν μπόρεσα να διαβάσω το αρχείο {file_path}: {e}")
            return None
    
    def _get_mime_type(self, file_path: Path) -> str:
        """Εντοπισμός MIME type αρχείου"""
        try:
            mime_type, _ = mimetypes.guess_type(str(file_path))
            return mime_type or 'unknown'
        except Exception:
            return 'unknown'
    
    def _is_supported_file(self, file_info: Dict) -> bool:
        """Έλεγχος αν το αρχείο υποστηρίζεται"""
        # Έλεγχος επέκτασης
        if file_info['file_extension'] not in self.supported_formats:
            return False
        
        # Έλεγχος μεγέθους
        if file_info['file_size'] > self.max_file_size:
            logger.warning(f"Αρχείο πολύ μεγάλο: {file_info['filename']} ({file_info['file_size']} bytes)")
            return False
        
        # Έλεγχος αν είναι αναγνώσιμο
        if not file_info['is_readable']:
            logger.warning(f"Αρχείο μη αναγνώσιμο: {file_info['filename']}")
            return False
        
        return True
    
    def _is_hidden_directory(self, directory: Path) -> bool:
        """Έλεγχος αν ο φάκελος είναι κρυφός"""
        return directory.name.startswith('.')
    
    def get_directory_stats(self, directory_path: str) -> Dict:
        """Στατιστικά φακέλου"""
        stats = {
            'total_files': 0,
            'supported_files': 0,
            'total_size': 0,
            'by_extension': {},
            'by_size_range': {'small': 0, 'medium': 0, 'large': 0},
            'errors': 0
        }
        
        try:
            for file_info in self.scan_directory(directory_path):
                stats['total_files'] += 1
                stats['total_size'] += file_info['file_size']
                
                # Group by extension
                ext = file_info['file_extension']
                stats['by_extension'][ext] = stats['by_extension'].get(ext, 0) + 1
                
                # Group by size
                size = file_info['file_size']
                if size < 1024 * 1024:  # < 1MB
                    stats['by_size_range']['small'] += 1
                elif size < 10 * 1024 * 1024:  # < 10MB
                    stats['by_size_range']['medium'] += 1
                else:
                    stats['by_size_range']['large'] += 1
                
                if self._is_supported_file(file_info):
                    stats['supported_files'] += 1
            
        except Exception as e:
            logger.error(f"Σφάλμα υπολογισμού στατιστικών: {e}")
            stats['errors'] += 1
        
        return stats
    
    def validate_directory(self, directory_path: str) -> Dict:
        """Επικύρωση φακέλου πριν τη σάρωση"""
        validation = {
            'is_valid': False,
            'exists': False,
            'is_directory': False,
            'is_readable': False,
            'estimated_files': 0,
            'warnings': []
        }
        
        directory = Path(directory_path)
        
        # Έλεγχος ύπαρξης
        validation['exists'] = directory.exists()
        if not validation['exists']:
            validation['warnings'].append(f"Ο φάκελος δεν υπάρχει: {directory_path}")
            return validation
        
        # Έλεγχος αν είναι φάκελος
        validation['is_directory'] = directory.is_dir()
        if not validation['is_directory']:
            validation['warnings'].append(f"Το μονοπάτι δεν είναι φάκελος: {directory_path}")
            return validation
        
        # Έλεγχος δικαιωμάτων ανάγνωσης
        validation['is_readable'] = os.access(directory, os.R_OK)
        if not validation['is_readable']:
            validation['warnings'].append(f"Δεν υπάρχει άδεια ανάγνωσης: {directory_path}")
            return validation
        
        # Εκτίμηση αριθμού αρχείων
        try:
            file_count = sum(1 for _ in directory.rglob('*') if _.is_file())
            validation['estimated_files'] = file_count
            
            if file_count > 10000:
                validation['warnings'].append(f"Μεγάλος αριθμός αρχείων ({file_count}). Η επεξεργασία μπορεί να πάρει χρόνο.")
        
        except Exception as e:
            validation['warnings'].append(f"Δεν μπόρεσα να εκτιμήσω τον αριθμό αρχείων: {e}")
        
        validation['is_valid'] = (validation['exists'] and 
                                validation['is_directory'] and 
                                validation['is_readable'])
        
        return validation
