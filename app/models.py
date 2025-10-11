"""
LLM CV Information Extraction Module
------------------------------------
Extract structured information from CV text using various LLM models.
"""

import json
import requests
import time
import os
import re
import hashlib
from pathlib import Path
import threading
import concurrent.futures
from typing import Dict, Any, Optional

from app.config import Config


class CVInfoExtractor:
    """Extract structured information from CV text using LLM models."""
    
    def __init__(self):
        self.config = Config()
        self.cache_dir = self.config.DATA_DIR / 'cache'
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Model settings
        self.models = ['llama3:latest', 'phi:latest', 'mistral:latest']
        self.openrouter_models = [
            'mistralai/mistral-7b-instruct:free',
            'shisa-ai/shisa-v2-llama3.3-70b:free',
            'cognitivecomputations/dolphin3.0-mistral-24b:free'
        ]
        
        # Optimized extraction prompt template for maximum accuracy
        self.extraction_prompt = """You are a professional CV data extraction specialist. Extract information from this resume with 100% accuracy and completeness.

CRITICAL EXTRACTION RULES:
1. Extract EXACTLY what is written - do not infer, guess, or paraphrase
2. Maintain original spelling, capitalization, and formatting
3. Include ALL skills mentioned anywhere in the document
4. Capture ALL education entries (degrees, certifications, courses)
5. Record ALL work experience (jobs, internships, projects)
6. Find contact information from header/footer sections
7. Return ONLY valid JSON - no explanations, markdown, or code blocks

REQUIRED JSON STRUCTURE:
{{
"personal_info": {{
    "name": "Complete full name as written on CV",
    "email": "Exact email address with correct domain", 
    "phone": "Complete phone number with all formatting",
    "address": "Full address if mentioned anywhere"
}},
"education": [
    {{
    "degree": "Complete degree/qualification name exactly as written",
    "institution": "Full institution name without abbreviations",
    "year": "Exact graduation year or date range",
    "description": "Additional details like GPA, honors, relevant coursework"
    }}
],
"experience": [
    {{
    "job_title": "Complete job title/position exactly as written",
    "company": "Full company/organization name", 
    "duration": "Exact employment period (start-end dates)",
    "description": "Key responsibilities, achievements, and impact"
    }}
],
"skills": [
    "List every single skill mentioned",
    "Include programming languages",
    "Include software and tools",
    "Include technical skills",
    "Include soft skills",
    "Include certifications",
    "Preserve exact wording and spelling"
],
"languages": ["Every language mentioned with proficiency level if stated"]
}}

EXTRACTION PRIORITY:
- Personal info: Check header, footer, contact sections
- Skills: Scan entire document including experience descriptions
- Education: Look for degrees, certifications, training, courses
- Experience: Include all work history, internships, projects
- Languages: Check skills section and personal details

ACCURACY IS CRITICAL. EXTRACT EVERYTHING. RETURN ONLY JSON.

CV Text:
{{cv_text}}"""
    
    def check_ollama_available(self):
        """Verify Ollama API is running"""
        try:
            r = requests.get("http://localhost:11434/api/version", timeout=5)
            r.raise_for_status()
            print(f"✅ Ollama is running (version: {r.json().get('version', 'unknown')})")
            return True
        except requests.exceptions.RequestException as e:
            print(f"❌ Ollama is not available: {e}")
            return False
    
    def check_openrouter_available(self):
        """Verify OpenRouter API is available"""
        if not self.config.OPENROUTER_API_KEY:
            print("❌ OpenRouter API key is not configured")
            return False
        
        try:
            r = requests.get(
                f"{self.config.OPENROUTER_BASE_URL}/auth/key",
                headers={"Authorization": f"Bearer {self.config.OPENROUTER_API_KEY}"},
                timeout=5
            )
            r.raise_for_status()
            print("✅ OpenRouter API connection successful")
            return True
        except requests.exceptions.RequestException as e:
            print(f"❌ OpenRouter API is not available: {e}")
            return False
    
    def get_cache_key(self, cv_text, model):
        """Generate a cache key based on model and CV text"""
        content = f"{model}:{cv_text}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def get_from_cache(self, cache_key):
        """Get result from cache if available"""
        cache_file = self.cache_dir / f"{cache_key}.json"
        if cache_file.exists():
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    print("📂 Using cached result")
                    return json.load(f)
            except Exception as e:
                print(f"⚠️ Cache error: {e}")
                return None
        return None
    
    def save_to_cache(self, cache_key, result):
        """Save result to cache"""
        cache_file = self.cache_dir / f"{cache_key}.json"
        try:
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
                print("📥 Result cached successfully")
        except Exception as e:
            print(f"⚠️ Error saving to cache: {e}")
    
    def call_ollama_api(self, model, prompt):
        """Call Ollama API with retry logic"""
        print(f"🔄 Using Ollama model: {model}")
        
        # Check if model is available
        try:
            model_response = requests.get(f"http://localhost:11434/api/tags", timeout=5)
            local_models = [m["name"] for m in model_response.json().get("models", [])]
            
            if model not in local_models and not model.endswith(':latest'):
                base_model = model.split(':')[0]
                if f"{base_model}:latest" not in local_models:
                    print(f"⚠️ Model '{model}' is not available locally.")
                    return None
        except requests.exceptions.RequestException:
            print("⚠️ Could not check available models. Proceeding anyway.")
        
        # Prepare payload
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.01,
                "num_predict": self.config.CONTEXT_LENGTH,
                "num_ctx": self.config.CONTEXT_LENGTH
            }
        }
        
        try:
            response = requests.post(
                self.config.OLLAMA_API_URL,
                json=payload,
                timeout=self.config.REQUEST_TIMEOUT
            )
            response.raise_for_status()
            
            result = response.json()
            if 'response' in result:
                return result['response']
            else:
                print(f"⚠️ Unexpected response format from Ollama")
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"⚠️ Ollama API error: {e}")
            return None
    
    def call_openrouter_api(self, prompt):
        """Call OpenRouter API with fallback models"""
        if not self.config.OPENROUTER_API_KEY:
            print("❌ OpenRouter API key not configured")
            return None
            
        print("🌐 Falling back to OpenRouter API")
        
        # Try each OpenRouter model in sequence
        for model in self.openrouter_models:
            try:
                print(f"🔄 Using OpenRouter model: {model}")
                
                # Enhanced system message for JSON output
                system_message = """You are a CV information extractor that outputs ONLY valid JSON.
                IMPORTANT: Your entire response must be ONLY raw JSON with no markdown formatting, 
                no code blocks, and no explanatory text."""
                
                # Prepare the payload
                payload = {
                    "model": model,
                    "messages": [
                        {"role": "system", "content": system_message},
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.1,
                    "max_tokens": 2048,
                    "response_format": {"type": "json_object"}
                }
                
                # Make the API call
                headers = {
                    "Authorization": f"Bearer {self.config.OPENROUTER_API_KEY}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": "https://cv-extractor.app"
                }
                
                print(f"📡 Sending request to OpenRouter API...")
                response = requests.post(
                    f"{self.config.OPENROUTER_BASE_URL}/chat/completions",
                    headers=headers,
                    json=payload,
                    timeout=self.config.REQUEST_TIMEOUT
                )
                
                # Check for HTTP errors
                if response.status_code != 200:
                    print(f"⚠️ OpenRouter API returned status code {response.status_code}")
                    continue
                
                # Parse the response
                response_data = response.json()
                if 'choices' in response_data and len(response_data['choices']) > 0:
                    response_text = response_data['choices'][0]['message']['content']
                    print(f"✅ OpenRouter API request successful")
                    return response_text
                else:
                    print(f"⚠️ OpenRouter API returned empty response")
                    continue
                    
            except requests.exceptions.RequestException as e:
                print(f"⚠️ OpenRouter API error with model {model}: {e}")
                continue
        
        # If we get here, all models failed
        print(f"❌ All OpenRouter models failed")
        return None

    def extract_json_from_response(self, response: str) -> Dict[str, Any]:
        """Extract and parse JSON from the response"""
        if not response:
            return {"error": "Empty response"}
        
        try:
            # Clean the response to extract JSON
            print("🔍 Extracting JSON from response...")
            
            # Find the first opening brace and last closing brace
            first_brace = response.find('{')
            last_brace = response.rfind('}')
            
            if first_brace == -1 or last_brace == -1 or first_brace > last_brace:
                # Try to find code block markers
                json_start = response.find('```json')
                json_end = response.rfind('```')
                
                if json_start != -1 and json_end != -1 and json_start < json_end:
                    # Extract JSON from code block
                    json_content = response[json_start + 7:json_end].strip()
                    parsed_result = json.loads(json_content)
                else:
                    return {"error": "Could not find valid JSON in response"}
            else:
                # Extract the JSON part
                json_str = response[first_brace:last_brace + 1]
                parsed_result = json.loads(json_str)
            
            # Normalize the result to expected format
            if isinstance(parsed_result, dict):
                normalized = self._normalize_extraction_result(parsed_result)
                return normalized
            else:
                return {"error": "Invalid JSON structure"}
            
        except json.JSONDecodeError as e:
            print(f"❌ JSON parse error: {str(e)}")
            return {
                "error": f"JSON parsing error: {str(e)}",
                "raw_response": response[:100] + "..." if len(response) > 100 else response
            }
        except Exception as e:
            print(f"❌ Error extracting JSON: {str(e)}")
            return {
                "error": f"JSON extraction error: {str(e)}",
                "raw_response": response[:100] + "..." if len(response) > 100 else response
            }
    
    def _normalize_extraction_result(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize extraction result to standard format"""
        normalized = {
            "personal_info": {},
            "education": [],
            "experience": [],
            "skills": [],
            "languages": []
        }
        
        # Handle different field name variations
        for key, value in result.items():
            key_lower = key.lower()
            
            if key_lower in ['name', 'fullname', 'full_name']:
                normalized["personal_info"]["name"] = value
            elif key_lower in ['email', 'email_address']:
                normalized["personal_info"]["email"] = value
            elif key_lower in ['phone', 'phone_number']:
                normalized["personal_info"]["phone"] = value
            elif key_lower in ['address', 'location']:
                normalized["personal_info"]["address"] = value
            elif key_lower == 'personal_info' and isinstance(value, dict):
                normalized["personal_info"].update(value)
            elif key_lower in ['education', 'educations']:
                normalized["education"] = value if isinstance(value, list) else []
            elif key_lower in ['experience', 'work_experience', 'employment']:
                normalized["experience"] = value if isinstance(value, list) else []
            elif key_lower == 'skills':
                normalized["skills"] = value if isinstance(value, list) else []
            elif key_lower in ['languages', 'language']:
                normalized["languages"] = value if isinstance(value, list) else []
        
        return normalized
    
    def extract_from_cv(self, cv_text, model=None):
        """Extract structured information from CV text"""
        if model is None:
            model = self.config.DEFAULT_MODEL
        
        try:
            # Format prompt with escaped curly braces in cv_text to prevent format errors
            escaped_cv_text = cv_text.replace("{", "{{").replace("}", "}}")
            prompt = self.extraction_prompt.format(cv_text=escaped_cv_text)
        except KeyError as e:
            print(f"⚠️ Error formatting prompt: {e}")
            # Fallback approach: manually insert the CV text
            parts = self.extraction_prompt.split("{cv_text}")
            if len(parts) == 2:
                prompt = parts[0] + cv_text + parts[1]
            else:
                # Last resort
                prompt = f"""Extract structured information from this CV as JSON: {cv_text}
                Return ONLY a valid JSON object with personal_info, education, experience, skills and languages fields."""
        
        result = None
        
        # First try Ollama models
        ollama_available = self.check_ollama_available()
        if ollama_available:
            for model_name in self.models:
                # Check cache first
                cache_key = self.get_cache_key(cv_text, model_name)
                cached_result = self.get_from_cache(cache_key)
                if cached_result:
                    return cached_result
                
                print(f"\n🔄 Trying model: {model_name}")
                
                # Call model
                response = self.call_ollama_api(model_name, prompt)
                if response:
                    result = self.extract_json_from_response(response)
                    if "error" not in result:
                        # Cache successful result
                        self.save_to_cache(cache_key, result)
                        return result
                    else:
                        print(f"⚠️ Model {model_name} gave error: {result.get('error')}")
                        continue
        
        # If Ollama failed, try OpenRouter
        print("\n🌐 Trying OpenRouter API...")
        if self.check_openrouter_available():
            # Check OpenRouter cache
            cache_key = self.get_cache_key(cv_text, "openrouter")
            cached_result = self.get_from_cache(cache_key)
            if cached_result:
                return cached_result
                
            # Call OpenRouter API
            response = self.call_openrouter_api(prompt)
            if response:
                result = self.extract_json_from_response(response)
                if "error" not in result:
                    # Cache successful result
                    self.save_to_cache(cache_key, result)
                    return result
        
        # If all methods failed
        print("❌ All extraction methods failed")
        return {
            "error": "All extraction methods failed",
            "personal_info": {
                "name": "Extraction Failed",
                "email": "",
                "phone": "",
                "address": ""
            },
            "education": [],
            "experience": [],
            "skills": [],
            "languages": []
        }


def main():
    """Main function for command line usage."""
    print("🚀 Starting CV Information Extractor")
    
    import argparse
    parser = argparse.ArgumentParser(description="Extract structured information from CV text")
    parser.add_argument("--input", "-i", help="Input text file path", type=str, required=True)
    parser.add_argument("--output", "-o", help="Output JSON file path", type=str)
    parser.add_argument("--model", "-m", help="Model to use", type=str, default="llama3")
    args = parser.parse_args()
    
    extractor = CVInfoExtractor()
    
    input_path = Path(args.input)
    if not input_path.exists():
        print(f"❌ Input file not found: {input_path}")
        return
    
    # Read input file
    with open(input_path, 'r', encoding='utf-8') as f:
        cv_text = f.read().strip()
    
    if not cv_text:
        print("❌ Input file is empty")
        return
    
    print(f"📝 Processing {len(cv_text)} characters")
    
    # Extract information
    result = extractor.extract_from_cv(cv_text, args.model)
    
    # Save result
    if args.output:
        output_path = Path(args.output)
    else:
        output_path = input_path.with_suffix('.json')
    
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Result saved to: {output_path}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 Process interrupted by user")
    except Exception as e:
        print(f"💥 Unexpected error: {str(e)}")
        import traceback
        traceback.print_exc()
