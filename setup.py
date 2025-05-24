"""
Windows Setup Script για AI Document Analyzer
"""
import os
import subprocess
import sys
import shutil
import urllib.request
from pathlib import Path
import zipfile

def print_banner():
    """Εμφάνιση banner"""
    print("=" * 60)
    print("🚀 AI Document Analyzer - Windows Setup")
    print("=" * 60)
    print("Αυτό το script θα εγκαταστήσει όλα τα απαραίτητα components")
    print("για την εφαρμογή AI Document Analyzer στα Windows.\n")

def check_python_version():
    """Έλεγχος Python version"""
    print("🐍 Έλεγχος Python version...")
    if sys.version_info < (3, 8):
        print("❌ Απαιτείται Python 3.8 ή νεότερη έκδοση")
        print(f"   Τρέχουσα version: {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
        print("   Κατεβάστε Python από: https://python.org")
        input("Πατήστε Enter για έξοδο...")
        sys.exit(1)
    else:
        print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")

def check_pip():
    """Έλεγχος και αναβάθμιση pip"""
    print("\n📦 Έλεγχος pip...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "--version"], 
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print("✅ pip είναι διαθέσιμο")
        
        # Αναβάθμιση pip
        print("📦 Αναβάθμιση pip...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "pip"], 
                            stdout=subprocess.DEVNULL)
        print("✅ pip αναβαθμίστηκε")
    except subprocess.CalledProcessError:
        print("❌ pip δεν είναι διαθέσιμο")
        print("Παρακαλώ επανεγκαταστήστε Python με pip enabled")
        input("Πατήστε Enter για έξοδο...")
        sys.exit(1)

def create_requirements_file():
    """Δημιουργία requirements.txt"""
    requirements_content = """# Web Framework
dash==2.17.1
dash-bootstrap-components==1.5.0
plotly==5.17.0

# Document Processing
PyPDF2==3.0.1
python-docx==1.1.0
pytesseract==0.3.10
Pillow==10.1.0
python-magic-bin==0.4.14

# AI/ML
requests==2.31.0

# Utilities
pandas==2.1.4
numpy==1.25.2

# Logging
loguru==0.7.2

# GUI
tkinter
"""
    
    with open("requirements.txt", "w", encoding="utf-8") as f:
        f.write(requirements_content)
    print("✅ requirements.txt δημιουργήθηκε")

def install_requirements():
    """Εγκατάσταση Python dependencies"""
    print("\n📦 Εγκατάσταση Python dependencies...")
    
    requirements_path = Path("requirements.txt")
    if not requirements_path.exists():
        print("❌ Το αρχείο requirements.txt δεν βρέθηκε")
        print("Δημιουργία requirements.txt...")
        create_requirements_file()
    
    try:
        print("Αυτό μπορεί να πάρει μερικά λεπτά...")
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "-r", "requirements.txt", "--upgrade", "--user"
        ])
        print("✅ Python dependencies εγκαταστάθηκαν επιτυχώς")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Σφάλμα εγκατάστασης dependencies: {e}")
        print("Δοκιμάστε να εκτελέσετε manually:")
        print("pip install -r requirements.txt")
        return False

def check_ollama():
    """Έλεγχος εγκατάστασης Ollama"""
    print("\n🤖 Έλεγχος Ollama...")
    
    # Έλεγχος αν το ollama.exe υπάρχει
    ollama_paths = [
        "C:\\Users\\{username}\\AppData\\Local\\Programs\\Ollama\\ollama.exe".format(username=os.getenv('USERNAME')),
        "C:\\Program Files\\Ollama\\ollama.exe",
        "ollama.exe"  # Αν είναι στο PATH
    ]
    
    ollama_found = False
    for path in ollama_paths:
        if os.path.exists(path) or shutil.which("ollama"):
            print("✅ Ollama βρέθηκε")
            ollama_found = True
            break
    
    if not ollama_found:
        print("❌ Ollama δεν είναι εγκατεστημένο")
        return False
    
    # Έλεγχος αν τρέχει
    try:
        import requests
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            print("✅ Ollama server τρέχει")
            return True
        else:
            print("⚠️  Ollama είναι εγκατεστημένο αλλά δεν τρέχει")
            return "installed_not_running"
    except Exception:
        print("⚠️  Ollama είναι εγκατεστημένο αλλά δεν τρέχει")
        return "installed_not_running"

def download_ollama():
    """Κατέβασμα Ollama για Windows"""
    print("\n⬇️  Κατέβασμα Ollama για Windows...")
    
    ollama_url = "https://ollama.ai/download/OllamaSetup.exe"
    download_path = Path("OllamaSetup.exe")
    
    try:
        print(f"Κατέβασμα από {ollama_url}...")
        print("Αυτό μπορεί να πάρει μερικά λεπτά...")
        
        urllib.request.urlretrieve(ollama_url, download_path)
        print(f"✅ Ollama κατέβηκε στο {download_path}")
        
        # Εκτέλεση installer
        choice = input("Θέλετε να εκτελέσετε τον installer τώρα? (y/n): ").lower()
        if choice == 'y':
            print("Εκτέλεση Ollama installer...")
            subprocess.run([str(download_path)], check=False)
            print("✅ Ollama installer εκτελέστηκε")
            print("Παρακαλώ ολοκληρώστε την εγκατάσταση και ξανατρέξτε το setup")
        else:
            print(f"Εκτελέστε το {download_path} manually για εγκατάσταση")
        
        return True
    except Exception as e:
        print(f"❌ Σφάλμα κατεβάσματος Ollama: {e}")
        print("Μπορείτε να κατεβάσετε το Ollama manually από: https://ollama.ai")
        return False

def start_ollama():
    """Εκκίνηση Ollama server"""
    print("\n🚀 Εκκίνηση Ollama server...")
    
    try:
        # Δοκιμή εκκίνησης Ollama
        subprocess.Popen(["ollama", "serve"], 
                        stdout=subprocess.DEVNULL, 
                        stderr=subprocess.DEVNULL,
                        creationflags=subprocess.CREATE_NO_WINDOW)
        
        import time
        time.sleep(3)  # Περιμένουμε να ξεκινήσει
        
        # Έλεγχος αν ξεκίνησε
        import requests
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            print("✅ Ollama server ξεκίνησε επιτυχώς")
            return True
        else:
            print("❌ Ollama server δεν ξεκίνησε")
            return False
            
    except Exception as e:
        print(f"❌ Σφάλμα εκκίνησης Ollama: {e}")
        print("Δοκιμάστε να εκκινήσετε manual: ollama serve")
        return False

def setup_ollama_model():
    """Εγκατάσταση Llama model"""
    print("\n🧠 Εγκατάσταση Llama 3.1 8B model...")
    print("ΠΡΟΣΟΧΗ: Αυτό θα κατεβάσει ~4.7GB δεδομένα!")
    
    choice = input("Συνέχεια? (y/n): ").lower()
    if choice != 'y':
        print("⏭️  Παράλειψη εγκατάστασης model")
        return False
    
    try:
        print("Κατέβασμα model... (10-30 λεπτά ανάλογα με internet)")
        print("Μην κλείσετε το παράθυρο!")
        
        result = subprocess.run(
            ["ollama", "pull", "llama3.1:8b"], 
            capture_output=True, text=True, timeout=3600  # 1 hour timeout
        )
        
        if result.returncode == 0:
            print("✅ Llama 3.1 8B model εγκαταστάθηκε επιτυχώς")
            return True
        else:
            print(f"❌ Σφάλμα εγκατάστασης model: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("⏰ Timeout - το κατέβασμα πήρε πολύ χρόνο")
        print("Μπορείτε να συνεχίσετε manual με: ollama pull llama3.1:8b")
        return False
    except FileNotFoundError:
        print("❌ Ollama command δεν βρέθηκε")
        print("Βεβαιωθείτε ότι το Ollama είναι εγκατεστημένο και στο PATH")
        return False
    except Exception as e:
        print(f"❌ Σφάλμα: {e}")
        return False

def check_tesseract():
    """Έλεγχος Tesseract OCR"""
    print("\n🔍 Έλεγχος Tesseract OCR...")
    
    # Συνήθεις τοποθεσίες Tesseract στα Windows
    tesseract_paths = [
        "C:\\Program Files\\Tesseract-OCR\\tesseract.exe",
        "C:\\Program Files (x86)\\Tesseract-OCR\\tesseract.exe",
        "tesseract.exe"  # Αν είναι στο PATH
    ]
    
    for path in tesseract_paths:
        if os.path.exists(path) or shutil.which("tesseract"):
            try:
                result = subprocess.run([path if os.path.exists(path) else "tesseract", "--version"], 
                                      capture_output=True, text=True, timeout=10)
                if result.returncode == 0:
                    version_line = result.stdout.split('\n')[0]
                    print(f"✅ Tesseract βρέθηκε: {version_line}")
                    return True
            except Exception:
                continue
    
    print("❌ Tesseract δεν είναι εγκατεστημένο")
    return False

def setup_tesseract():
    """Οδηγίες για Tesseract OCR"""
    print("\n🔍 Tesseract OCR Setup για Windows:")
    print("1. Κατεβάστε από: https://github.com/UB-Mannheim/tesseract/wiki")
    print("2. Εγκαταστήστε το tesseract-ocr-w64-setup-5.x.x.exe")
    print("3. Κατά την εγκατάσταση επιλέξτε:")
    print("   - Additional language data")
    print("   - Greek language pack")
    print("4. Προσθέστε στο PATH: C:\\Program Files\\Tesseract-OCR")
    
    choice = input("\nΘέλετε να ανοίξω το link για κατέβασμα? (y/n): ").lower()
    if choice == 'y':
        import webbrowser
        webbrowser.open("https://github.com/UB-Mannheim/tesseract/wiki")

def create_directories():
    """Δημιουργία απαραίτητων φακέλων"""
    directories = [
        "data/database",
        "data/logs", 
        "data/temp",
        "app",
        "core", 
        "ui",
        "utils",
        "models",
        "tests"
    ]
    
    print("\n📁 Δημιουργία φακέλων...")
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"✅ {directory}")

def create_init_files():
    """Δημιουργία __init__.py αρχείων"""
    init_dirs = ["app", "core", "ui", "utils", "models", "tests"]
    
    print("\n📄 Δημιουργία __init__.py αρχείων...")
    for directory in init_dirs:
        init_file = Path(directory) / "__init__.py"
        if not init_file.exists():
            init_file.touch()
            print(f"✅ {init_file}")

def create_config_file():
    """Δημιουργία config.py"""
    if Path("config.py").exists():
        print("✅ config.py υπάρχει ήδη")
        return
        
    print("\n⚙️  Δημιουργία config.py...")
    config_content = '''"""
Ρυθμίσεις εφαρμογής AI Document Analyzer
"""
import os
from pathlib import Path

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
    AI_MODEL_NAME = "llama3.1:8b"
    AI_API_URL = "http://localhost:11434"
    MAX_CHUNK_SIZE = 4000
    
    # Document Processing
    SUPPORTED_FORMATS = {'.pdf', '.docx', '.txt', '.png', '.jpg', '.jpeg'}
    MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
    MAX_DEPTH = 5
    
    # Dash App Settings
    DEBUG = True
    HOST = "127.0.0.1"
    PORT = 8050
    
    # UI Settings
    ITEMS_PER_PAGE = 20
    REFRESH_INTERVAL = 1000
    
    # Logging
    LOG_LEVEL = "INFO"
    LOG_FORMAT = "{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}"
    
    @classmethod
    def create_directories(cls):
        """Δημιουργία απαραίτητων φακέλων"""
        for directory in [cls.DATA_DIR, cls.DATABASE_DIR, 
                         cls.LOGS_DIR, cls.TEMP_DIR]:
            directory.mkdir(parents=True, exist_ok=True)

# Development config
class DevelopmentConfig(Config):
    DEBUG = True
    LOG_LEVEL = "DEBUG"

# Production config  
class ProductionConfig(Config):
    DEBUG = False
    LOG_LEVEL = "WARNING"

# Default configuration
config = DevelopmentConfig()
'''
    
    with open("config.py", "w", encoding="utf-8") as f:
        f.write(config_content)
    print("✅ config.py δημιουργήθηκε")

def test_installation():
    """Test της εγκατάστασης"""
    print("\n🧪 Test εγκατάστασης...")
    
    success = True
    
    # Test Python packages
    test_packages = {
        "dash": "Dash web framework",
        "dash_bootstrap_components": "Bootstrap components", 
        "PyPDF2": "PDF processing",
        "docx": "Word document processing",
        "PIL": "Image processing",
        "requests": "HTTP requests",
        "pandas": "Data processing",
        "plotly": "Charts",
        "loguru": "Logging"
    }
    
    for package, description in test_packages.items():
        try:
            __import__(package)
            print(f"✅ {package} - {description}")
        except ImportError:
            print(f"❌ {package} - {description} (δεν εγκαταστάθηκε)")
            success = False
    
    # Test Tesseract (optional)
    if check_tesseract():
        try:
            import pytesseract
            from PIL import Image
            # Δοκιμή με κενή εικόνα
            test_img = Image.new('RGB', (100, 30), color='white')
            pytesseract.image_to_string(test_img)
            print("✅ Tesseract OCR λειτουργεί")
        except Exception as e:
            print(f"⚠️  Tesseract OCR: {e}")
    else:
        print("⚠️  Tesseract OCR δεν είναι διαθέσιμο (προαιρετικό)")
    
    # Test Ollama
    ollama_status = check_ollama()
    if ollama_status == True:
        try:
            import requests
            response = requests.get("http://localhost:11434/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json().get('models', [])
                llama_models = [m for m in models if 'llama' in m.get('name', '').lower()]
                if llama_models:
                    print("✅ Ollama + Llama model διαθέσιμα")
                else:
                    print("⚠️  Ollama τρέχει αλλά δεν βρέθηκε Llama model")
                    success = False
            else:
                print("⚠️  Ollama server δεν απαντά σωστά")
                success = False
        except Exception as e:
            print(f"⚠️  Ollama: {e}")
            success = False
    else:
        print("❌ Ollama δεν είναι διαθέσιμο")
        success = False
    
    return success

def create_run_script():
    """Δημιουργία Windows batch script"""
    script_content = '''@echo off
title AI Document Analyzer
echo ================================================================
echo          AI Document Analyzer - Starting Application
echo ================================================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python δεν βρέθηκε στο PATH
    echo Παρακαλώ εγκαταστήστε Python ή προσθέστε το στο PATH
    pause
    exit /b 1
)

REM Check if main.py exists
if not exist "main.py" (
    echo ❌ main.py δεν βρέθηκε
    echo Βεβαιωθείτε ότι βρίσκεστε στον σωστό φάκελο
    pause
    exit /b 1
)

echo ✅ Εκκίνηση AI Document Analyzer...
echo 🌐 Θα ανοίξει στο http://localhost:8050
echo.
echo Για έξοδο πατήστε Ctrl+C
echo.

REM Start the application
python main.py

echo.
echo Εφαρμογή τερματίστηκε.
pause
'''
    
    with open("run.bat", "w", encoding="utf-8") as f:
        f.write(script_content)
    print("✅ Δημιουργήθηκε run.bat για εύκολη εκκίνηση")

def main():
    """Κύρια συνάρτηση setup"""
    print_banner()
    
    # Βασικοί έλεγχοι
    check_python_version()
    check_pip()
    
    # Δημιουργία δομής project
    create_directories()
    create_init_files()
    create_config_file()
    
    # Εγκατάσταση Python dependencies
    if not install_requirements():
        print("\n❌ Αποτυχία εγκατάστασης Python packages")
        print("Παρακαλώ επιλύστε τα προβλήματα και ξανατρέξτε το setup")
        input("Πατήστε Enter για έξοδο...")
        return
    
    # Ollama setup
    ollama_status = check_ollama()
    if not ollama_status:
        print("\n🤖 Ollama δεν είναι εγκατεστημένο")
        choice = input("Θέλετε να κατεβάσετε το Ollama? (y/n): ").lower()
        if choice == 'y':
            if download_ollama():
                print("\n✅ Ollama κατέβηκε")
                print("Παρακαλώ εγκαταστήστε το και ξανατρέξτε το setup")
                input("Πατήστε Enter για έξοδο...")
                return
        else:
            print("⚠️  Θα χρειαστεί να εγκαταστήσετε το Ollama manually")
            print("   Κατεβάστε από: https://ollama.ai")
    elif ollama_status == "installed_not_running":
        print("\n🚀 Προσπάθεια εκκίνησης Ollama...")
        if not start_ollama():
            print("Δοκιμάστε να εκκινήσετε manual: ollama serve")
    
    # Model setup
    if ollama_status == True:
        choice = input("\nΘέλετε να κατεβάσετε το Llama 3.1 8B model? (y/n): ").lower()
        if choice == 'y':
            setup_ollama_model()
        else:
            print("⚠️  Θα χρειαστεί να κατεβάσετε το model manual:")
            print("   ollama pull llama3.1:8b")
    
    # Tesseract setup (optional)
    if not check_tesseract():
        print("\n⚠️  Tesseract OCR δεν είναι διαθέσιμο")
        choice = input("Θέλετε οδηγίες εγκατάστασης Tesseract? (y/n): ").lower()
        if choice == 'y':
            setup_tesseract()
        print("Η OCR λειτουργικότητα θα είναι απενεργοποιημένη χωρίς Tesseract")
    
    # Final test
    print("\n" + "="*60)
    print("🧪 Τελικός έλεγχος εγκατάστασης...")
    if test_installation():
        print("\n🎉 Setup ολοκληρώθηκε επιτυχώς!")
        
        create_run_script()
        
        print("\n📋 Επόμενα βήματα:")
        print("1. Βεβαιωθείτε ότι το Ollama τρέχει")
        print("2. Εκτελέστε: python main.py")
        print("3. Ή double-click το run.bat")
        print("4. Ανοίξτε browser στο: http://localhost:8050")
        
        # Final checks
        print("\n🔍 Τελικοί έλεγχοι:")
        if check_ollama() == True:
            print("✅ Ollama είναι έτοιμο")
        else:
            print("⚠️  Μην ξεχάσετε να εκκινήσετε το Ollama: ollama serve")
        
        print("\n🎯 Η εφαρμογή είναι έτοιμη για χρήση!")
        
    else:
        print("\n❌ Setup απέτυχε")
        print("Ελέγξτε τα μηνύματα σφάλματος παραπάνω")
        print("Για βοήθεια δημιουργήστε issue στο GitHub")
    
    input("\nΠατήστε Enter για έξοδο...")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Setup διακόπηκε από χρήστη")
    except Exception as e:
        print(f"\n\n❌ Απροσδόκητο σφάλμα: {e}")
        print("Παρακαλώ αναφέρετε αυτό το σφάλμα")
    finally:
        input("Πατήστε Enter για έξοδο...")
