"""
Llama AI Client για AI Document Analyzer
"""
import requests
import json
import time
from typing import Dict, List, Optional
from config import config
from utils.logger import setup_logger

logger = setup_logger()

class LlamaClient:
    """Client για επικοινωνία με Ollama Llama model"""
    
    def __init__(self):
        self.api_url = config.AI_API_URL
        self.model_name = config.AI_MODEL_NAME
        self.timeout = 300  # 5 minutes timeout
        
    def is_model_available(self) -> bool:
        """Έλεγχος αν το model είναι διαθέσιμο"""
        try:
            response = requests.get(f"{self.api_url}/api/tags", timeout=10)
            if response.status_code == 200:
                models = response.json().get('models', [])
                available_models = [model['name'] for model in models]
                return self.model_name in available_models
            return False
        except Exception as e:
            logger.error(f"Σφάλμα ελέγχου model: {e}")
            return False
    
    def generate_summary(self, text: str) -> Dict:
        """Δημιουργία περίληψης κειμένου"""
        prompt = f"""
Διάβασε το παρακάτω κείμενο και δημιούργησε μια σύντομη περίληψη στα ελληνικά.
Η περίληψη πρέπει να είναι 2-3 προτάσεις και να περιλαμβάνει τα κύρια σημεία.

Κείμενο:
{text[:2000]}  # Περιορισμός για μεγάλα κείμενα

Περίληψη:"""

        return self._generate_response(prompt, "summary")
    
    def extract_keywords(self, text: str) -> Dict:
        """Εξαγωγή λέξεων-κλειδιών"""
        prompt = f"""
Από το παρακάτω κείμενο, εξάγαγε τις 10 πιο σημαντικές λέξεις-κλειδιά.
Δώσε τις λέξεις σε μορφή λίστας, χωρισμένες με κόμμα.
Χρησιμοποίησε ελληνικά όπου είναι δυνατό.

Κείμενο:
{text[:2000]}

Λέξεις-κλειδιά:"""

        result = self._generate_response(prompt, "keywords")
        
        # Επεξεργασία για μετατροπή σε λίστα
        if result['success'] and result['content']:
            keywords = [kw.strip() for kw in result['content'].split(',')]
            keywords = [kw for kw in keywords if kw]  # Αφαίρεση κενών
            result['keywords'] = keywords[:10]  # Μέγιστο 10 keywords
        
        return result
    
    def categorize_content(self, text: str) -> Dict:
        """Κατηγοριοποίηση περιεχομένου"""
        prompt = f"""
Ανάλυσε το παρακάτω κείμενο και κατηγοριοποίησέ το.
Επίλεξε έως 3 κατηγορίες από τις παρακάτω:

- Νομικό
- Οικονομικό  
- Τεχνολογικό
- Εκπαιδευτικό
- Ιατρικό
- Επιστημονικό
- Διοικητικό
- Μάρκετινγκ
- Προσωπικό
- Άλλο

Κείμενο:
{text[:2000]}

Κατηγορίες (χωρισμένες με κόμμα):"""

        result = self._generate_response(prompt, "categories")
        
        # Επεξεργασία για μετατροπή σε λίστα
        if result['success'] and result['content']:
            categories = [cat.strip() for cat in result['content'].split(',')]
            categories = [cat for cat in categories if cat]
            result['categories'] = categories[:3]  # Μέγιστο 3 κατηγορίες
        
        return result
    
    def analyze_sentiment(self, text: str) -> Dict:
        """Ανάλυση συναισθήματος κειμένου"""
        prompt = f"""
Ανάλυσε το συναισθηματικό τόνο του παρακάτω κειμένου.
Δώσε μια βαθμολογία από -1.0 (πολύ αρνητικό) έως +1.0 (πολύ θετικό).
Δώσε μόνο τον αριθμό, για παράδειγμα: 0.3

Κείμενο:
{text[:1500]}

Βαθμολογία συναισθήματος:"""

        result = self._generate_response(prompt, "sentiment")
        
        # Επεξεργασία για εξαγωγή αριθμού
        if result['success'] and result['content']:
            try:
                # Εξαγωγή αριθμού από την απάντηση
                import re
                numbers = re.findall(r'-?\d+\.?\d*', result['content'])
                if numbers:
                    sentiment_score = float(numbers[0])
                    # Εξασφάλιση ότι είναι στο εύρος [-1, 1]
                    sentiment_score = max(-1.0, min(1.0, sentiment_score))
                    result['sentiment_score'] = sentiment_score
                else:
                    result['sentiment_score'] = 0.0
            except (ValueError, IndexError):
                result['sentiment_score'] = 0.0
                result['warnings'] = ['Δεν μπόρεσα να εξάγω βαθμολογία συναισθήματος']
        
        return result
    
    def comprehensive_analysis(self, text: str) -> Dict:
        """Πλήρης ανάλυση κειμένου"""
        logger.info("Έναρξη πλήρους ανάλυσης κειμένου")
        start_time = time.time()
        
        results = {
            'success': True,
            'summary': '',
            'keywords': [],
            'categories': [],
            'sentiment_score': 0.0,
            'confidence_score': 0.0,
            'processing_time': 0.0,
            'errors': []
        }
        
        # Περίληψη
        try:
            summary_result = self.generate_summary(text)
            if summary_result['success']:
                results['summary'] = summary_result['content']
            else:
                results['errors'].append(f"Σφάλμα περίληψης: {summary_result.get('error', 'Άγνωστο')}")
        except Exception as e:
            results['errors'].append(f"Εξαίρεση περίληψης: {str(e)}")
        
        # Λέξεις-κλειδιά
        try:
            keywords_result = self.extract_keywords(text)
            if keywords_result['success']:
                results['keywords'] = keywords_result.get('keywords', [])
            else:
                results['errors'].append(f"Σφάλμα keywords: {keywords_result.get('error', 'Άγνωστο')}")
        except Exception as e:
            results['errors'].append(f"Εξαίρεση keywords: {str(e)}")
        
        # Κατηγορίες
        try:
            categories_result = self.categorize_content(text)
            if categories_result['success']:
                results['categories'] = categories_result.get('categories', [])
            else:
                results['errors'].append(f"Σφάλμα κατηγοριών: {categories_result.get('error', 'Άγνωστο')}")
        except Exception as e:
            results['errors'].append(f"Εξαίρεση κατηγοριών: {str(e)}")
        
        # Συναίσθημα
        try:
            sentiment_result = self.analyze_sentiment(text)
            if sentiment_result['success']:
                results['sentiment_score'] = sentiment_result.get('sentiment_score', 0.0)
            else:
                results['errors'].append(f"Σφάλμα sentiment: {sentiment_result.get('error', 'Άγνωστο')}")
        except Exception as e:
            results['errors'].append(f"Εξαίρεση sentiment: {str(e)}")
        
        # Υπολογισμός confidence score
        successful_operations = 4 - len(results['errors'])
        results['confidence_score'] = successful_operations / 4.0
        
        # Χρόνος επεξεργασίας
        results['processing_time'] = time.time() - start_time
        
        # Αν υπάρχουν πολλά σφάλματα, θεωρούμε την ανάλυση ανεπιτυχή
        if len(results['errors']) >= 3:
            results['success'] = False
        
        logger.info(f"Ανάλυση ολοκληρώθηκε σε {results['processing_time']:.2f}s "
                   f"(confidence: {results['confidence_score']:.2f})")
        
        return results
    
    def _generate_response(self, prompt: str, operation_type: str) -> Dict:
        """Βοηθητική συνάρτηση για αποστολή prompts στο model"""
        try:
            logger.debug(f"Αποστολή {operation_type} prompt στο model")
            
            payload = {
                "model": self.model_name,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.3,  # Χαμηλή για πιο συνεπείς αποκρίσεις
                    "top_p": 0.9,
                    "top_k": 40
                }
            }
            
            response = requests.post(
                f"{self.api_url}/api/generate",
                json=payload,
                timeout=self.timeout,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                result = response.json()
                content = result.get('response', '').strip()
                
                return {
                    'success': True,
                    'content': content,
                    'model_info': {
                        'model': self.model_name,
                        'total_duration': result.get('total_duration', 0),
                        'load_duration': result.get('load_duration', 0),
                        'prompt_eval_count': result.get('prompt_eval_count', 0),
                        'eval_count': result.get('eval_count', 0)
                    }
                }
            else:
                error_msg = f"HTTP {response.status_code}: {response.text}"
                logger.error(f"Σφάλμα API για {operation_type}: {error_msg}")
                return {
                    'success': False,
                    'content': '',
                    'error': error_msg
                }
                
        except requests.exceptions.Timeout:
            error_msg = f"Timeout για {operation_type} operation"
            logger.error(error_msg)
            return {'success': False, 'content': '', 'error': error_msg}
            
        except requests.exceptions.ConnectionError:
            error_msg = "Δεν μπόρεσα να συνδεθώ στο Ollama. Βεβαιωθείτε ότι τρέχει."
            logger.error(error_msg)
            return {'success': False, 'content': '', 'error': error_msg}
            
        except Exception as e:
            error_msg = f"Απροσδόκητο σφάλμα για {operation_type}: {str(e)}"
            logger.error(error_msg)
            return {'success': False, 'content': '', 'error': error_msg}
    
    def test_connection(self) -> Dict:
        """Test της σύνδεσης με το AI model"""
        try:
            # Έλεγχος αν το Ollama τρέχει
            response = requests.get(f"{self.api_url}/api/tags", timeout=10)
            
            if response.status_code != 200:
                return {
                    'success': False,
                    'error': f"Ollama δεν απαντά (HTTP {response.status_code})"
                }
            
            # Έλεγχος αν το model είναι διαθέσιμο
            if not self.is_model_available():
                available_models = [m['name'] for m in response.json().get('models', [])]
                return {
                    'success': False,
                    'error': f"Model {self.model_name} δεν είναι διαθέσιμο. "
                            f"Διαθέσιμα: {', '.join(available_models) if available_models else 'Κανένα'}"
                }
            
            # Test με απλό prompt
            test_result = self._generate_response("Γεια σου! Απάντησε με 'Γεια σας!'", "test")
            
            if test_result['success']:
                return {
                    'success': True,
                    'message': f"Model {self.model_name} λειτουργεί επιτυχώς",
                    'model_info': test_result.get('model_info', {})
                }
            else:
                return {
                    'success': False,
                    'error': f"Model test απέτυχε: {test_result.get('error', 'Άγνωστο σφάλμα')}"
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f"Σφάλμα σύνδεσης: {str(e)}"
            }
