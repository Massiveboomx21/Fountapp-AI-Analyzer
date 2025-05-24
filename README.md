# AI Document Analyzer

Application for automatic document analysis using artificial intelligence. Scans folders, extracts text from documents and analyzes their content using local AI models.

## 🚀 Features

- **Folder Scanning**: Automatic discovery and processing of documents
- **Multiple File Types**: PDF, DOCX, TXT, images (OCR)
- **AI Analysis**: Summary, keywords, categorization, sentiment analysis
- **Local AI**: Uses Llama 3.1 without cloud dependencies
- **Web Interface**: Modern interface with Dash
- **Database**: Storage and search of results

## 📋 Requirements

### Software
- **Python 3.8+**
- **Ollama** (for AI model)
- **Tesseract OCR** (optional, for images)

### Hardware
- **RAM**: 8GB+ (for Llama 3.1 8B)
- **Storage**: 5GB+ free space
- **CPU**: 4+ cores recommended

## 🛠️ Installation

### 1. Clone the Repository
```bash
git clone 
cd Fountapp-AI-Analyzer
```

### 2. Run Setup Script
```bash
python setup.py
```

### 3. Install Ollama
1. Download from: https://ollama.ai
2. Install and start
3. Download the model:
```bash
ollama pull llama3.1:8b
```

### 4. Install Tesseract (Optional)
**Windows:**
1. Download from: https://github.com/UB-Mannheim/tesseract/wiki
2. Install and add to PATH
3. Download language packs

## 🎯 Usage

### Starting the Application
```bash
python main.py
```

The application will be available at: http://localhost:8050

### Basic Usage
1. **Select folder**: Click "Browse" and select folder
2. **Settings**: Choose file types and processing options
3. **Start**: Click "Start Analysis"
4. **Results**: Monitor progress and view results

### Processing Options
- **Recursive scanning**: Process subfolders
- **Images (OCR)**: Extract text from images
- **Detailed analysis**: More thorough AI processing

## 📁 Project Structure

```
AI_Document_Analyzer/
├── main.py                 # Application startup
├── config.py              # Settings
├── requirements.txt       # Dependencies
├── setup.py              # Setup script
├── README.md             # This file
│
├── app/                  # Dash application
│   ├── dash_app.py      # Setup
│   └── callbacks.py     # Callbacks
│
├── core/                # Core logic
│   ├── file_scanner.py  # File scanning
│   ├── document_processor.py # Document processing
│   ├── ai_analyzer.py   # AI analysis
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

## ⚙️ Configuration

Edit `config.py` for customization:

```python
# AI Model
AI_MODEL_NAME = "llama3.1:8b"  # Model name
AI_API_URL = "http://localhost:11434"  # Ollama URL

# Document Processing  
MAX_CHUNK_SIZE = 4000  # Chunk size
SUPPORTED_FORMATS = {'.pdf', '.docx', '.txt', '.png', '.jpg', '.jpeg'}

# App Settings
HOST = "127.0.0.1"
PORT = 8050
DEBUG = True
```

## 🔧 Troubleshooting

### Common Issues

**1. Ollama not connecting**
```bash
# Check if running
curl http://localhost:11434/api/tags

# Restart
ollama serve
```

**2. Tesseract errors**
```bash
# Windows: Add to PATH
set PATH=%PATH%;C:\Program Files\Tesseract-OCR
```

**3. Memory errors**
- Use smaller model (llama3.1:7b)
- Reduce MAX_CHUNK_SIZE in config.py

**4. Permission errors**
- Run as Administrator (Windows)
- Check folder permissions

### Logs
Logs are stored in `data/logs/`:
- `app_YYYY-MM-DD.log`: General logs
- `errors_YYYY-MM-DD.log`: Error logs only

## 📊 Performance Tips

### For better performance:
1. **SSD Storage**: For fast file access
2. **RAM**: 16GB+ for large documents
3. **GPU**: NVIDIA GPU for faster AI (future support)

### Batch Processing:
- Process 50-100 files at a time
- Use "Detailed analysis" only when needed

## 🤝 Contributing

1. Fork the project
2. Create feature branch
3. Commit your changes
4. Push to branch
5. Create Pull Request

## 📄 License

MIT License - See LICENSE file for details.

## 🆘 Support

For issues or questions:
1. Check logs in `data/logs/`
2. Create GitHub issue
3. Include system details and error information

## 🔮 Future Improvements

- [ ] GPU support for faster AI
- [ ] More AI models (Mistral, Qwen)
- [ ] Export results (PDF, Excel)
- [ ] REST API
- [ ] Docker containerization
- [ ] Multi-language support

---

**Made with ❤️ for document analysis automation**
