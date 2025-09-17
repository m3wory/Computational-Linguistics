# Frequency Dictionary

A powerful multilingual frequency dictionary application that analyzes text files and creates searchable word frequency databases. Built with Python and Flask, supporting Russian, English, and German languages.

## 🌟 Features

### Core Functionality
- **Multilingual Support**: Russian, English, and German text processing
- **Text Analysis**: Processes multiple text files to create comprehensive frequency dictionaries  
- **Smart Word Cleaning**: Language-specific text preprocessing and normalization
- **Unicode Support**: Handles various text encodings (UTF-8, CP1251, Latin-1, CP1252)

### Interactive Interfaces
- **Console Interface**: Full-featured command-line interface with menus
- **Web Interface**: Modern Bootstrap-based web UI with real-time updates
- **REST API**: JSON endpoints for programmatic access

### Dictionary Management
- **Search**: Find words by prefix patterns
- **Sorting**: Sort by frequency or alphabetically (ascending/descending)
- **Word Operations**: Add, delete, and correct words with automatic statistics updates
- **File Processing**: Add new text files to expand existing dictionaries
- **Statistics**: Comprehensive word count and uniqueness metrics

## 🚀 Quick Start

### Prerequisites
- Python 3.7+
- pip package manager

### Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd FrequencyDictionary
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Prepare your text files**
```
data/
├── english/
│   ├── movies.txt
│   └── wikis.txt
├── german/
│   ├── Der_Mann_ohne_Eigenschaften.txt
│   └── Die_Ahnen.txt
└── russian/
    ├── anna_karenina.txt
    ├── war_and_peace.txt
    └── master_and_margarita.txt
```

4. **Create dictionaries**
```bash
# Create all language dictionaries
python app.py create --language all

# Or create specific language
python app.py create --language russian
```

5. **Launch interface**
```bash
# Console interface
python app.py interface

# Web interface
python app.py web
```

## 📋 Usage

### Command Line Interface

#### Creating Dictionaries
```bash
# Create all dictionaries
python app.py create --language all

# Create specific language dictionary
python app.py create --language russian

# Force recreate existing dictionary
python app.py create --language english --force
```

#### Interactive Console
```bash
# Launch main menu
python app.py interface

# Launch specific language directly
python app.py interface --language russian
```

#### Web Interface
```bash
# Launch on default host (127.0.0.1:5000)
python app.py web

# Custom host and port
python app.py web --host 0.0.0.0 --port 8080

# Debug mode
python app.py web --debug
```

### Web Interface Features

Access the web interface at `http://localhost:5000` and enjoy:

- **Language Selection**: Choose from available dictionaries
- **Real-time Statistics**: Live word count and uniqueness metrics
- **Interactive Search**: Type-ahead word search with instant results
- **Multiple Sorting Options**: 
  - Alphabetical (A→Z, Z→A)
  - Frequency (High→Low, Low→High)
- **Word Management**:
  - Add new words
  - Delete existing words
  - Correct/merge word entries
- **File Upload**: Drag & drop .txt files to expand dictionaries
- **Responsive Design**: Works on desktop and mobile devices

### Console Interface Menu

```
=== FREQUENCY DICTIONARY ===
1. Statistics
2. Alphabetical A→Z
3. Alphabetical Z→A  
4. Frequency ↓
5. Frequency ↑
6. Search words
7. Correct word
8. Delete word
9. Add word
10. Add new text file
0. Back
```

## 🏗️ Project Structure

```
FrequencyDictionary/
├── data/                          # Text files for processing
│   ├── english/
│   ├── german/
│   └── russian/
├── dictionaries/                  # Generated JSON dictionaries
│   ├── english_dictionary.json
│   ├── german_dictionary.json
│   └── russian_dictionary.json
├── templates/                     # Flask templates
│   └── index.html
├── app.py                         # Main CLI application
├── frequency_dictionary.py       # Core dictionary logic
├── web_app.py                    # Flask web application
├── config.py                     # Configuration and constants
├── requirements.txt              # Python dependencies
└── README.md                     # This file
```

## 🔧 Configuration

### Supported Languages
- **Russian**: Full Cyrillic support with proper locale sorting
- **English**: ASCII + common punctuation handling  
- **German**: Includes umlauts (äöüÄÖÜß) and special characters

### File Processing Settings
```python
# Maximum display limits
MAX_DISPLAY_WORDS = 50
MAX_SEARCH_RESULTS = 20

# Supported file extensions  
ALLOWED_EXTENSIONS = ['.txt']

# Encoding priority for reading files
ENCODINGS = ['utf-8', 'cp1251', 'latin-1', 'cp1252']
```

### Text Cleaning Patterns
Each language has specific regex patterns for cleaning:
- **English**: `[^a-zA-Z\-\']`
- **German**: `[^a-zA-ZäöüÄÖÜß\-\']`  
- **Russian**: `[^а-яёА-ЯЁ\-]`

## 🌐 API Endpoints

The web interface provides REST API endpoints:

### Statistics
```
GET /stats
```
Returns current dictionary statistics.

### Word Lists  
```
GET /words?sort=alphabet&reverse=false&limit=50&search=term
```
Parameters:
- `sort`: `alphabet` or `frequency`
- `reverse`: `true` or `false`
- `limit`: number of results
- `search`: prefix search term

### Word Operations
```
POST /word_action
```
Form data:
- `action`: `add`, `delete`, or `correct`
- `word`: target word
- `wrong_word`, `correct_word`: for corrections

### File Upload
```
POST /upload_text
```
Multipart form with `file` field containing .txt file.

## 💻 Examples

### Processing Custom Text Files

1. Add your text files to the appropriate language directory:
```bash
cp my_book.txt data/english/
```

2. Recreate the dictionary:
```bash
python app.py create --language english --force
```

### Programmatic Access

```python
from frequency_dictionary import FrequencyDictionary

# Initialize
fd = FrequencyDictionary()

# Create dictionary from files
fd.create_dictionary('english')

# Load and use
fd.load_dictionary('english')
fd.stats()
fd.search('hello')
fd.add_word('newword')
```

### Web Interface Workflow

1. **Select Language**: Choose from available dictionaries
2. **View Statistics**: See total and unique word counts  
3. **Browse Words**: Use sorting options to explore vocabulary
4. **Search**: Find words starting with specific letters
5. **Edit**: Add, correct, or remove words as needed
6. **Expand**: Upload new text files to grow the dictionary

## 🛠️ Dependencies

### Core Requirements
- **numpy** (1.24.3): Numerical operations and data processing
- **tqdm** (4.65.0): Progress bars for file processing
- **Flask** (2.3.3): Web interface framework

### Built-in Libraries Used
- `json`: Dictionary serialization
- `re`: Text pattern matching and cleaning
- `locale`: Language-specific sorting
- `pathlib`: Modern file path handling
- `collections.defaultdict`: Efficient word counting
- `argparse`: Command-line argument parsing

## 🚦 Performance Notes

### File Processing
- Uses progress bars (tqdm) for long operations
- Processes files in chunks to manage memory
- Efficient defaultdict for word counting
- Multiple encoding attempts for robust file reading

### Memory Usage
- Dictionaries stored as JSON files on disk
- Only current language loaded in memory
- Efficient word cleaning with compiled regex patterns

### Web Interface
- Responsive Bootstrap UI
- AJAX requests for smooth user experience
- Real-time statistics updates
- Pagination for large word lists

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes and test thoroughly
4. Commit with clear messages: `git commit -m "Add feature description"`
5. Push to your fork: `git push origin feature-name`
6. Open a pull request with detailed description

### Adding New Languages

To add support for a new language:

1. **Update `config.py`**:
```python
LANGUAGES = {
    # existing languages...
    'french': 'Français'
}

LOCALES = {
    # existing locales...
    'french': 'fr_FR.UTF-8'
}

CLEAN_PATTERNS = {
    # existing patterns...
    'french': r'[^a-zA-ZàâäéèêëïîôöùûüÀÂÄÉÈÊËÏÎÔÖÙÛÜ\-\']'
}
```

2. **Create data directory**:
```bash
mkdir data/french
# Add .txt files to this directory
```

3. **Test the implementation**:
```bash
python app.py create --language french
python app.py interface --language french
```

## 📄 License

This project is available under the MIT License. See LICENSE file for details.

## 🐛 Troubleshooting

### Common Issues

**Dictionary not found**
- Ensure text files exist in `data/{language}/` directory
- Run `python app.py create --language {language}` first

**File encoding errors**
- Check that text files are in supported encodings (UTF-8 recommended)
- The application tries multiple encodings automatically

**Web interface not loading**
- Verify Flask is installed: `pip install flask`
- Check if port 5000 is available or use `--port` option
- Ensure dictionaries are created before using web interface

**Locale errors**
- System locale might not support the language
- Application falls back to standard sorting if locale unavailable

**Memory issues with large files**
- Consider splitting very large text files
- Monitor system memory during dictionary creation
- Use `--force` flag cautiously with large datasets

### Getting Help

1. Check this README for configuration options
2. Review error messages for specific guidance
3. Ensure all dependencies are properly installed
4. Verify file permissions for data and dictionaries directories