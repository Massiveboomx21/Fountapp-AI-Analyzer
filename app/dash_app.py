"""
Dash Application Setup για AI Document Analyzer
"""
import dash
from dash import dcc, html
import dash_bootstrap_components as dbc
from config import config
from ui.layouts import create_main_layout
from utils.logger import setup_logger

logger = setup_logger()

def create_app():
    """Δημιουργία και ρύθμιση Dash εφαρμογής"""
    
    # Δημιουργία Dash app με Bootstrap theme
    app = dash.Dash(
        __name__,
        external_stylesheets=[
            dbc.themes.BOOTSTRAP,
            dbc.icons.FONT_AWESOME,
            "https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap"
        ],
        suppress_callback_exceptions=True,
        title="AI Document Analyzer"
    )
    
    # Custom CSS
    app.index_string = '''
    <!DOCTYPE html>
    <html>
        <head>
            {%metas%}
            <title>{%title%}</title>
            {%favicon%}
            {%css%}
            <style>
                body {
                    font-family: 'Inter', sans-serif;
                    background-color: #f8f9fa;
                }
                .main-container {
                    padding: 20px;
                    max-width: 1400px;
                    margin: 0 auto;
                }
                .card-custom {
                    border: none;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                    border-radius: 8px;
                }
                .header-title {
                    color: #2c3e50;
                    font-weight: 600;
                    margin-bottom: 0;
                }
                .status-badge {
                    font-size: 0.85em;
                    padding: 0.4em 0.8em;
                }
                .file-item {
                    border-left: 4px solid #007bff;
                    background-color: white;
                    margin-bottom: 10px;
                    padding: 15px;
                    border-radius: 0 8px 8px 0;
                    box-shadow: 0 1px 3px rgba(0,0,0,0.1);
                }
                .progress-custom {
                    height: 8px;
                    border-radius: 4px;
                }
                .keyword-tag {
                    background-color: #e3f2fd;
                    color: #1976d2;
                    padding: 0.3em 0.6em;
                    border-radius: 12px;
                    font-size: 0.85em;
                    margin: 0.2em;
                    display: inline-block;
                }
                .category-tag {
                    background-color: #f3e5f5;
                    color: #7b1fa2;
                    padding: 0.3em 0.6em;
                    border-radius: 12px;
                    font-size: 0.85em;
                    margin: 0.2em;
                    display: inline-block;
                }
                .sentiment-positive {
                    color: #4caf50;
                    font-weight: 500;
                }
                .sentiment-negative {
                    color: #f44336;
                    font-weight: 500;
                }
                .sentiment-neutral {
                    color: #ff9800;
                    font-weight: 500;
                }
                .loading-overlay {
                    position: fixed;
                    top: 0;
                    left: 0;
                    width: 100%;
                    height: 100%;
                    background-color: rgba(0,0,0,0.5);
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    z-index: 9999;
                }
                .stats-card {
                    text-align: center;
                    padding: 20px;
                }
                .stats-number {
                    font-size: 2.5rem;
                    font-weight: 700;
                    color: #2c3e50;
                }
                .stats-label {
                    color: #6c757d;
                    font-size: 0.9rem;
                    text-transform: uppercase;
                    letter-spacing: 0.5px;
                }
            </style>
        </head>
        <body>
            {%app_entry%}
            <footer>
                {%config%}
                {%scripts%}
                {%renderer%}
            </footer>
        </body>
    </html>
    '''
    
    # Ρύθμιση layout
    app.layout = create_main_layout()
    
    # Import callbacks after app creation
    from app.callbacks import register_callbacks
    register_callbacks(app)
    
    logger.info("Dash εφαρμογή δημιουργήθηκε επιτυχώς")
    
    return app
