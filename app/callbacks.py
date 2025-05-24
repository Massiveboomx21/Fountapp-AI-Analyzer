"""
Dash Callbacks για AI Document Analyzer
"""
import os
import threading
import time
from pathlib import Path
from dash import Input, Output, State, callback_context, html
import dash_bootstrap_components as dbc
from tkinter import filedialog
import tkinter as tk

from core.file_scanner import FileScanner
from core.document_processor import DocumentProcessor
from core.ai_analyzer import AIAnalyzer
from core.database import DatabaseManager
from ui.layouts import create_document_card
from utils.logger import setup_logger

logger = setup_logger()

def register_callbacks(app):
    """Εγγραφή όλων των callbacks"""
    
    # Global instances
    file_scanner = FileScanner()
    doc_processor = DocumentProcessor()
    ai_analyzer = AIAnalyzer()
    db_manager = DatabaseManager()
    
    # Processing state
    processing_state = {
        'active': False,
        'thread': None,
        'progress': 0,
        'current_file': '',
        'total_files': 0,
        'processed_files': 0
    }
    
    @app.callback(
        Output('folder-validation', 'children'),
        Output('start-analysis-btn', 'disabled'),
        Input('folder-path-input', 'value')
    )
    def validate_folder(folder_path):
        """Επικύρωση επιλεγμένου φακέλου"""
        if not folder_path or not folder_path.strip():
            return [], True
        
        validation = file_scanner.validate_directory(folder_path)
        
        if validation['is_valid']:
            return [
                dbc.Alert([
                    html.I(className="fas fa-check-circle me-2"),
                    f"Έγκυρος φάκελος ({validation['estimated_files']} εκτιμώμενα αρχεία)"
                ], color="success", className="py-2")
            ], False
        else:
            warnings = validation.get('warnings', ['Μη έγκυρος φάκελος'])
            return [
                dbc.Alert([
                    html.I(className="fas fa-exclamation-triangle me-2"),
                    html.Br().join(warnings)
                ], color="warning", className="py-2")
            ], True
    
    @app.callback(
        Output('folder-path-input', 'value'),
        Input('browse-folder-btn', 'n_clicks'),
        prevent_initial_call=True
    )
    def browse_folder(n_clicks):
        """Άνοιγμα dialog επιλογής φακέλου"""
        if n_clicks > 0:
            try:
                # Create hidden tkinter window
                root = tk.Tk()
                root.withdraw()
                root.attributes('-topmost', True)
                
                # Open folder dialog
                folder_path = filedialog.askdirectory(
                    title="Επιλέξτε φάκελο για ανάλυση"
                )
                
                root.destroy()
                
                if folder_path:
                    return folder_path
            except Exception as e:
                logger.error(f"Σφάλμα επιλογής φακέλου: {e}")
        
        return ""
    
    @app.callback(
        Output('loading-overlay', 'style'),
        Output('refresh-interval', 'disabled'),
        Output('start-analysis-btn', 'children'),
        Output('stop-analysis-btn', 'disabled'),
        Input('start-analysis-btn', 'n_clicks'),
        Input('stop-analysis-btn', 'n_clicks'),
        State('folder-path-input', 'value'),
        State('processing-options', 'value'),
        State('file-types', 'value'),
        prevent_initial_call=True
    )
    def handle_analysis_control(start_clicks, stop_clicks, folder_path, processing_options, file_types):
        """Διαχείριση έναρξης/διακοπής ανάλυσης"""
        ctx = callback_context
        
        if not ctx.triggered:
            return {'display': 'none'}, True, [html.I(className="fas fa-play me-2"), "Έναρξη Ανάλυσης"], True
        
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]
        
        if button_id == 'start-analysis-btn' and start_clicks:
            # Έναρξη ανάλυσης
            if not processing_state['active']:
                processing_state['active'] = True
                processing_state['progress'] = 0
                
                # Start analysis in background thread
                thread = threading.Thread(
                    target=run_analysis,
                    args=(folder_path, processing_options, file_types)
                )
                thread.daemon = True
                thread.start()
                processing_state['thread'] = thread
                
                return (
                    {'display': 'flex'},  # Show loading overlay
                    False,  # Enable refresh interval
                    [html.I(className="fas fa-spinner fa-spin me-2"), "Επεξεργασία..."],
                    False  # Enable stop button
                )
        
        elif button_id == 'stop-analysis-btn' and stop_clicks:
            # Διακοπή ανάλυσης
            processing_state['active'] = False
            
            return (
                {'display': 'none'},  # Hide loading overlay
                True,  # Disable refresh interval
                [html.I(className="fas fa-play me-2"), "Έναρξη Ανάλυσης"],
                True  # Disable stop button
            )
        
        return {'display': 'none'}, True, [html.I(className="fas fa-play me-2"), "Έναρξη Ανάλυσης"], True
    
    def run_analysis(folder_path, processing_options, file_types):
        """Εκτέλεση ανάλυσης σε background thread"""
        try:
            logger.info(f"Έναρξη ανάλυσης φακέλου: {folder_path}")
            
            # Configuration based on user selections
            recursive = 'recursive' in processing_options
            include_images = 'include_images' in processing_options
            detailed_analysis = 'detailed_analysis' in processing_options
            
            # File type mapping
            extensions = set()
            if 'pdf' in file_types:
                extensions.add('.pdf')
            if 'docx' in file_types:
                extensions.add('.docx')
            if 'txt' in file_types:
                extensions.add('.txt')
            if 'images' in file_types and include_images:
                extensions.update(['.png', '.jpg', '.jpeg'])
            
            # Temporarily update scanner supported formats
            original_formats = file_scanner.supported_formats
            file_scanner.supported_formats = extensions
            
            # Scan files
            files = list(file_scanner.scan_directory(folder_path, recursive))
            processing_state['total_files'] = len(files)
            processing_state['processed_files'] = 0
            
            logger.info(f"Βρέθηκαν {len(files)} αρχεία για επεξεργασία")
            
            for i, file_info in enumerate(files):
                if not processing_state['active']:  # Check if stopped
                    break
                
                processing_state['current_file'] = file_info['filename']
                processing_state['progress'] = int((i / len(files)) * 100)
                
                try:
                    # Add document to database
                    doc_id = db_manager.add_document(
                        filepath=file_info['filepath'],
                        filename=file_info['filename'],
                        file_size=file_info['file_size'],
                        file_type=file_info['file_extension'][1:]  # Remove dot
                    )
                    
                    # Update status to processing
                    db_manager.update_document_status(doc_id, 'processing')
                    
                    # Process document
                    logger.info(f"Επεξεργασία: {file_info['filename']}")
                    doc_result = doc_processor.process_document(file_info)
                    
                    if not doc_result['success']:
                        db_manager.update_document_status(doc_id, 'failed', doc_result['error'])
                        continue
                    
                    # Add chunks to database
                    db_manager.add_document_chunks(doc_id, doc_result['chunks'])
                    
                    # AI Analysis
                    if detailed_analysis:
                        ai_result = ai_analyzer.analyze_document(doc_id, doc_result['chunks'])
                    else:
                        # Quick analysis with fewer features
                        combined_text = '\n\n'.join(doc_result['chunks'][:3])  # First 3 chunks only
                        ai_result = ai_analyzer.analyze_document(doc_id, [combined_text])
                    
                    if ai_result['success']:
                        logger.info(f"Ολοκληρώθηκε: {file_info['filename']}")
                    else:
                        logger.warning(f"Αποτυχία AI ανάλυσης: {file_info['filename']}")
                    
                except Exception as e:
                    logger.error(f"Σφάλμα επεξεργασίας {file_info['filename']}: {e}")
                    if 'doc_id' in locals():
                        db_manager.update_document_status(doc_id, 'failed', str(e))
                
                processing_state['processed_files'] += 1
                time.sleep(0.1)  # Small delay to prevent overwhelming
            
            # Restore original formats
            file_scanner.supported_formats = original_formats
            
            logger.info(f"Ανάλυση ολοκληρώθηκε. Επεξεργάστηκαν {processing_state['processed_files']}/{processing_state['total_files']} αρχεία")
            
        except Exception as e:
            logger.error(f"Σφάλμα ανάλυσης: {e}")
        finally:
            processing_state['active'] = False
            processing_state['progress'] = 100
    
    @app.callback(
        Output('progress-bar', 'value'),
        Output('progress-text', 'children'),
        Input('refresh-interval', 'n_intervals'),
        prevent_initial_call=True
    )
    def update_progress(n_intervals):
        """Ενημέρωση progress bar"""
        if processing_state['active']:
            current_file = processing_state.get('current_file', '')
            processed = processing_state.get('processed_files', 0)
            total = processing_state.get('total_files', 0)
            
            if current_file:
                text = f"Επεξεργασία: {current_file[:30]}... ({processed}/{total})"
            else:
                text = f"Επεξεργασία αρχείων... ({processed}/{total})"
            
            return processing_state['progress'], text
        else:
            return 0, "Αναμονή..."
    
    @app.callback(
        Output('results-container', 'children'),
        Output('total-docs-stat', 'children'),
        Output('processed-docs-stat', 'children'),
        Output('processing-docs-stat', 'children'),
        Output('success-rate-stat', 'children'),
        [Input('refresh-interval', 'n_intervals'),
         Input('refresh-btn', 'n_clicks'),
         Input('search-btn', 'n_clicks')],
        [State('search-input', 'value'),
         State('status-filter', 'value'),
         State('type-filter', 'value'),
         State('sort-by', 'value')],
        prevent_initial_call=True
    )
    def update_results(n_intervals, refresh_clicks, search_clicks, search_query, status_filter, type_filter, sort_by):
        """Ενημέρωση αποτελεσμάτων και στατιστικών"""
        try:
            # Get documents from database
            if search_query and search_query.strip():
                documents = db_manager.search_documents(search_query.strip())
            else:
                documents = db_manager.get_documents()
            
            # Apply filters
            if status_filter != 'all':
                documents = [doc for doc in documents if doc['status'] == status_filter]
            
            if type_filter != 'all':
                documents = [doc for doc in documents if doc['file_type'] == type_filter]
            
            # Sort documents
            if sort_by == 'date_desc':
                documents.sort(key=lambda x: x['created_at'], reverse=True)
            elif sort_by == 'date_asc':
                documents.sort(key=lambda x: x['created_at'])
            elif sort_by == 'name_asc':
                documents.sort(key=lambda x: x['filename'].lower())
            elif sort_by == 'name_desc':
                documents.sort(key=lambda x: x['filename'].lower(), reverse=True)
            elif sort_by == 'size_desc':
                documents.sort(key=lambda x: x['file_size'], reverse=True)
            
            # Get enhanced document data (with analysis results)
            enhanced_docs = []
            for doc in documents:
                enhanced_doc = db_manager.get_document_with_analysis(doc['id'])
                if enhanced_doc:
                    enhanced_docs.append(enhanced_doc)
            
            # Create result cards
            if enhanced_docs:
                result_cards = [create_document_card(doc) for doc in enhanced_docs]
            else:
                result_cards = [
                    html.Div([
                        html.I(className="fas fa-inbox fa-3x text-muted mb-3"),
                        html.H5("Δεν βρέθηκαν έγγραφα", className="text-muted"),
                        html.P("Δοκιμάστε να αλλάξετε τα φίλτρα ή να εκτελέσετε νέα ανάλυση.", 
                               className="text-muted")
                    ], className="text-center py-5")
                ]
            
            # Calculate statistics
            all_docs = db_manager.get_documents()
            stats = db_manager.get_statistics()
            
            total_docs = len(all_docs)
            completed_docs = len([doc for doc in all_docs if doc['status'] == 'completed'])
            processing_docs = len([doc for doc in all_docs if doc['status'] == 'processing'])
            
            success_rate = (completed_docs / total_docs * 100) if total_docs > 0 else 0
            
            return (
                result_cards,
                str(total_docs),
                str(completed_docs),
                str(processing_docs),
                f"{success_rate:.1f}%"
            )
            
        except Exception as e:
            logger.error(f"Σφάλμα ενημέρωσης αποτελεσμάτων: {e}")
            return [
                dbc.Alert([
                    html.I(className="fas fa-exclamation-triangle me-2"),
                    f"Σφάλμα φόρτωσης δεδομένων: {str(e)}"
                ], color="danger")
            ], "0", "0", "0", "0%"
