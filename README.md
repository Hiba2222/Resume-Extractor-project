# CV Extractor - New Project Structure

## 🎯 **Overview**
Professional AI-powered CV/Resume data extraction tool with a clean, organized structure.

## 📁 **New Project Structure**

```
cv-extractor/
├── 📄 main.py                    # Single entry point
├── 📄 requirements.txt
├── 📄 .env.example
├── 📄 .gitignore
├── 📄 README.md
│
├── 📁 app/                       # Main application
│   ├── 📄 __init__.py
│   ├── 📄 config.py             # Configuration
│   ├── 📄 pipeline.py           # Core processing
│   ├── 📄 models.py             # AI models
│   ├── 📄 extractor.py          # PDF extraction
│   └── 📄 utils.py              # Utilities
│
├── 📁 web/                       # Web interface
│   ├── 📄 __init__.py
│   ├── 📄 app.py                # Flask app
│   ├── 📁 static/
│   │   ├── 📄 style.css
│   │   ├── 📄 scripts.js
│   │   └── 📄 interface1.png
│   └── 📁 templates/
│       ├── 📄 base.html
│       ├── 📄 home.html
│       ├── 📄 index.html
│       ├── 📄 result.html
│       ├── 📄 about.html
│       ├── 📄 error.html
│       └── 📄 macros.html
│
├── 📁 evaluation/                # Model evaluation
│   ├── 📄 __init__.py
│   ├── 📄 evaluator.py          # Evaluation logic
│   ├── 📄 metrics.py            # Evaluation metrics
│   ├── 📄 core.py               # Core evaluation
│   └── 📄 runner.py             # Evaluation runner
│
├── 📁 tests/                     # Test suite
│   ├── 📄 __init__.py
│   ├── 📄 test_pipeline.py      # Core tests
│   ├── 📄 test_models.py        # Model tests
│   ├── 📄 test_web.py           # Web tests
│   └── 📁 fixtures/             # Test data
│
├── 📁 data/                      # Data storage
│   ├── 📁 uploads/              # Temp uploads
│   ├── 📁 outputs/              # Results
│   ├── 📁 results/              # Processing results
│   ├── 📁 input/                # Input files
│   └── 📁 ground_truth/         # Evaluation data
│
└── 📁 scripts/                   # Utility scripts
    ├── 📄 run_web.py            # Start web app
    ├── 📄 run_evaluation.py     # Run evaluation
    └── 📄 run_tests.py          # Run tests
```

## 🚀 **Quick Start**

### **1. Web Application**
```bash
# Method 1: Using main entry point
python main.py web

# Method 2: Using script
python scripts/run_web.py

# Method 3: Direct
python web/app.py
```

### **2. CLI Processing**
```bash
# Process single file
python main.py cli -i resume.pdf

# Process with specific model
python main.py cli -i resume.pdf -m mistral

# Save to file
python main.py cli -i resume.pdf -o results.json
```

### **3. Run Evaluation**
```bash
# Using main entry point
python main.py eval

# Using script
python scripts/run_evaluation.py --cv-dir data/samples
```

### **4. Run Tests**
```bash
# Using main entry point
python main.py test

# Using script
python scripts/run_tests.py
```

## 🔧 **Configuration**

All configuration is centralized in `app/config.py`:

```python
from app.config import Config

# Access configuration
print(Config.HOST)
print(Config.PORT)
print(Config.DEFAULT_MODEL)
```

## 📦 **Key Improvements**

### **✅ Benefits of New Structure:**
- **Clean separation** of concerns
- **Easy to navigate** and understand
- **Modular design** - each component is independent
- **Professional structure** following Python best practices
- **Comprehensive testing** framework
- **Evaluation system** for model performance
- **Single entry point** for all operations
- **Centralized configuration**

### **🔄 Migration Changes:**
- `cv_extractor/` → `app/` (core application)
- `cv_extractor/web/` → `web/` (web interface)
- `cv_extractor/evaluation/` → `evaluation/` (evaluation system)
- `bin/` → `scripts/` (utility scripts)
- All imports updated to new structure
- Single `main.py` entry point

## 🧪 **Testing**

```bash
# Run all tests
python main.py test

# Run specific test module
python scripts/run_tests.py --module test_pipeline

# Run with coverage
python scripts/run_tests.py --coverage
```

## 📊 **Evaluation**

```bash
# Evaluate single CV
python scripts/run_evaluation.py --single-cv resume.pdf

# Evaluate dataset
python scripts/run_evaluation.py --cv-dir data/samples --models llama3 mistral phi

# Custom output
python scripts/run_evaluation.py --cv-dir data/samples --output my_report.json
```

## 🔍 **Development**

### **Adding New Models:**
1. Add model config to `app/config.py`
2. Update `app/models.py` with new model logic
3. Add tests in `tests/test_models.py`

### **Adding New Features:**
1. Core logic → `app/`
2. Web interface → `web/`
3. Tests → `tests/`
4. Documentation → Update README

## 🎉 **Ready to Use!**

The project is now organized with a professional, clean structure that's easy to:
- **Navigate** and understand
- **Extend** with new features
- **Test** comprehensively
- **Deploy** to production
- **Maintain** long-term

Start with: `python main.py web` and visit http://localhost:5000
