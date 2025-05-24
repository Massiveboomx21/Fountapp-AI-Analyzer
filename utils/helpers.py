"""
Helper functions για AI Document Analyzer
"""
import os
import re
import mimetypes
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Union

def format_file_size(size_bytes: int) -> str:
    """Μετατροπή bytes σε human-readable format"""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024**2:
        return f"{size_bytes/1024:.1f} KB"
    elif size_bytes < 1024**3:
        return f"{size_bytes/(1024**2):.1f} MB"
    else:
        return f"{size_bytes/(1024**3):.1f} GB"

def format_duration(seconds: float) -> str:
    """Μετατροπή seconds σε human-readable duration"""
    if seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        minutes = int(seconds // 60)
        remaining_seconds = seconds % 60
        return f"{minutes}m {remaining_seconds:.0f}s"
    else:
        hours = int(seconds // 3600)
        remaining_minutes = int((seconds % 3600) // 60)
        return f"{hours}h {remaining_minutes}m"

def safe_filename(filename: str) -> str:
    """Δημιουργία ασφαλούς ονόματος αρχείου"""
    # Αφαίρεση ή αντικατάσταση μη επιτρεπόμενων χαρακτήρων
    safe_name = re.sub(r'[<>:"/\\|?*]', '_', filename)
    safe_name = re.sub(r'\s+', '_', safe_name)  # Αντικατάσταση spaces
    safe_name = safe_name.strip('._')  # Αφαίρεση dots/underscores από άκρα
    
    # Περιορισμός μήκους
    if len(safe_name) > 100:
        name_part = safe_name[:80]
        ext_part = safe_name[-15:] if '.' in safe_name[-15:] else ''
        safe_name = name_part + '...' + ext_part
    
    return safe_name or 'unnamed_file'

def get_file_type_icon(file_extension: str) -> str:
    """Επιστροφή FontAwesome icon για τύπο αρχείου"""
    icon_map = {
        '.pdf': 'fas fa-file-pdf',
        '.docx': 'fas fa-file-word',
        '.doc': 'fas fa-file-word',
        '.txt': 'fas fa-file-alt',
        '.png': 'fas fa-file-image',
        '.jpg': 'fas fa-file-image',
        '.jpeg': 'fas fa-file-image',
        '.gif': 'fas fa-file-image',
        '.bmp': 'fas fa-file-image',
        '.xlsx': 'fas fa-file-excel',
        '.xls': 'fas fa-file-excel',
        '.pptx': 'fas fa-file-powerpoint',
        '.ppt': 'fas fa-file-powerpoint',
    }
    
    return icon_map.get(file_extension.lower(), 'fas fa-file')

def validate_path(path: Union[str, Path]) -> Dict:
    """Επικύρωση μονοπατιού αρχείου ή φακέλου"""
    path = Path(path) if isinstance(path, str) else path
    
    validation = {
        'is_valid': False,
        'exists': False,
        'is_file': False,
        'is_directory': False,
        'is_readable': False,
        'is_writable': False,
        'size': 0,
        'warnings': []
    }
    
    try:
        validation['exists'] = path.exists()
        
        if validation['exists']:
            validation['is_file'] = path.is_file()
            validation['is_directory'] = path.is_dir()
            validation['is_readable'] = os.access(path, os.R_OK)
            validation['is_writable'] = os.access(path, os.W_OK)
            
            if validation['is_file']:
                validation['size'] = path.stat().st_size
        else:
            validation['warnings'].append(f"Το μονοπάτι δεν υπάρχει: {path}")
        
        validation['is_valid'] = validation['exists'] and validation['is_readable']
        
    except Exception as e:
        validation['warnings'].append(f"Σφάλμα επικύρωσης: {str(e)}")
    
    return validation

def clean_text_for_display(text: str, max_length: int = 200) -> str:
    """Καθαρισμός κειμένου για εμφάνιση στο UI"""
    if not text:
        return ""
    
    # Αφαίρεση πολλαπλών line breaks και spaces
    cleaned = re.sub(r'\s+', ' ', text.strip())
    
    # Truncate αν χρειάζεται
    if len(cleaned) > max_length:
        cleaned = cleaned[:max_length - 3] + "..."
    
    return cleaned

def extract_keywords_simple(text: str, max_keywords: int = 10) -> List[str]:
    """Απλή εξαγωγή keywords (fallback αν το AI αποτύχει)"""
    if not text:
        return []
    
    # Καθαρισμός κειμένου
    text = re.sub(r'[^\w\s]', ' ', text.lower())
    words = text.split()
    
    # Αφαίρεση stop words (απλή λίστα)
    stop_words = {
        'και', 'ή', 'αλλά', 'όμως', 'για', 'με', 'από', 'στο', 'στη', 'στον', 'στην',
        'του', 'της', 'των', 'τον', 'την', 'τα', 'το', 'ο', 'η', 'οι', 'ένα', 'μια',
        'είναι', 'ήταν', 'θα', 'να', 'σε', 'κι', 'κα', 'πω', 'πως', 'που', 'ποια',
        'the', 'and', 'or', 'but', 'for', 'with', 'from', 'to', 'in', 'on', 'at',
        'is', 'was', 'are', 'were', 'be', 'been', 'have', 'has', 'had', 'a', 'an'
    }
    
    # Φιλτράρισμα και μέτρηση
    word_count = {}
    for word in words:
        if len(word) > 3 and word not in stop_words:
            word_count[word] = word_count.get(word, 0) + 1
    
    # Ταξινόμηση και επιστροφή top keywords
    sorted_words = sorted(word_count.items(), key=lambda x: x[1], reverse=True)
    return [word for word, count in sorted_words[:max_keywords]]

def categorize_by_keywords(keywords: List[str]) -> List[str]:
    """Απλή κατηγοριοποίηση βάσει keywords"""
    categories = []
    keyword_str = ' '.join(keywords).lower()
    
    category_keywords = {
        'Νομικό': ['νόμος', 'δικαστήριο', 'συμβόλαιο', 'δικηγόρος', 'αγωγή', 'κανονισμός'],
        'Οικονομικό': ['χρήματα', 'τράπεζα', 'επένδυση', 'οικονομία', 'φόρος', 'budget'],
        'Τεχνολογικό': ['τεχνολογία', 'software', 'hardware', 'κώδικας', 'προγραμματισμός'],
        'Εκπαιδευτικό': ['σχολείο', 'μάθημα', 'εκπαίδευση', 'φοιτητής', 'διδασκαλία'],
        'Ιατρικό': ['υγεία', 'γιατρός', 'ασθένεια', 'θεραπεία', 'φάρμακο', 'νοσοκομείο'],
        'Διοικητικό': ['διοίκηση', 'γραφείο', 'υπάλληλος', 'διαδικασία', 'έγγραφο']
    }
    
    for category, cat_keywords in category_keywords.items():
        if any(kw in keyword_str for kw in cat_keywords):
            categories.append(category)
    
    return categories[:3] if categories else ['Γενικό']

def estimate_reading_time(text: str, words_per_minute: int = 200) -> int:
    """Εκτίμηση χρόνου ανάγνωσης σε λεπτά"""
    if not text:
        return 0
    
    word_count = len(text.split())
    minutes = max(1, round(word_count / words_per_minute))
    return minutes

def get_file_encoding(file_path: Union[str, Path]) -> str:
    """Ανίχνευση encoding αρχείου"""
    try:
        import chardet
        
        with open(file_path, 'rb') as file:
            raw_data = file.read(10000)  # Διάβασμα πρώτων 10KB
            result = chardet.detect(raw_data)
            return result.get('encoding', 'utf-8')
    except ImportError:
        # Fallback αν δεν υπάρχει chardet
        return 'utf-8'
    except Exception:
        return 'utf-8'

def create_backup_filename(original_path: Union[str, Path]) -> Path:
    """Δημιουργία backup filename"""
    path = Path(original_path)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    backup_name = f"{path.stem}_backup_{timestamp}{path.suffix}"
    return path.parent / backup_name

def sanitize_for_json(data: Union[str, Dict, List]) -> Union[str, Dict, List]:
    """Καθαρισμός δεδομένων για JSON serialization"""
    if isinstance(data, str):
        # Αφαίρεση non-printable characters
        return ''.join(char for char in data if char.isprintable() or char.isspace())
    elif isinstance(data, dict):
        return {key: sanitize_for_json(value) for key, value in data.items()}
    elif isinstance(data, list):
        return [sanitize_for_json(item) for item in data]
    else:
        return data

def chunk_list(lst: List, chunk_size: int) -> List[List]:
    """Διαίρεση λίστας σε chunks"""
    return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]

def merge_dictionaries(*dicts) -> Dict:
    """Συνδυασμός πολλαπλών dictionaries"""
    result = {}
    for d in dicts:
        if isinstance(d, dict):
            result.update(d)
    return result

def format_timestamp(timestamp: Optional[Union[str, datetime]] = None) -> str:
    """Μορφοποίηση timestamp για εμφάνιση"""
    if timestamp is None:
        timestamp = datetime.now()
    elif isinstance(timestamp, str):
        try:
            timestamp = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        except ValueError:
            return "Μη έγκυρη ημερομηνία"
    
    # Ελληνική μορφοποίηση
    months = [
        'Ιαν', 'Φεβ', 'Μαρ', 'Απρ', 'Μαϊ', 'Ιουν',
        'Ιουλ', 'Αυγ', 'Σεπ', 'Οκτ', 'Νοε', 'Δεκ'
    ]
    
    day = timestamp.day
    month = months[timestamp.month - 1]
    year = timestamp.year
    time_str = timestamp.strftime('%H:%M')
    
    return f"{day} {month} {year}, {time_str}"

def create_safe_directory(path: Union[str, Path]) -> bool:
    """Δημιουργία φακέλου με ασφάλεια"""
    try:
        Path(path).mkdir(parents=True, exist_ok=True)
        return True
    except Exception:
        return False