"""
Utility functions for CV Extractor
"""

import os
import json
from pathlib import Path
from typing import Any, Dict, List
import hashlib
import tempfile
import shutil

from app.config import Config


def ensure_directories():
    """Create necessary directories if they don't exist."""
    Config.ensure_directories()


def validate_file(file_path: str, allowed_extensions: set = None) -> bool:
    """Validate if file exists and has allowed extension."""
    if allowed_extensions is None:
        allowed_extensions = Config.ALLOWED_EXTENSIONS
    
    file_path = Path(file_path)
    
    if not file_path.exists():
        return False
    
    if file_path.suffix.lower().lstrip('.') not in allowed_extensions:
        return False
    
    return True


def get_file_hash(file_path: str) -> str:
    """Generate MD5 hash of a file."""
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


def save_json(data: Dict[str, Any], file_path: str) -> bool:
    """Save data as JSON file."""
    try:
        file_path = Path(file_path)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        return True
    except Exception as e:
        print(f"Error saving JSON: {e}")
        return False


def load_json(file_path: str) -> Dict[str, Any]:
    """Load data from JSON file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading JSON: {e}")
        return {}


def clean_temp_files(directory: str, max_age_hours: int = 24):
    """Clean temporary files older than specified hours."""
    import time
    
    directory = Path(directory)
    if not directory.exists():
        return
    
    current_time = time.time()
    max_age_seconds = max_age_hours * 3600
    
    for file_path in directory.iterdir():
        if file_path.is_file():
            file_age = current_time - file_path.stat().st_mtime
            if file_age > max_age_seconds:
                try:
                    file_path.unlink()
                    print(f"Cleaned temp file: {file_path.name}")
                except Exception as e:
                    print(f"Error cleaning {file_path.name}: {e}")


def format_file_size(size_bytes: int) -> str:
    """Format file size in human readable format."""
    if size_bytes == 0:
        return "0B"
    
    size_names = ["B", "KB", "MB", "GB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.1f}{size_names[i]}"


def create_safe_filename(filename: str) -> str:
    """Create a safe filename by removing/replacing invalid characters."""
    import re
    
    # Remove or replace invalid characters
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    
    # Remove leading/trailing spaces and dots
    filename = filename.strip(' .')
    
    # Ensure filename is not empty
    if not filename:
        filename = "unnamed_file"
    
    return filename


def get_unique_filename(directory: str, filename: str) -> str:
    """Get a unique filename by adding numbers if file exists."""
    directory = Path(directory)
    file_path = directory / filename
    
    if not file_path.exists():
        return filename
    
    name_part = file_path.stem
    extension = file_path.suffix
    counter = 1
    
    while file_path.exists():
        new_filename = f"{name_part}_{counter}{extension}"
        file_path = directory / new_filename
        counter += 1
    
    return file_path.name


def copy_file_safely(source: str, destination: str) -> bool:
    """Copy file with error handling."""
    try:
        source_path = Path(source)
        dest_path = Path(destination)
        
        # Create destination directory if needed
        dest_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Copy file
        shutil.copy2(source_path, dest_path)
        return True
        
    except Exception as e:
        print(f"Error copying file: {e}")
        return False


def validate_json_structure(data: Dict[str, Any], required_fields: List[str]) -> bool:
    """Validate if JSON data has required fields."""
    try:
        for field in required_fields:
            if field not in data:
                return False
        return True
    except Exception:
        return False


def sanitize_text(text: str) -> str:
    """Sanitize text by removing unwanted characters."""
    import re
    
    if not text:
        return ""
    
    # Remove control characters except newlines and tabs
    text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]', '', text)
    
    # Normalize whitespace
    text = re.sub(r'\s+', ' ', text)
    
    return text.strip()


def create_backup(file_path: str, backup_dir: str = None) -> str:
    """Create a backup of a file."""
    import datetime
    
    file_path = Path(file_path)
    
    if backup_dir is None:
        backup_dir = file_path.parent / "backups"
    else:
        backup_dir = Path(backup_dir)
    
    backup_dir.mkdir(parents=True, exist_ok=True)
    
    # Create backup filename with timestamp
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_filename = f"{file_path.stem}_{timestamp}{file_path.suffix}"
    backup_path = backup_dir / backup_filename
    
    # Copy file to backup location
    if copy_file_safely(str(file_path), str(backup_path)):
        return str(backup_path)
    else:
        return ""


def log_processing_stats(stats: Dict[str, Any], log_file: str = None):
    """Log processing statistics."""
    import datetime
    
    if log_file is None:
        log_file = Config.DATA_DIR / "processing_log.json"
    
    log_entry = {
        "timestamp": datetime.datetime.now().isoformat(),
        "stats": stats
    }
    
    # Load existing log
    log_data = []
    if Path(log_file).exists():
        log_data = load_json(log_file)
        if not isinstance(log_data, list):
            log_data = []
    
    # Add new entry
    log_data.append(log_entry)
    
    # Keep only last 100 entries
    log_data = log_data[-100:]
    
    # Save updated log
    save_json(log_data, log_file)


def get_system_info() -> Dict[str, Any]:
    """Get system information for debugging."""
    import platform
    import psutil
    
    return {
        "platform": platform.platform(),
        "python_version": platform.python_version(),
        "cpu_count": psutil.cpu_count(),
        "memory_total": psutil.virtual_memory().total,
        "memory_available": psutil.virtual_memory().available,
        "disk_usage": psutil.disk_usage('/').percent if os.name != 'nt' else psutil.disk_usage('C:').percent
    }
