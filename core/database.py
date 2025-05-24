"""
Database Manager για AI Document Analyzer
"""
import sqlite3
import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional
from config import config
from utils.logger import setup_logger

logger = setup_logger()

class DatabaseManager:
    """Διαχείριση database operations"""
    
    def __init__(self):
        self.db_path = config.DATABASE_PATH
    
    def get_connection(self):
        """Δημιουργία σύνδεσης με database"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Για dict-like access
        return conn
    
    def initialize_database(self):
        """Δημιουργία database tables"""
        with self.get_connection() as conn:
            # Table για documents
            conn.execute('''
                CREATE TABLE IF NOT EXISTS documents (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    filepath TEXT UNIQUE NOT NULL,
                    filename TEXT NOT NULL,
                    file_size INTEGER,
                    file_type TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    modified_at TIMESTAMP,
                    processed_at TIMESTAMP,
                    status TEXT DEFAULT 'pending',
                    error_message TEXT
                )
            ''')
            
            # Table για AI analysis results
            conn.execute('''
                CREATE TABLE IF NOT EXISTS analysis_results (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    document_id INTEGER,
                    summary TEXT,
                    keywords TEXT,  -- JSON array
                    categories TEXT,  -- JSON array
                    sentiment_score REAL,
                    confidence_score REAL,
                    processing_time REAL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (document_id) REFERENCES documents (id)
                )
            ''')
            
            # Table για document content chunks
            conn.execute('''
                CREATE TABLE IF NOT EXISTS document_chunks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    document_id INTEGER,
                    chunk_index INTEGER,
                    content TEXT,
                    word_count INTEGER,
                    FOREIGN KEY (document_id) REFERENCES documents (id)
                )
            ''')
            
            # Indexes για καλύτερη απόδοση
            conn.execute('CREATE INDEX IF NOT EXISTS idx_documents_status ON documents(status)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_documents_filepath ON documents(filepath)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_analysis_document_id ON analysis_results(document_id)')
            
            conn.commit()
            logger.info("Database tables δημιουργήθηκαν επιτυχώς")
    
    def add_document(self, filepath: str, filename: str, file_size: int, file_type: str) -> int:
        """Προσθήκη νέου document"""
        with self.get_connection() as conn:
            cursor = conn.execute('''
                INSERT OR REPLACE INTO documents 
                (filepath, filename, file_size, file_type, modified_at)
                VALUES (?, ?, ?, ?, ?)
            ''', (filepath, filename, file_size, file_type, datetime.now()))
            
            document_id = cursor.lastrowid
            conn.commit()
            logger.debug(f"Document προστέθηκε: {filename} (ID: {document_id})")
            return document_id
    
    def update_document_status(self, document_id: int, status: str, error_message: str = None):
        """Ενημέρωση status document"""
        with self.get_connection() as conn:
            conn.execute('''
                UPDATE documents 
                SET status = ?, error_message = ?, processed_at = ?
                WHERE id = ?
            ''', (status, error_message, datetime.now(), document_id))
            conn.commit()
    
    def add_analysis_result(self, document_id: int, summary: str, keywords: List[str], 
                          categories: List[str], sentiment_score: float, 
                          confidence_score: float, processing_time: float):
        """Προσθήκη αποτελεσμάτων ανάλυσης"""
        with self.get_connection() as conn:
            conn.execute('''
                INSERT INTO analysis_results 
                (document_id, summary, keywords, categories, sentiment_score, 
                 confidence_score, processing_time)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (document_id, summary, json.dumps(keywords), json.dumps(categories),
                  sentiment_score, confidence_score, processing_time))
            conn.commit()
    
    def add_document_chunks(self, document_id: int, chunks: List[str]):
        """Προσθήκη chunks εγγράφου"""
        with self.get_connection() as conn:
            for i, chunk in enumerate(chunks):
                word_count = len(chunk.split())
                conn.execute('''
                    INSERT INTO document_chunks 
                    (document_id, chunk_index, content, word_count)
                    VALUES (?, ?, ?, ?)
                ''', (document_id, i, chunk, word_count))
            conn.commit()
    
    def get_documents(self, status: str = None, limit: int = None) -> List[Dict]:
        """Ανάκτηση documents"""
        with self.get_connection() as conn:
            query = "SELECT * FROM documents"
            params = []
            
            if status:
                query += " WHERE status = ?"
                params.append(status)
            
            query += " ORDER BY created_at DESC"
            
            if limit:
                query += " LIMIT ?"
                params.append(limit)
            
            cursor = conn.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]
    
    def get_document_with_analysis(self, document_id: int) -> Optional[Dict]:
        """Ανάκτηση document με analysis results"""
        with self.get_connection() as conn:
            cursor = conn.execute('''
                SELECT d.*, a.summary, a.keywords, a.categories, 
                       a.sentiment_score, a.confidence_score, a.processing_time
                FROM documents d
                LEFT JOIN analysis_results a ON d.id = a.document_id
                WHERE d.id = ?
            ''', (document_id,))
            
            row = cursor.fetchone()
            if row:
                result = dict(row)
                # Parse JSON fields
                if result.get('keywords'):
                    result['keywords'] = json.loads(result['keywords'])
                if result.get('categories'):
                    result['categories'] = json.loads(result['categories'])
                return result
            return None
    
    def search_documents(self, query: str) -> List[Dict]:
        """Αναζήτηση στα documents"""
        with self.get_connection() as conn:
            cursor = conn.execute('''
                SELECT DISTINCT d.* FROM documents d
                LEFT JOIN analysis_results a ON d.id = a.document_id
                LEFT JOIN document_chunks c ON d.id = c.document_id
                WHERE d.filename LIKE ? 
                   OR a.summary LIKE ? 
                   OR a.keywords LIKE ?
                   OR c.content LIKE ?
                ORDER BY d.created_at DESC
            ''', (f'%{query}%', f'%{query}%', f'%{query}%', f'%{query}%'))
            
            return [dict(row) for row in cursor.fetchall()]
    
    def get_statistics(self) -> Dict:
        """Στατιστικά της εφαρμογής"""
        with self.get_connection() as conn:
            stats = {}
            
            # Συνολικά documents
            cursor = conn.execute("SELECT COUNT(*) as total FROM documents")
            stats['total_documents'] = cursor.fetchone()['total']
            
            # Documents by status
            cursor = conn.execute('''
                SELECT status, COUNT(*) as count 
                FROM documents 
                GROUP BY status
            ''')
            stats['by_status'] = {row['status']: row['count'] for row in cursor.fetchall()}
            
            # Documents by type
            cursor = conn.execute('''
                SELECT file_type, COUNT(*) as count 
                FROM documents 
                GROUP BY file_type
            ''')
            stats['by_type'] = {row['file_type']: row['count'] for row in cursor.fetchall()}
            
            return stats
