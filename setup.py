"""
Setup script για AI Document Analyzer
"""
import os
import subprocess
import sys
from pathlib import Path

def check_python_version():
    """Έλεγχος Python version"""
    if sys.version_info < (3, 8):
        print("❌ Απαιτείται Python 3.8 ή νεότερη έκδοση")
        sys.exit(1)
    else:
        print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")

def install_requirements():
    """Εγκατάσταση dependencies"""
    print("\n📦 Εγκατάσταση dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies εγκαταστάθηκαν επιτυχώς")
    except subprocess.CalledProcessError:
        print("❌ Σφάλμα εγκατάστασης dependencies")
        sys.exit(1)

def setup_tessract():
    """Οδηγίες για Tesseract OCR"""
    print("\n🔍 Tesseract OCR Setup:")
    print("Για OCR λειτουργικότητα, χρειάζεται να εγκαταστήσετε το Tesseract:")
    print("1. Κατεβάστε από: https://github.com/UB-Mannheim/tesseract/wiki")
    print("2. Εγκαταστήστε και προσθέστε στο PATH")
    print("3. Κατεβάστε ελληνικά language packs")

def setup_ollama():
    """Οδηγίες για Ollama"""
    print("\n🤖 Ollama AI Model Setup:")
    print("1. Κατεβάστε Ollama από: https://ollama.ai")
    print("2. Εγκαταστήστε και εκκινήστε το")
    print("3. Εκτελέστε: ollama pull llama3.1:8b")
    print("4. Βεβαιωθείτε ότι τρέχει στο http://localhost:11434")

def create_directories():
    """Δημιουργία απαραίτητων φακέλων"""
    directories = [
        "data/database",
        "data/logs", 
        "data/
