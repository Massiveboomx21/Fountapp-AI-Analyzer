# AI Document Analyzer

Εφαρμογή για αυτόματη ανάλυση εγγράφων με τεχνητή νοημοσύνη. Σαρώνει φακέλους, εξάγει κείμενο από έγγραφα και αναλύει το περιεχόμενό τους χρησιμοποιώντας τοπικό AI model.

## 🚀 Χαρακτηριστικά

- **Σάρωση φακέλων**: Αυτόματη εύρεση και επεξεργασία εγγράφων
- **Πολλαπλοί τύποι αρχείων**: PDF, DOCX, TXT, εικόνες (OCR)
- **AI Ανάλυση**: Περίληψη, λέξεις-κλειδιά, κατηγοριοποίηση, sentiment analysis
- **Τοπικό AI**: Χρήση Llama 3.1 χωρίς cloud dependencies
- **Web Interface**: Σύγχρονη διεπαφή με Dash
- **Database**: Αποθήκευση και αναζήτηση αποτελεσμάτων

## 📋 Απαιτήσεις

### Λογισμικό
- **Python 3.8+**
- **Ollama** (για AI model)
- **Tesseract OCR** (προαιρετικό, για εικόνες)

### Hardware
- **RAM**: 8GB+ (για Llama 3.1 8B)
- **Storage**: 5GB+ ελεύθερος χώρος
- **CPU**: 4+ cores προτεινόμενα

## 🛠️ Εγκατάσταση

### 1. Clone το Repository
```bash
git clone 
cd AI_Document_Analyzer
```

### 2. Εκτέλεση Setup Script
```bash
python setup.py
```

### 3. Εγκατάσταση Ollama
1. Κατεβάστε από: https://ollama.ai
2. Εγκαταστήστε και εκκινήστε
3. Κατεβάστε το model:
```bash
ollama pull llama3.1:8b
```

### 4. Εγκατάσταση Tesseract (Προαιρετικό)
**Windows:**
1. Κατεβάστε από: https://github.com/UB-Mannheim/tesseract/wiki
2. Εγκαταστήστε και προσθέστε στο PATH
3. Κατεβάστε ελληνικά language packs

## 🎯 Χρήση

### Εκκίνηση Εφαρμογής
```bash
python main.py
```

Η εφαρμογή θα είναι διαθέσιμη στο: http://localhost:8050

### Βασική Χρήση
1. **Επιλογή φακέλου**: Κλικ στο "Browse" και επιλέξτε φάκελο
2. **Ρυθμίσεις**: Επιλέξτε τύπους αρχείων και επιλογές επεξεργασίας
3. **Έναρξη**: Κλικ "Έναρξη Ανάλυσης"
4. **Αποτελέσματα**: Παρακολούθηση προόδου και προβολή αποτελεσμάτων

### Επιλογές Επεξεργασίας
- **Recursive σάρωση**: Επεξεργασία υποφακέλων
- **Εικόνες (OCR)**: Εξαγωγή κειμένου από εικόνες
- **Λεπτομερής ανάλυση**: Πιο αναλυτική AI επεξεργασία

## 📁 Δομή Project

```
AI_Document_Analyzer/
├── main.py                 # Εκκίνηση εφαρμογής
├── config.py              # Ρυθμίσεις
├── requirements.txt       # Dependencies
├── setup.py              # Setup script
├── README.md             # Αυτό το αρχείο
│
├── app/                  # Dash εφαρμογή
│   ├── dash_app.py      # Setup
│   └── callbacks.py     # Callbacks
│
├── core/                # Κύρια λογική
│   ├── file_scanner.py  # Σάρωση αρχείων
│   ├── document_processor.py # Επεξεργασία εγγράφων
│   ├── ai_analyzer.py   # AI ανάλυση
│   └── database.py      # Database operations
│
├── models/              # AI Models
│   └── llama_client.py  # Llama client
│
├── ui/                  # UI Components
│   └── layouts.py       # Layouts
│
├── utils/               # Utilities
│   └── logger.py        # Logging
│
└── data/               # Data storage
    ├── database/       # SQLite DB
    ├── logs/          # Log files
    └── temp/          # Temporary files
```

## ⚙️ Ρυθμίσεις

Επεξεργαστείτε το `config.py` για προσαρμογή:

```python
# AI Model
AI_MODEL_NAME = "llama3.1:8b"  # Όνομα model
AI_API_URL = "http://localhost:11434"  # Ollama URL

# Document Processing  
MAX_CHUNK_SIZE = 4000  # Μέγεθος chunks
SUPPORTED_FORMATS = {'.pdf', '.docx', '.txt', '.png', '.jpg', '.jpeg'}

# App Settings
HOST = "127.0.0.1"
PORT = 8050
DEBUG = True
```

## 🔧 Troubleshooting

### Συχνά Προβλήματα

**1. Ollama δεν συνδέεται**
```bash
# Έλεγχος αν τρέχει
curl http://localhost:11434/api/tags

# Επανεκκίνηση
ollama serve
```

**2. Tesseract σφάλματα**
```bash
# Windows: Προσθήκη στο PATH
set PATH=%PATH%;C:\Program Files\Tesseract-OCR
```

**3. Memory errors**
- Χρησιμοποιήστε μικρότερο model (llama3.1:7b)
- Μειώστε MAX_CHUNK_SIZE στο config.py

**4. Permission errors**
- Εκτελέστε ως Administrator (Windows)
- Ελέγξτε δικαιώματα φακέλων

### Logs
Τα logs αποθηκεύονται στο `data/logs/`:
- `app_YYYY-MM-DD.log`: Γενικά logs
- `errors_YYYY-MM-DD.log`: Μόνο σφάλματα

## 📊 Performance Tips

### Για καλύτερη απόδοση:
1. **SSD Storage**: Για γρήγορη πρόσβαση στα αρχεία
2. **RAM**: 16GB+ για μεγάλα έγγραφα
3. **GPU**: NVIDIA GPU για γρηγορότερο AI (μελλοντική υποστήριξη)

### Batch Processing:
- Επεξεργασία 50-100 αρχείων κάθε φορά
- Χρήση "Λεπτομερής ανάλυση" μόνο όταν χρειάζεται

## 🤝 Contributing

1. Fork το project
2. Δημιουργήστε feature branch
3. Commit τις αλλαγές σας
4. Push στο branch
5. Δημιουργήστε Pull Request

## 📄 License

MIT License - Δείτε το LICENSE αρχείο για λεπτομέρειες.

## 🆘 Υποστήριξη

Για προβλήματα ή ερωτήσεις:
1. Ελέγξτε τα logs στο `data/logs/`
2. Δημιουργήστε GitHub issue
3. Συμπεριλάβετε λεπτομέρειες συστήματος και σφάλματος

## 🔮 Μελλοντικές Βελτιώσεις

- [ ] GPU υποστήριξη για γρηγορότερο AI
- [ ] Περισσότερα AI models (Mistral, Qwen)
- [ ] Export αποτελεσμάτων (PDF, Excel)
- [ ] REST API
- [ ] Docker containerization
- [ ] Πολυγλωσσική υποστήριξη

---

**Made with ❤️ for document analysis automation**
