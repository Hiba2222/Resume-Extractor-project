"""
Evaluation Configuration
Clean and standardized field definitions for CV evaluation
"""

# Standard CV fields to evaluate
EVALUATION_FIELDS = {
    'name': {
        'type': 'string',
        'weight': 0.15,
        'description': 'Full name of the candidate'
    },
    'email': {
        'type': 'string', 
        'weight': 0.10,
        'description': 'Email address'
    },
    'phone': {
        'type': 'string',
        'weight': 0.10, 
        'description': 'Phone number'
    },
    'skills': {
        'type': 'list',
        'weight': 0.25,
        'description': 'List of technical and soft skills'
    },
    'education': {
        'type': 'complex',
        'weight': 0.20,
        'description': 'Educational background',
        'subfields': ['degree', 'institution', 'year']
    },
    'experience': {
        'type': 'complex', 
        'weight': 0.20,
        'description': 'Work experience',
        'subfields': ['job_title', 'company', 'duration', 'description']
    }
}

# Model configurations
MODELS = {
    'llama3': {
        'name': 'Llama 3',
        'expected_quality': 0.90,
        'description': 'Meta Llama 3 model'
    },
    'mistral': {
        'name': 'Mistral',
        'expected_quality': 0.85,
        'description': 'Mistral AI model'
    },
    'phi': {
        'name': 'Phi',
        'expected_quality': 0.80,
        'description': 'Microsoft Phi model'
    }
}

# Evaluation thresholds
QUALITY_THRESHOLDS = {
    'excellent': 0.90,
    'good': 0.80,
    'fair': 0.70,
    'poor': 0.60
}

# Field type definitions
FIELD_TYPES = {
    'string': ['name', 'email', 'phone'],
    'list': ['skills'],
    'complex': ['education', 'experience']
}

def get_field_names():
    """Get list of all evaluation field names"""
    return list(EVALUATION_FIELDS.keys())

def get_field_weights():
    """Get dictionary of field weights"""
    return {field: config['weight'] for field, config in EVALUATION_FIELDS.items()}

def get_models():
    """Get list of available models"""
    return list(MODELS.keys())

def get_quality_level(score):
    """Get quality level description for a score"""
    if score >= QUALITY_THRESHOLDS['excellent']:
        return 'excellent'
    elif score >= QUALITY_THRESHOLDS['good']:
        return 'good'
    elif score >= QUALITY_THRESHOLDS['fair']:
        return 'fair'
    else:
        return 'poor'
