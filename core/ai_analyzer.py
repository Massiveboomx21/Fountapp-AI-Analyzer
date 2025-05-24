"""
AI Analyzer Manager για AI Document Analyzer
"""
import time
from typing import Dict, List
from models.llama_client import LlamaClient
from core.database import DatabaseManager
from utils.logger import setup_logger

logger = setup_logger()

class AIAnalyzer:
    """Κεντρική κλάση για AI ανάλυση εγγράφων"""
    
    def __init__(self):
        self.llama_client = LlamaClient()
        self.db_manager = DatabaseManager()
        
    def analyze_document(self, document_id: int, text_chunks: List[str]) -> Dict:
        """
        Πλήρης ανάλυση εγγράφου με AI
        
        Args:
            document_id: ID εγγράφου στη database
            text_chunks: Λίστα με chunks κειμένου
            
        Returns:
            Dict με αποτελέσματα ανάλυσης
        """
        logger.info(f"Έναρξη AI ανάλυσης για document ID: {document_id}")
        start_time = time.time()
        
        try:
            # Έλεγχος σύνδεσης με AI model
            connection_test = self.llama_client.test_connection()
            if not connection_test['success']:
                error_msg = f"AI model δεν είναι διαθέσιμο: {connection_test['error']}"
                logger.error(error_msg)
                self.db_manager.update_document_status(document_id, 'failed', error_msg)
                return {
                    'success': False,
                    'error': error_msg,
                    'document_id': document_id
                }
            
            # Συνδυασμός όλων των chunks σε ένα κείμενο για ανάλυση
            full_text = self._combine_chunks(text_chunks)
            
            if not full_text.strip():
                error_msg = "Δεν βρέθηκε κείμενο για ανάλυση"
                logger.warning(error_msg)
                self.db_manager.update_document_status(document_id, 'failed', error_msg)
                return {
                    'success': False,
                    'error': error_msg,
                    'document_id': document_id
                }
            
            # AI ανάλυση
            logger.info(f"Εκτέλεση AI ανάλυσης για {len(full_text)} χαρακτήρες")
            analysis_result = self.llama_client.comprehensive_analysis(full_text)
            
            if not analysis_result['success']:
                error_msg = f"AI ανάλυση απέτυχε: {'; '.join(analysis_result.get('errors', ['Άγνωστο σφάλμα']))}"
                logger.error(error_msg)
                self.db_manager.update_document_status(document_id, 'failed', error_msg)
                return {
                    'success': False,
                    'error': error_msg,
                    'document_id': document_id
                }
            
            # Αποθήκευση αποτελεσμάτων στη database
            try:
                self.db_manager.add_analysis_result(
                    document_id=document_id,
                    summary=analysis_result.get('summary', ''),
                    keywords=analysis_result.get('keywords', []),
                    categories=analysis_result.get('categories', []),
                    sentiment_score=analysis_result.get('sentiment_score', 0.0),
                    confidence_score=analysis_result.get('confidence_score', 0.0),
                    processing_time=analysis_result.get('processing_time', 0.0)
                )
                
                # Ενημέρωση status του document
                self.db_manager.update_document_status(document_id, 'completed')
                
                total_time = time.time() - start_time
                logger.info(f"AI ανάλυση ολοκληρώθηκε επιτυχώς για document {document_id} "
                           f"σε {total_time:.2f}s")
                
                return {
                    'success': True,
                    'document_id': document_id,
                    'summary': analysis_result.get('summary', ''),
                    'keywords': analysis_result.get('keywords', []),
                    'categories': analysis_result.get('categories', []),
                    'sentiment_score': analysis_result.get('sentiment_score', 0.0),
                    'confidence_score': analysis_result.get('confidence_score', 0.0),
                    'processing_time': total_time,
                    'ai_processing_time': analysis_result.get('processing_time', 0.0)
                }
                
            except Exception as e:
                error_msg = f"Σφάλμα αποθήκευσης αποτελεσμάτων: {str(e)}"
                logger.error(error_msg)
                self.db_manager.update_document_status(document_id, 'failed', error_msg)
                return {
                    'success': False,
                    'error': error_msg,
                    'document_id': document_id
                }
                
        except Exception as e:
            error_msg = f"Απροσδόκητο σφάλμα AI ανάλυσης: {str(e)}"
            logger.error(error_msg)
            self.db_manager.update_document_status(document_id, 'failed', error_msg)
            return {
                'success': False,
                'error': error_msg,
                'document_id': document_id
            }
    
    def _combine_chunks(self, chunks: List[str], max_length: int = 8000) -> str:
        """Συνδυασμός chunks σε ένα κείμενο για ανάλυση"""
        if not chunks:
            return ""
        
        # Αν έχουμε μόνο ένα chunk και είναι μικρό, το επιστρέφουμε
        if len(chunks) == 1:
            return chunks[0][:max_length]
        
        # Συνδυασμός chunks μέχρι το μέγιστο όριο
        combined = ""
        for chunk in chunks:
            if len(combined + chunk) <= max_length:
                if combined:
                    combined += "\n\n" + chunk
                else:
                    combined = chunk
            else:
                # Αν δεν χωράει όλο το chunk, παίρνουμε ό,τι χωράει
                remaining_space = max_length - len(combined)
                if remaining_space > 100:  # Αν έχουμε αρκετό χώρο
                    combined += "\n\n" + chunk[:remaining_space-4] + "..."
                break
        
        return combined
    
    def analyze_chunk_individually(self, document_id: int, text_chunks: List[str]) -> Dict:
        """Ανάλυση κάθε chunk ξεχωριστά (για πολύ μεγάλα έγγραφα)"""
        logger.info(f"Έναρξη chunk-by-chunk ανάλυσης για document {document_id}")
        start_time = time.time()
        
        all_summaries = []
        all_keywords = []
        all_categories = []
        sentiment_scores = []
        errors = []
        
        for i, chunk in enumerate(text_chunks):
            logger.debug(f"Ανάλυση chunk {i+1}/{len(text_chunks)}")
            
            try:
                # Περίληψη για κάθε chunk
                summary_result = self.llama_client.generate_summary(chunk)
                if summary_result['success']:
                    all_summaries.append(summary_result['content'])
                
                # Keywords για κάθε chunk
                keywords_result = self.llama_client.extract_keywords(chunk)
                if keywords_result['success']:
                    all_keywords.extend(keywords_result.get('keywords', []))
                
                # Κατηγορίες για κάθε chunk
                categories_result = self.llama_client.categorize_content(chunk)
                if categories_result['success']:
                    all_categories.extend(categories_result.get('categories', []))
                
                # Sentiment για κάθε chunk
                sentiment_result = self.llama_client.analyze_sentiment(chunk)
                if sentiment_result['success']:
                    sentiment_scores.append(sentiment_result.get('sentiment_score', 0.0))
                
            except Exception as e:
                error_msg = f"Σφάλμα ανάλυσης chunk {i+1}: {str(e)}"
                logger.warning(error_msg)
                errors.append(error_msg)
        
        # Συνδυασμός αποτελεσμάτων
        final_summary = self._combine_summaries(all_summaries)
        final_keywords = self._deduplicate_keywords(all_keywords)
        final_categories = self._deduplicate_categories(all_categories)
        final_sentiment = sum(sentiment_scores) / len(sentiment_scores) if sentiment_scores else 0.0
        
        # Υπολογισμός confidence score
        successful_chunks = len(text_chunks) - len(errors)
        confidence_score = successful_chunks / len(text_chunks) if text_chunks else 0.0
        
        # Αποθήκευση αποτελεσμάτων
        try:
            processing_time = time.time() - start_time
            
            self.db_manager.add_analysis_result(
                document_id=document_id,
                summary=final_summary,
                keywords=final_keywords,
                categories=final_categories,
                sentiment_score=final_sentiment,
                confidence_score=confidence_score,
                processing_time=processing_time
            )
            
            self.db_manager.update_document_status(document_id, 'completed')
            
            logger.info(f"Chunk-by-chunk ανάλυση ολοκληρώθηκε για document {document_id}")
            
            return {
                'success': True,
                'document_id': document_id,
                'summary': final_summary,
                'keywords': final_keywords,
                'categories': final_categories,
                'sentiment_score': final_sentiment,
                'confidence_score': confidence_score,
                'processing_time': processing_time,
                'chunks_processed': successful_chunks,
                'total_chunks': len(text_chunks),
                'errors': errors
            }
            
        except Exception as e:
            error_msg = f"Σφάλμα αποθήκευσης chunk analysis: {str(e)}"
            logger.error(error_msg)
            self.db_manager.update_document_status(document_id, 'failed', error_msg)
            return {
                'success': False,
                'error': error_msg,
                'document_id': document_id
            }
    
    def _combine_summaries(self, summaries: List[str]) -> str:
        """Συνδυασμός περιλήψεων από πολλά chunks"""
        if not summaries:
            return "Δεν μπόρεσα να δημιουργήσω περίληψη."
        
        if len(summaries) == 1:
            return summaries[0]
        
        # Δημιουργία ενοποιημένης περίληψης
        combined = "Κύρια σημεία του εγγράφου:\n"
        for i, summary in enumerate(summaries, 1):
            combined += f"{i}. {summary}\n"
        
        return combined.strip()
    
    def _deduplicate_keywords(self, keywords: List[str]) -> List[str]:
        """Αφαίρεση διπλότυπων keywords και επιστροφή των top 10"""
        if not keywords:
            return []
        
        # Μετατροπή σε lowercase για σύγκριση
        seen = set()
        unique_keywords = []
        
        for keyword in keywords:
            keyword_lower = keyword.lower().strip()
            if keyword_lower and keyword_lower not in seen:
                seen.add(keyword_lower)
                unique_keywords.append(keyword.strip())
        
        return unique_keywords[:10]  # Top 10
    
    def _deduplicate_categories(self, categories: List[str]) -> List[str]:
        """Αφαίρεση διπλότυπων κατηγοριών"""
        if not categories:
            return []
        
        # Μετατροπή σε lowercase για σύγκριση
        seen = set()
        unique_categories = []
        
        for category in categories:
            category_lower = category.lower().strip()
            if category_lower and category_lower not in seen:
                seen.add(category_lower)
                unique_categories.append(category.strip())
        
        return unique_categories[:3]  # Top 3
    
    def get_analysis_status(self, document_id: int) -> Dict:
        """Στατιστικά ανάλυσης για έγγραφο"""
        try:
            document = self.db_manager.get_document_with_analysis(document_id)
            
            if not document:
                return {
                    'success': False,
                    'error': f"Document {document_id} δεν βρέθηκε"
                }
            
            return {
                'success': True,
                'document_id': document_id,
                'filename': document['filename'],
                'status': document['status'],
                'has_analysis': bool(document.get('summary')),
                'processed_at': document.get('processed_at'),
                'processing_time': document.get('processing_time'),
                'confidence_score': document.get('confidence_score'),
                'error_message': document.get('error_message')
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f"Σφάλμα ανάκτησης στατιστικών: {str(e)}"
            }
    
    def reanalyze_document(self, document_id: int) -> Dict:
        """Επανάληψη ανάλυσης εγγράφου"""
        logger.info(f"Επανάληψη ανάλυσης για document {document_id}")
        
        try:
            # Ανάκτηση chunks από τη database
            with self.db_manager.get_connection() as conn:
                cursor = conn.execute("""
                    SELECT content FROM document_chunks 
                    WHERE document_id = ? 
                    ORDER BY chunk_index
                """, (document_id,))
                
                chunks = [row['content'] for row in cursor.fetchall()]
            
            if not chunks:
                return {
                    'success': False,
                    'error': f"Δεν βρέθηκαν chunks για document {document_id}"
                }
            
            # Ενημέρωση status σε processing
            self.db_manager.update_document_status(document_id, 'processing')
            
            # Εκτέλεση ανάλυσης
            return self.analyze_document(document_id, chunks)
            
        except Exception as e:
            error_msg = f"Σφάλμα επανάληψης ανάλυσης: {str(e)}"
            logger.error(error_msg)
            self.db_manager.update_document_status(document_id, 'failed', error_msg)
            return {
                'success': False,
                'error': error_msg
            }
