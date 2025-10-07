"""
CV Extractor Web Application
----------------------------
Flask web interface for CV extraction and processing.
"""

from flask import Flask, render_template, request, redirect, url_for, send_file, jsonify, flash
import os
import uuid
import json
import sys
import time
from werkzeug.utils import secure_filename
from pathlib import Path
import threading

from cv_extractor.config import (
    FLASK_SECRET_KEY,
    UPLOAD_FOLDER,
    RESULTS_FOLDER,
    ALLOWED_EXTENSIONS,
    MAX_CONTENT_LENGTH,
    POPPLER_PATH,
    GOOGLE_API_KEY,
    PROJECT_ROOT,
    ensure_directories
)
from cv_extractor.pdf import ExtractFromPDF
from cv_extractor.llm import CVInfoExtractor

# Ensure directories exist
ensure_directories()

app = Flask(__name__, 
           template_folder='templates',
           static_folder='static')
app.secret_key = FLASK_SECRET_KEY

# Configuration
app.config['UPLOAD_FOLDER'] = str(UPLOAD_FOLDER)
app.config['RESULTS_FOLDER'] = str(RESULTS_FOLDER)
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


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
        return redirect(url_for('upload_page'))
    
    file = request.files['pdf_file']
    
    if file.filename == '':
        flash('No selected file')
        return redirect(url_for('upload_page'))
    
    if not allowed_file(file.filename):
        flash('Only PDF files are allowed')
        return redirect(url_for('upload_page'))
    
    # Get selected models
    models = request.form.getlist('models')
    if not models:
        models = ['phi', 'mistral', 'llama3']  # Default models
    
    # Save and process file
    unique_id = str(uuid.uuid4())
    secure_name = secure_filename(file.filename)
    filename = f"{unique_id}_{secure_name}"
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)
    
    # Process PDF and extract info
    try:
        results = process_pdf(filepath, models)
        
        # Debug duration fields for encoding issues
        for model, data in results.items():
            if 'Experience' in data and data['Experience']:
                for i, exp in enumerate(data['Experience']):
                    if 'duration' in exp and exp['duration']:
                        # Normalize duration field explicitly
                        original = exp['duration']
                        normalized = original
                        for char in ['\u2013', '\u2014', '\u2015', '\u2212', '\u2010', '\u2011', '\u2012', '\u2043']:
                            normalized = normalized.replace(char, '-')
                        
                        # Apply fix if needed
                        if original != normalized:
                            print(f"Duration field fixed: '{original}' → '{normalized}'")
                            print(f"Original chars: {[ord(c) for c in original]}")
                            exp['duration'] = normalized
        
        # Save session and results
        session_id = unique_id
        session_file = os.path.join(app.config['RESULTS_FOLDER'], f"{session_id}_session.json")
        result_files = {}
        
        for model, data in results.items():
            result_file = os.path.join(app.config['RESULTS_FOLDER'], f"{session_id}_{model}_result.json")
            # Only save the result file if it does not contain an error
            with open(result_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            result_files[model] = result_file
        
        session_data = {
            'pdf_path': filepath,
            'results': results,
            'result_files': result_files
        }
        
        with open(session_file, 'w', encoding='utf-8') as f:
            json.dump(session_data, f, indent=4, ensure_ascii=False)
        
        return redirect(url_for('show_results', session_id=session_id))
    except Exception as e:
        flash(f'Error processing PDF: {str(e)}')
        return redirect(url_for('upload_page'))


def process_pdf(pdf_path, models):
    """Process the PDF and extract information using selected models with timeout fallback"""
    # Initialize PDF extractor with Gemini
    pdf_extractor = ExtractFromPDF(
        poppler_path=POPPLER_PATH,
        api_key=GOOGLE_API_KEY
    )
    
    # Create a results container that can be accessed by both threads
    results_container = {"text": None, "error": None}
    
    # Define the primary PDF extraction function
    def extract_text_primary():
        try:
            # Check if PDF is text-based or image-based
            print(f"Checking if PDF is text-based or scanned: {pdf_path}")
            is_scanned = not pdf_extractor.is_text_based_pdf(pdf_path)
            
            if is_scanned:
                print("Processing as scanned PDF with Gemini OCR...")
                results_container["text"] = pdf_extractor.extract_from_scanned_pdf(pdf_path)
                print(f"Scanned PDF extracted text length: {len(results_container['text']) if results_container['text'] else 0}")
            else:
                print("Processing as text-based PDF with PyMuPDF...")
                results_container["text"] = pdf_extractor.extract_text_from_pdf(pdf_path)
                print(f"Text-based PDF extracted text length: {len(results_container['text']) if results_container['text'] else 0}")
        except Exception as e:
            error_msg = f"Error in primary extraction: {str(e)}"
            print(error_msg)
            results_container["error"] = error_msg
    
    # Define fallback method
    def extract_text_fallback():
        try:
            # Try the opposite method
            is_scanned = not pdf_extractor.is_text_based_pdf(pdf_path)
            
            if not is_scanned:  # Inverse of primary
                print("Fallback: Processing as scanned PDF with Gemini OCR...")
                text = pdf_extractor.extract_from_scanned_pdf(pdf_path)
                print(f"Fallback scanned PDF extracted text length: {len(text) if text else 0}")
                return text
            else:
                print("Fallback: Processing as text-based PDF with PyMuPDF...")
                text = pdf_extractor.extract_text_from_pdf(pdf_path)
                print(f"Fallback text-based PDF extracted text length: {len(text) if text else 0}")
                return text
        except Exception as e:
            error_msg = f"Error in fallback extraction: {str(e)}"
            print(error_msg)
            # If all fails, return a placeholder text
            return f"Failed to extract text from PDF. Error: {str(e)}"
    
    # Start extraction in a separate thread
    extraction_thread = threading.Thread(target=extract_text_primary)
    extraction_thread.start()
    
    # Wait for the thread to complete with a timeout
    timeout = 100  # 100 seconds timeout
    start_time = time.time()
    
    # Wait for extraction to complete or timeout
    extraction_thread.join(timeout)
    
    # Check if extraction completed in time
    if extraction_thread.is_alive() or results_container["error"] is not None:
        print(f"Primary extraction timed out after {timeout} seconds or encountered an error. Using fallback method.")
        # Thread is still running or there was an error - use fallback
        text = extract_text_fallback()
    else:
        text = results_container["text"]
    
    print(f"Text extraction completed in {time.time() - start_time:.2f} seconds")
    
    # If text is None or empty after both attempts, return a meaningful error
    if not text:
        print("ERROR: Failed to extract any text from the PDF file.")
        return {"error": {"error": "Could not extract text from PDF", 
                         "Name": "Extraction Error",
                         "Email": "",
                         "Phone": "",
                         "Address": "",
                         "Education": [],
                         "Experience": [],
                         "Skills": ["PDF extraction failed"]}}
    
    # Print the first few characters of the extracted text for debugging
    print(f"Extracted text sample: {text[:200]}...")
    
    # Initialize CVInfoExtractor
    cv_extractor = CVInfoExtractor()
    
    # Process with the LLM models
    results = {}
    for model in models:
        processing_start = time.time()
        print(f"Processing with model {model}...")
        
        # Process the text with timeout
        try:
            # Set a timeout for LLM processing - CVInfoExtractor handles this internally
            info = cv_extractor.extract_from_cv(cv_text=text)
            
            # Print a sample of the result for debugging
            print(f"LLM processing result: {str(info)[:200]}...")
            
            if "error" in info:
                print(f"ERROR: LLM processing error: {info.get('error')}")
                
            results[model] = info
            print(f"Model {model} completed in {time.time() - processing_start:.2f} seconds")
        except Exception as e:
            error_str = str(e)
            error_msg = f"Error extracting with model {model}: {error_str}"
            print(error_msg)
            
            # Handle the specific Llama3 error pattern (quoted field structure)
            friendly_error = error_str
            if '\\n "Name"' in error_str or error_str.startswith('"Name"'):
                friendly_error = "Model returned improperly formatted JSON. Try another model."
                
            results[model] = {
                "Name": "Processing Error",
                "Email": "",
                "Phone": "",
                "Address": "",
                "Education": [],
                "Experience": [],
                "Skills": ["The model returned an incomplete response. Try using another model."],
            }
    
    return results


@app.route('/results/<session_id>')
def show_results(session_id):
    """Display extraction results"""
    session_file = os.path.join(app.config['RESULTS_FOLDER'], f"{session_id}_session.json")
    
    if not os.path.exists(session_file):
        return redirect(url_for('upload_page'))
    
    with open(session_file, 'r') as f:
        session_data = json.load(f)
    
    pdf_path = session_data['pdf_path']
    results = session_data['results']
    
    # Generate URL for PDF viewing
    pdf_url = url_for('serve_pdf', session_id=session_id)
    
    return render_template('result.html', pdf_url=pdf_url, results=results)


@app.route('/pdf/<session_id>')
def serve_pdf(session_id):
    """Serve the uploaded PDF for viewing"""
    session_file = os.path.join(app.config['RESULTS_FOLDER'], f"{session_id}_session.json")
    
    if not os.path.exists(session_file):
        return redirect(url_for('upload_page'))
    
    with open(session_file, 'r') as f:
        session_data = json.load(f)
    
    pdf_path = session_data['pdf_path']
    
    return send_file(pdf_path, mimetype='application/pdf')


@app.route('/download/<model>')
def download_result(model):
    """Download extraction results as JSON"""
    session_id = request.args.get('session_id')
    
    if not session_id:
        return redirect(url_for('upload_page'))
    
    session_file = os.path.join(app.config['RESULTS_FOLDER'], f"{session_id}_session.json")
    
    if not os.path.exists(session_file):
        return redirect(url_for('upload_page'))
    
    with open(session_file, 'r') as f:
        session_data = json.load(f)
    
    result_file = session_data['result_files'].get(model)
    
    if not result_file or not os.path.exists(result_file):
        return redirect(url_for('upload_page'))
    
    return send_file(result_file, mimetype='application/json', 
                     download_name=f"cv_extraction_{model}.json", as_attachment=True)


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
    
    # Get the single selected model
    model = request.form.get('model', 'phi')  # Default to phi if none specified
    models = [model]
    
    # Save and process file
    unique_id = str(uuid.uuid4())
    secure_name = secure_filename(file.filename)
    filename = f"{unique_id}_{secure_name}"
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)
    
    # Process PDF and extract info
    results = process_pdf(filepath, models)
    
    return jsonify({'results': results})


@app.errorhandler(413)
def request_entity_too_large(error):
    return render_template('error.html', error="File too large. Maximum size is 16MB."), 413


@app.errorhandler(500)
def internal_server_error(error):
    return render_template('error.html', error="Server error. Please try again later."), 500


if __name__ == '__main__':
    from cv_extractor.config import FLASK_PORT, FLASK_DEBUG
    app.run(debug=FLASK_DEBUG, host='0.0.0.0', port=FLASK_PORT)
