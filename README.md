# CV Extractor 

## 🎯 **Overview**
Professional AI-powered CV/Resume data extraction tool with modern web interface, modular architecture, and comprehensive testing suite. Built with Flask, featuring multiple AI models (Llama 3, Mistral, Phi) and beautiful, responsive UI.

## ✨ **Key Features**
- 🤖 **Multiple AI Models** - Llama 3, Mistral, and Microsoft Phi
- 🎨 **Modern Web Interface** - Responsive design with semantic HTML/CSS
- 📱 **Mobile Optimized** - Works perfectly on all devices
- 🔄 **Real-time Processing** - Live extraction with progress indicators
- 📊 **Comprehensive Results** - Structured data extraction with JSON export
- 🧪 **Full Test Coverage** - Comprehensive testing framework
- 🏗️ **Modular Architecture** - Clean, maintainable codebase

## 📁 **Project Structure**

```
Resume_extractor_project/
├── 📄 Dockerfile                # Docker configuration
├── 📄 README.md                 # This file
│
├── 📁 app/                      # Core application logic
│   ├── 📄 __init__.py
│   ├── 📄 config.py            # Configuration management
│   ├── 📄 pipeline.py          # Processing pipeline
│   ├── 📄 models.py            # AI model implementations
│   ├── 📄 extractor.py         # PDF extraction logic
│   └── 📄 utils.py             # Utility functions
│
├── 📁 web/                      # Modern web interface
│   ├── 📄 app.py               # Flask application
│   ├── 📁 static/              # Static assets (modular)
│   │   ├── 📁 css/            # Modular CSS architecture
│   │   │   ├── 📄 main.css    # Main CSS (imports all)
│   │   │   ├── 📄 base.css    # Variables & typography
│   │   │   ├── 📄 layout.css  # Navigation & layout
│   │   │   ├── 📄 components.css # Reusable components
│   │   │   ├── 📄 pages.css   # Page-specific styles
│   │   │   ├── 📄 upload.css  # Upload functionality
│   │   │   └── 📄 animations.css # Animations & effects
│   │   └── 📁 js/             # Modular JavaScript
│   │       ├── 📄 main.js     # Main initialization
│   │       ├── 📄 common.js   # Shared utilities
│   │       ├── 📄 upload.js   # Upload functionality
│   │       └── 📄 results.js  # Results page logic
│   └── 📁 templates/           # Jinja2 templates (organized)
│       ├── 📁 base/           # Reusable components
│       │   ├── 📄 head.html   # HTML head
│       │   ├── 📄 navigation.html # Navigation bar
│       │   ├── 📄 footer.html # Footer
│       │   ├── 📄 flash_messages.html # Flash messages
│       │   └── 📄 scripts.html # Script includes
│       ├── 📁 home/           # Home page
│       │   └── 📄 index.html
│       ├── 📁 about/          # About page
│       │   └── 📄 index.html
│       ├── 📁 upload/         # Upload page
│       │   └── 📄 index.html
│       ├── 📁 results/        # Results page
│       │   └── 📄 index.html
│       ├── 📄 base.html       # Base template
│       ├── 📄 error.html      # Error pages
│       └── 📄 macros.html     # Jinja2 macros
│
├── 📁 evaluation/              # Model evaluation system
│   ├── 📄 __init__.py
│   ├── 📄 evaluator.py        # Evaluation logic
│   ├── 📄 metrics.py          # Performance metrics
│   ├── 📄 core.py             # Core evaluation
│   └── 📄 runner.py           # Evaluation runner
│
├── 📁 tests/                   # Comprehensive test suite
│   ├── 📄 __init__.py
│   ├── 📄 test_pipeline.py    # Core logic tests
│   ├── 📄 test_models.py      # AI model tests
│   └── 📄 test_web.py         # Web interface tests
│
├── 📁 data/                    # Data storage
│   ├── 📁 cache/             # Processing cache
│   ├── 📁 ground_truth/      # Evaluation datasets
│   ├── 📁 input/             # Sample CV files
│   ├── 📁 outputs/           # Processing outputs
│   ├── 📁 results/           # Session results
│   └── 📁 uploads/           # Temporary uploads
│
└── 📁 scripts/                 # Utility scripts
    ├── 📄 run_web.py          # Start web server
    ├── 📄 run_evaluation.py   # Run evaluations
    └── 📄 run_tests.py        # Run test suite
```

## 🚀 **Quick Start**

### **1. Installation**
```bash
# Clone the repository
git clone <repository-url>
cd Resume_extractor_project

# Install dependencies
pip install -r requirements.txt

# Set up environment variables (optional)
cp .env.example .env
```

### **2. Start Web Application**
```bash
# Start the Flask web server
python web/app.py

# Or using scripts
python scripts/run_web.py
```

Visit `http://localhost:5000` to access the web interface.

### **3. Using the Web Interface**

1. **Home Page** - Overview of features and capabilities
2. **Upload CV** - Drag & drop or browse to upload PDF files
3. **Select AI Model** - Choose from Llama 3, Mistral, or Phi
4. **View Results** - See extracted data with original PDF side-by-side
5. **Export Data** - Download results as JSON

### **4. Run Tests**
```bash
# Run all tests
python scripts/run_tests.py

# Run specific test module
python -m pytest tests/test_web.py -v
```

### **5. Run Evaluation**
```bash
# Evaluate model performance
python scripts/run_evaluation.py --cv-dir data/input
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

## 🎨 **UI/UX Features**

### **Modern Design System**
- **Consistent Colors** - Professional blue gradient theme
- **Responsive Layout** - Mobile-first design approach
- **Semantic HTML** - Accessible and SEO-friendly structure
- **Modular CSS** - 7 organized CSS files for maintainability
- **Smooth Animations** - Floating dots, hover effects, and transitions
- **Interactive Elements** - Drag & drop, model selection, progress indicators

### **User Experience**
- **Intuitive Navigation** - Clear page structure and flow
- **Real-time Feedback** - Loading states and progress indicators
- **Error Handling** - Graceful error messages and recovery
- **Mobile Optimized** - Touch-friendly interface for all devices
- **Accessibility** - ARIA labels and semantic markup

## 🏗️ **Architecture Highlights**

### **Frontend Architecture**
- **Component-Based** - Reusable template components
- **Modular CSS** - Organized by functionality (base, layout, components, pages)
- **Progressive Enhancement** - Works without JavaScript
- **Cache Optimization** - Versioned assets and proper headers

### **Backend Architecture**
- **MVC Pattern** - Clear separation of concerns
- **Modular Design** - Independent, testable components
- **Configuration Management** - Centralized settings
- **Error Handling** - Comprehensive error management
- **Session Management** - Secure file handling and cleanup

## 🧪 **Testing & Quality**

### **Test Coverage**
- **Unit Tests** - Core logic and model testing
- **Integration Tests** - End-to-end workflow testing
- **Web Tests** - Flask application testing
- **Fixtures** - Reusable test data and mocks

### **Code Quality**
- **Clean Code** - Following Python best practices
- **Documentation** - Comprehensive inline documentation
- **Type Hints** - Enhanced code reliability
- **Error Handling** - Robust error management

## 🚀 **Deployment**

### **Docker Support**
```bash
# Build Docker image
docker build -t cv-extractor .

# Run container
docker run -p 5000:5000 cv-extractor
```

### **Production Considerations**
- **Environment Variables** - Secure configuration management
- **Static File Serving** - Optimized for production
- **Error Logging** - Comprehensive logging system
- **Security** - CSRF protection and secure file handling

## 🔧 **Development**

### **Adding New Features**
1. **Backend Logic** → Add to `app/` modules
2. **Frontend** → Update templates and static files
3. **Styling** → Add to appropriate CSS module
4. **Testing** → Add tests to `tests/` directory
5. **Documentation** → Update README and inline docs

### **CSS Architecture**
- `base.css` - Variables, typography, base styles
- `layout.css` - Navigation, footer, main layout
- `components.css` - Reusable UI components
- `pages.css` - Page-specific styles
- `upload.css` - Upload functionality styles
- `animations.css` - Animations and transitions
- `main.css` - Imports all modules

### **JavaScript Modules**
- `main.js` - Application initialization
- `common.js` - Shared utilities and functions
- `upload.js` - File upload and drag-drop functionality
- `results.js` - Results page interactions

## 🎯 **Project Status**

✅ **Completed Features:**
- Modern, responsive web interface
- Multiple AI model support (Llama 3, Mistral, Phi)
- Comprehensive CSS/JS refactoring
- Component-based template architecture
- Mobile-optimized design
- Real-time file processing
- JSON export functionality
- Comprehensive test suite
- Clean project structure

🚀 **Ready for Production!**

The CV Extractor is now a professional-grade application with:
- **Clean Architecture** - Maintainable and scalable codebase
- **Modern UI/UX** - Beautiful, responsive interface
- **Robust Testing** - Comprehensive test coverage
- **Production Ready** - Docker support and deployment considerations

Start exploring: `python web/app.py` → http://localhost:5000
