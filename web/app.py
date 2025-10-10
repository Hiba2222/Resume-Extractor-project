"""
CV Extractor Web Application
----------------------------
Flask web interface for CV extraction and processing.
"""

from flask import Flask, render_template, request, redirect, url_for, send_file, jsonify, flash, session
import os
import uuid
import json
import sys
import time
from werkzeug.utils import secure_filename
from pathlib import Path
import threading

from app.config import Config, ensure_directories
from app.extractor import ExtractFromPDF
from app.models import CVInfoExtractor
from app.utils import validate_file, get_unique_filename, create_safe_filename


def create_app(testing=False):
    """Application factory function."""
    # Ensure directories exist
    ensure_directories()
    
    app = Flask(__name__, 
               template_folder='templates',
               static_folder='static')
    
    if testing:
        app.config.update({
            'TESTING': True,
            'SECRET_KEY': 'test-secret-key',
            'UPLOAD_FOLDER': str(Config.BASE_DIR / "tests" / "temp_uploads"),
            'RESULTS_FOLDER': str(Config.BASE_DIR / "tests" / "temp_results"),
        })
    else:
        app.config.update({
            'SECRET_KEY': Config.SECRET_KEY,
            'UPLOAD_FOLDER': str(Config.UPLOAD_FOLDER),
            'RESULTS_FOLDER': str(Config.RESULTS_FOLDER),
        })
    
    app.config['MAX_CONTENT_LENGTH'] = Config.MAX_CONTENT_LENGTH
    
    # Register routes
    register_routes(app)
    register_error_handlers(app)
    
    return app


def allowed_file(filename):
    """Check if file extension is allowed."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS


def register_routes(app):
    """Register all application routes."""
    
    @app.route('/')
    def home():
        """Home page with overview and features"""
        return render_template('home.html')

    @app.route('/upload')
    def upload_page():
        """Upload page for CV processing"""
        return render_template('index.html')

    @app.route('/about')
    def about():
        """About page with project information"""
        return render_template('about.html')

    @app.route('/process', methods=['POST'])
    def upload_file():
        """Handle CV upload and processing"""
        if 'pdf_file' not in request.files:
            flash('No file selected')
            return redirect(url_for('upload_page'))
        
        file = request.files['pdf_file']
        
        if file.filename == '':
            flash('No selected file')
            return redirect(url_for('upload_page'))
        
        if not allowed_file(file.filename):
            flash('Only PDF files are allowed')
            return redirect(url_for('upload_page'))
        
        # Get selected models - FIXED: handle both 'model' and 'models'
        selected_model = request.form.get('model')  # Single model from radio buttons
        if selected_model:
            models = [selected_model]
        else:
            models = request.form.getlist('models')  # Multiple models from checkboxes
            if not models:
                models = ['phi']  # Default to phi if none selected
        
        print(f"Selected models: {models}")
        
        # Save and process file
        try:
            unique_id = str(uuid.uuid4())
            safe_filename = create_safe_filename(file.filename)
            filename = f"{unique_id}_{safe_filename}"
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            # Process PDF and extract info
            results = process_pdf(filepath, models)
            
            # Save session and results
            session_id = unique_id
            session_file = os.path.join(app.config['RESULTS_FOLDER'], f"{session_id}_session.json")
            result_files = {}
            
            # Transform results to match template expectations
            transformed_results = {}
            for model, data in results.items():
                # Transform the nested structure to flat structure expected by template
                transformed_data = transform_data_structure(data)
                transformed_results[model] = transformed_data
                
                # Save transformed data
                result_file = os.path.join(app.config['RESULTS_FOLDER'], f"{session_id}_{model}_result.json")
                with open(result_file, 'w', encoding='utf-8') as f:
                    json.dump(transformed_data, f, indent=4, ensure_ascii=False)
                result_files[model] = result_file
            
            session_data = {
                'pdf_path': filepath,
                'results': transformed_results,  # Use transformed results
                'result_files': result_files,
                'original_filename': file.filename
            }
            
            with open(session_file, 'w', encoding='utf-8') as f:
                json.dump(session_data, f, indent=4, ensure_ascii=False)
            
            print(f"Processing complete. Redirecting to results page with session: {session_id}")
            return redirect(url_for('show_results', session_id=session_id))
            
        except Exception as e:
            flash(f'Error processing PDF: {str(e)}')
            print(f"Upload error: {str(e)}")
            return redirect(url_for('upload_page'))

    @app.route('/results/<session_id>')
    def show_results(session_id):
        """Display extraction results"""
        print(f"Loading results for session: {session_id}")
        session_file = os.path.join(app.config['RESULTS_FOLDER'], f"{session_id}_session.json")
        
        if not os.path.exists(session_file):
            flash('Session not found')
            print(f"Session file not found: {session_file}")
            return redirect(url_for('upload_page'))
        
        try:
            with open(session_file, 'r', encoding='utf-8') as f:
                session_data = json.load(f)
            
            pdf_path = session_data['pdf_path']
            results = session_data['results']
            original_filename = session_data.get('original_filename', 'Unknown')
            
            print(f"Loaded results keys: {list(results.keys()) if results else 'No results'}")
            
            # Generate URL for PDF viewing
            pdf_url = url_for('serve_pdf', session_id=session_id)
            
            # DEBUG: Print results structure
            if results:
                for model, data in results.items():
                    print(f"Model {model} data keys: {list(data.keys()) if data else 'No data'}")
            
            return render_template('results.html',  # FIXED: changed from result.html to results.html
                                 pdf_url=pdf_url, 
                                 results=results,
                                 original_filename=original_filename,
                                 session_id=session_id)
        except Exception as e:
            flash(f'Error loading results: {str(e)}')
            print(f"Results loading error: {str(e)}")
            return redirect(url_for('upload_page'))

    @app.route('/pdf/<session_id>')
    def serve_pdf(session_id):
        """Serve the uploaded PDF for viewing"""
        session_file = os.path.join(app.config['RESULTS_FOLDER'], f"{session_id}_session.json")
        
        if not os.path.exists(session_file):
            return redirect(url_for('upload_page'))
        
        try:
            with open(session_file, 'r', encoding='utf-8') as f:
                session_data = json.load(f)
            
            pdf_path = session_data['pdf_path']
            
            if not os.path.exists(pdf_path):
                flash('PDF file not found')
                return redirect(url_for('upload_page'))
            
            return send_file(pdf_path, mimetype='application/pdf')
        except Exception as e:
            flash(f'Error serving PDF: {str(e)}')
            return redirect(url_for('upload_page'))

    @app.route('/download/<model>')
    def download_result(model):
        """Download extraction results as JSON"""
        session_id = request.args.get('session_id')
        
        if not session_id:
            return redirect(url_for('upload_page'))
        
        session_file = os.path.join(app.config['RESULTS_FOLDER'], f"{session_id}_session.json")
        
        if not os.path.exists(session_file):
            return redirect(url_for('upload_page'))
        
        try:
            with open(session_file, 'r', encoding='utf-8') as f:
                session_data = json.load(f)
            
            result_file = session_data['result_files'].get(model)
            
            if not result_file or not os.path.exists(result_file):
                flash('Result file not found')
                return redirect(url_for('upload_page'))
            
            return send_file(result_file, mimetype='application/json', 
                           download_name=f"cv_extraction_{model}.json", as_attachment=True)
        except Exception as e:
            flash(f'Error downloading result: {str(e)}')
            return redirect(url_for('upload_page'))

    @app.route('/api/extract', methods=['POST'])
    def api_extract():
        """API endpoint for CV extraction"""
        if 'pdf_file' not in request.files:
            return jsonify({'error': 'No file part'}), 400
        
        file = request.files['pdf_file']
        
        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'File type not allowed'}), 400
        
        # Get the selected model
        model = request.form.get('model', Config.DEFAULT_MODEL)
        models = [model]
        
        try:
            # Save and process file
            unique_id = str(uuid.uuid4())
            safe_filename = create_safe_filename(file.filename)
            filename = f"{unique_id}_{safe_filename}"
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            # Process PDF and extract info
            results = process_pdf(filepath, models)
            
            return jsonify({'results': results})
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/health')
    def api_health():
        """Health check endpoint"""
        return jsonify({
            'status': 'healthy',
            'version': '1.0.0',
            'models_available': list(Config.MODELS.keys())
        })


def register_error_handlers(app):
    """Register error handlers."""
    
    @app.errorhandler(413)
    def request_entity_too_large(error):
        return render_template('error.html', 
                             error="File too large. Maximum size is 16MB."), 413

    @app.errorhandler(500)
    def internal_server_error(error):
        return render_template('error.html', 
                             error="Server error. Please try again later."), 500

    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('error.html', 
                             error="Page not found."), 404


def transform_data_structure(data):
    """Transform nested data structure to flat structure expected by template"""
    if not data:
        return {}
    
    if 'error' in data:
        return data
    
    transformed = {}
    
    # Extract personal info
    if 'personal_info' in data:
        personal_info = data['personal_info']
        transformed['Name'] = personal_info.get('name', '')
        transformed['Email'] = personal_info.get('email', '')
        transformed['Phone'] = personal_info.get('phone', '')
        transformed['Address'] = personal_info.get('address', '')
    
    # Fix descriptions - join single characters
    def fix_descriptions(items):
        for item in items:
            for key in ['description', 'Description']:
                if key in item and isinstance(item[key], list):
                    # Join if all items are single characters
                    if item[key] and all(len(str(x)) == 1 for x in item[key]):
                        item[key] = ''.join(item[key])
        return items
    
    transformed['Education'] = fix_descriptions(data.get('education', []))
    transformed['Experience'] = fix_descriptions(data.get('experience', []))
    transformed['Skills'] = data.get('skills', [])
    transformed['Languages'] = data.get('languages', [])
    
    if 'error' in data:
        transformed['error'] = data['error']
    
    return transformed

def process_pdf(pdf_path, models):
    """Process the PDF and extract information using selected models"""
    # Initialize PDF extractor
    pdf_extractor = ExtractFromPDF(
        poppler_path=Config.POPPLER_PATH,
        api_key=Config.GOOGLE_API_KEY
    )
    
    print(f"Processing PDF: {pdf_path}")
    
    try:
        # Extract text from PDF
        text = pdf_extractor.extract_text(pdf_path)
        
        if not text or len(text.strip()) < 10:
            return {
                "error": {
                    "error": "Could not extract meaningful text from PDF",
                    "personal_info": {
                        "name": "Extraction Error",
                        "email": "",
                        "phone": "",
                        "address": ""
                    },
                    "education": [],
                    "experience": [],
                    "skills": ["PDF extraction failed"],
                    "languages": []
                }
            }
        
        print(f"Extracted text length: {len(text)} characters")
        print(f"Text sample: {text[:200]}...")
        
        # Initialize CV extractor
        cv_extractor = CVInfoExtractor()
        
        # Process with each model
        results = {}
        for model in models:
            print(f"Processing with model: {model}")
            
            try:
                info = cv_extractor.extract_from_cv(text, model=model)
                results[model] = info
                print(f"Model {model} completed successfully")
                print(f"Model {model} result keys: {list(info.keys()) if info else 'No info'}")
                
            except Exception as e:
                print(f"Error with model {model}: {str(e)}")
                results[model] = {
                    "error": f"Model processing error: {str(e)}",
                    "personal_info": {
                        "name": "Processing Error",
                        "email": "",
                        "phone": "",
                        "address": ""
                    },
                    "education": [],
                    "experience": [],
                    "skills": ["Model processing failed"],
                    "languages": []
                }
        
        return results
        
    except Exception as e:
        print(f"PDF processing error: {str(e)}")
        return {
            "error": {
                "error": f"PDF processing failed: {str(e)}",
                "personal_info": {
                    "name": "Processing Error",
                    "email": "",
                    "phone": "",
                    "address": ""
                },
                "education": [],
                "experience": [],
                "skills": ["Processing failed"],
                "languages": []
            }
        }


# Create the Flask app instance
app = create_app()


if __name__ == '__main__':
    app.run(debug=Config.DEBUG, host=Config.HOST, port=Config.PORT)