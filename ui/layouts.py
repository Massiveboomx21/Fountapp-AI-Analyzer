"""
UI Layouts για AI Document Analyzer
"""
from dash import dcc, html
import dash_bootstrap_components as dbc

def create_main_layout():
    """Δημιουργία κύριου layout της εφαρμογής"""
    
    return html.Div([
        # Stores για δεδομένα
        dcc.Store(id='documents-store', data=[]),
        dcc.Store(id='selected-folder-store', data=''),
        dcc.Store(id='processing-status-store', data={'active': False, 'progress': 0}),
        
        # Intervals για auto-refresh
        dcc.Interval(
            id='refresh-interval',
            interval=2000,  # 2 seconds
            n_intervals=0,
            disabled=True
        ),
        
        # Header
        create_header(),
        
        # Main Content
        html.Div([
            dbc.Container([
                dbc.Row([
                    # Left Panel - Controls
                    dbc.Col([
                        create_control_panel()
                    ], width=4),
                    
                    # Right Panel - Results
                    dbc.Col([
                        create_results_panel()
                    ], width=8)
                ], className="g-4"),
                
                # Stats Row
                html.Hr(),
                create_stats_section(),
                
            ], fluid=True, className="main-container")
        ]),
        
        # Loading overlay
        html.Div(
            id='loading-overlay',
            children=[
                dbc.Spinner(
                    html.Div([
                        html.H4("Επεξεργασία εγγράφων...", className="text-white mb-3"),
                        dbc.Progress(id="progress-bar", value=0, className="mb-2"),
                        html.P(id="progress-text", className="text-white", children="Προετοιμασία...")
                    ]),
                    size="lg",
                    color="primary"
                )
            ],
            className="loading-overlay",
            style={'display': 'none'}
        )
    ])

def create_header():
    """Δημιουργία header"""
    return dbc.Navbar([
        dbc.Container([
            dbc.Row([
                dbc.Col([
                    html.Div([
                        html.I(className="fas fa-brain me-2", style={'color': '#007bff'}),
                        html.Span("AI Document Analyzer", className="header-title fs-3")
                    ])
                ], width="auto"),
                dbc.Col([
                    dbc.Badge(
                        "Powered by Llama 3.1",
                        color="info",
                        className="ms-2"
                    )
                ], width="auto")
            ], align="center", className="w-100", justify="between")
        ], fluid=True)
    ], color="white", className="mb-4 shadow-sm")

def create_control_panel():
    """Δημιουργία panel ελέγχων"""
    return dbc.Card([
        dbc.CardHeader([
            html.H5([
                html.I(className="fas fa-cog me-2"),
                "Ρυθμίσεις Ανάλυσης"
            ], className="mb-0")
        ]),
        dbc.CardBody([
            # Folder Selection
            html.Div([
                html.Label("Επιλογή Φακέλου:", className="form-label fw-bold"),
                dbc.InputGroup([
                    dbc.Input(
                        id="folder-path-input",
                        placeholder="C:\\Users\\...\\Documents",
                        value="",
                        type="text"
                    ),
                    dbc.Button(
                        [html.I(className="fas fa-folder-open")],
                        id="browse-folder-btn",
                        color="outline-secondary",
                        n_clicks=0
                    )
                ], className="mb-3"),
                
                # Folder validation
                html.Div(id="folder-validation", className="mb-3")
            ]),
            
            # Processing Options
            html.Hr(),
            html.H6("Επιλογές Επεξεργασίας:", className="fw-bold"),
            
            dbc.Checklist(
                id="processing-options",
                options=[
                    {"label": "Recursive σάρωση υποφακέλων", "value": "recursive"},
                    {"label": "Συμπερίληψη εικόνων (OCR)", "value": "include_images"},
                    {"label": "Λεπτομερής ανάλυση", "value": "detailed_analysis"}
                ],
                value=["recursive", "include_images"],
                className="mb-3"
            ),
            
            # File Types
            html.Label("Τύποι Αρχείων:", className="form-label fw-bold"),
            dbc.Checklist(
                id="file-types",
                options=[
                    {"label": "PDF", "value": "pdf"},
                    {"label": "Word (DOCX)", "value": "docx"},
                    {"label": "Text (TXT)", "value": "txt"},
                    {"label": "Εικόνες (PNG, JPG)", "value": "images"}
                ],
                value=["pdf", "docx", "txt", "images"],
                className="mb-3"
            ),
            
            # Action Buttons
            html.Hr(),
            dbc.Row([
                dbc.Col([
                    dbc.Button(
                        [
                            html.I(className="fas fa-play me-2"),
                            "Έναρξη Ανάλυσης"
                        ],
                        id="start-analysis-btn",
                        color="primary",
                        size="lg",
                        disabled=True,
                        className="w-100 mb-2"
                    )
                ], width=12),
                dbc.Col([
                    dbc.Button(
                        [
                            html.I(className="fas fa-stop me-2"),
                            "Διακοπή"
                        ],
                        id="stop-analysis-btn",
                        color="danger",
                        size="sm",
                        disabled=True,
                        className="w-100"
                    )
                ], width=6),
                dbc.Col([
                    dbc.Button(
                        [
                            html.I(className="fas fa-refresh me-2"),
                            "Ανανέωση"
                        ],
                        id="refresh-btn",
                        color="secondary",
                        size="sm",
                        className="w-100"
                    )
                ], width=6)
            ])
        ])
    ], className="card-custom")

def create_results_panel():
    """Δημιουργία panel αποτελεσμάτων"""
    return dbc.Card([
        dbc.CardHeader([
            dbc.Row([
                dbc.Col([
                    html.H5([
                        html.I(className="fas fa-file-alt me-2"),
                        "Αποτελέσματα Ανάλυσης"
                    ], className="mb-0")
                ], width="auto"),
                dbc.Col([
                    dbc.InputGroup([
                        dbc.Input(
                            id="search-input",
                            placeholder="Αναζήτηση...",
                            type="text",
                            size="sm"
                        ),
                        dbc.Button(
                            html.I(className="fas fa-search"),
                            id="search-btn",
                            color="outline-secondary",
                            size="sm"
                        )
                    ], size="sm")
                ], width="auto")
            ], justify="between", align="center")
        ]),
        dbc.CardBody([
            # Filters
            dbc.Row([
                dbc.Col([
                    dbc.Select(
                        id="status-filter",
                        options=[
                            {"label": "Όλα", "value": "all"},
                            {"label": "Επεξεργασμένα", "value": "completed"},
                            {"label": "Σε εξέλιξη", "value": "processing"},
                            {"label": "Αποτυχία", "value": "failed"},
                            {"label": "Αναμονή", "value": "pending"}
                        ],
                        value="all",
                        size="sm"
                    )
                ], width=3),
                dbc.Col([
                    dbc.Select(
                        id="type-filter",
                        options=[
                            {"label": "Όλοι οι τύποι", "value": "all"},
                            {"label": "PDF", "value": "pdf"},
                            {"label": "DOCX", "value": "docx"},
                            {"label": "TXT", "value": "txt"},
                            {"label": "Εικόνες", "value": "images"}
                        ],
                        value="all",
                        size="sm"
                    )
                ], width=3),
                dbc.Col([
                    dbc.Select(
                        id="sort-by",
                        options=[
                            {"label": "Ημερομηνία (νεότερα)", "value": "date_desc"},
                            {"label": "Ημερομηνία (παλαιότερα)", "value": "date_asc"},
                            {"label": "Όνομα (Α-Ω)", "value": "name_asc"},
                            {"label": "Όνομα (Ω-Α)", "value": "name_desc"},
                            {"label": "Μέγεθος", "value": "size_desc"}
                        ],
                        value="date_desc",
                        size="sm"
                    )
                ], width=3)
            ], className="mb-3"),
            
            # Results Container
            html.Div(
                id="results-container",
                children=[
                    html.Div([
                        html.I(className="fas fa-folder-open fa-3x text-muted mb-3"),
                        html.H5("Επιλέξτε φάκελο για να ξεκινήσετε", className="text-muted"),
                        html.P("Χρησιμοποιήστε το πάνελ αριστερά για να επιλέξετε φάκελο και να ξεκινήσετε την ανάλυση.", 
                               className="text-muted")
                    ], className="text-center py-5")
                ]
            ),
            
            # Pagination
            html.Div(
                id="pagination-container",
                className="mt-3"
            )
        ])
    ], className="card-custom")

def create_stats_section():
    """Δημιουργία section στατιστικών"""
    return dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.Div([
                        html.Div("0", className="stats-number", id="total-docs-stat"),
                        html.Div("Συνολικά Έγγραφα", className="stats-label")
                    ], className="stats-card")
                ])
            ], className="card-custom")
        ], width=3),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.Div([
                        html.Div("0", className="stats-number", id="processed-docs-stat"),
                        html.Div("Επεξεργασμένα", className="stats-label")
                    ], className="stats-card")
                ])
            ], className="card-custom")
        ], width=3),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.Div([
                        html.Div("0", className="stats-number", id="processing-docs-stat"),
                        html.Div("Σε Εξέλιξη", className="stats-label")
                    ], className="stats-card")
                ])
            ], className="card-custom")
        ], width=3),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.Div([
                        html.Div("0%", className="stats-number", id="success-rate-stat"),
                        html.Div("Ποσοστό Επιτυχίας", className="stats-label")
                    ], className="stats-card")
                ])
            ], className="card-custom")
        ], width=3)
    ], className="mb-4")

def create_document_card(doc):
    """Δημιουργία card για έγγραφο"""
    # Status badge
    status_colors = {
        'completed': 'success',
        'processing': 'warning',
        'failed': 'danger',
        'pending': 'secondary'
    }
    
    status_labels = {
        'completed': 'Ολοκληρώθηκε',
        'processing': 'Επεξεργασία',
        'failed': 'Αποτυχία',
        'pending': 'Αναμονή'
    }
    
    # File size formatting
    def format_file_size(size_bytes):
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024**2:
            return f"{size_bytes/1024:.1f} KB"
        elif size_bytes < 1024**3:
            return f"{size_bytes/(1024**2):.1f} MB"
        else:
            return f"{size_bytes/(1024**3):.1f} GB"
    
    # Sentiment display
    def get_sentiment_display(score):
        if score > 0.1:
            return html.Span([
                html.I(className="fas fa-smile me-1"),
                f"Θετικό ({score:.2f})"
            ], className="sentiment-positive")
        elif score < -0.1:
            return html.Span([
                html.I(className="fas fa-frown me-1"),
                f"Αρνητικό ({score:.2f})"
            ], className="sentiment-negative")
        else:
            return html.Span([
                html.I(className="fas fa-meh me-1"),
                f"Ουδέτερο ({score:.2f})"
            ], className="sentiment-neutral")
    
    card_content = [
        # Header with filename and status
        dbc.Row([
            dbc.Col([
                html.H6(doc['filename'], className="mb-1 text-truncate"),
                html.Small([
                    html.I(className="fas fa-file me-1"),
                    f"{doc['file_type'].upper()} • {format_file_size(doc['file_size'])}"
                ], className="text-muted")
            ], width=8),
            dbc.Col([
                dbc.Badge(
                    status_labels.get(doc['status'], doc['status']),
                    color=status_colors.get(doc['status'], 'secondary'),
                    className="status-badge"
                )
            ], width=4, className="text-end")
        ], className="mb-2")
    ]
    
    # Analysis results (if completed)
    if doc['status'] == 'completed' and doc.get('summary'):
        card_content.extend([
            html.Hr(className="my-2"),
            
            # Summary
            html.Div([
                html.Strong("Περίληψη: "),
                html.Span(doc['summary'][:200] + ("..." if len(doc['summary']) > 200 else ""))
            ], className="mb-2"),
            
            # Keywords
            html.Div([
                html.Strong("Λέξεις-κλειδιά: "),
                html.Div([
                    html.Span(keyword, className="keyword-tag")
                    for keyword in doc.get('keywords', [])[:5]
                ])
            ], className="mb-2") if doc.get('keywords') else None,
            
            # Categories
            html.Div([
                html.Strong("Κατηγορίες: "),
                html.Div([
                    html.Span(category, className="category-tag")
                    for category in doc.get('categories', [])
                ])
            ], className="mb-2") if doc.get('categories') else None,
            
            # Sentiment
            html.Div([
                html.Strong("Συναίσθημα: "),
                get_sentiment_display(doc.get('sentiment_score', 0))
            ], className="mb-2") if doc.get('sentiment_score') is not None else None,
            
            # Confidence and processing time
            dbc.Row([
                dbc.Col([
                    html.Small([
                        html.Strong("Εμπιστοσύνη: "),
                        f"{doc.get('confidence_score', 0)*100:.1f}%"
                    ], className="text-muted")
                ], width=6),
                dbc.Col([
                    html.Small([
                        html.Strong("Χρόνος: "),
                        f"{doc.get('processing_time', 0):.1f}s"
                    ], className="text-muted")
                ], width=6)
            ])
        ])
    
    # Processing progress (if processing)
    elif doc['status'] == 'processing':
        card_content.append(
            dbc.Progress(
                value=50,  # This should be dynamic
                striped=True,
                animated=True,
                className="progress-custom mt-2"
            )
        )
    
    # Error message (if failed)
    elif doc['status'] == 'failed' and doc.get('error_message'):
        card_content.append(
            dbc.Alert([
                html.I(className="fas fa-exclamation-triangle me-2"),
                doc['error_message'][:100] + ("..." if len(doc['error_message']) > 100 else "")
            ], color="danger", className="mt-2 py-2")
        )
    
    # Filter out None items
    card_content = [item for item in card_content if item is not None]
    
    return html.Div(card_content, className="file-item")
