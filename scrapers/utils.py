import re
from urllib.parse import urlparse
import os
import google.generativeai as genai
import json
from dotenv import load_dotenv
load_dotenv()

try:
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY environment variable not set.")
    genai.configure(api_key=GEMINI_API_KEY)
    print("Gemini API configured successfully.")
except Exception as e:
    print(f"Error configuring Gemini API: {e}")
    print("Please ensure you have set the GEMINI_API_KEY environment variable.")
    exit()


MODEL_NAME = "gemini-1.5-flash-latest" 
model = genai.GenerativeModel(MODEL_NAME)

def analyze_url(url: str):
    parsed = urlparse(url)
    netloc = parsed.netloc

    # Handle cases like "example.com" or "www.example.com"
    if netloc == "":
        netloc = parsed.path  # fallback if urlparse fails on incomplete URLs

    # Check for 'www' prefix
    has_www = 1 if netloc.startswith("www.") else 0

    # Remove 'www.' if present for domain analysis
    domain = netloc[4:] if has_www else netloc

    # Split domain into name and top-level domain
    domain_parts = domain.split('.')
    domain_name = domain_parts[0]
    top_domain = domain_parts[-1] if len(domain_parts) > 1 else ''

    # Metrics
    domain_length = len(domain_name)
    top_domain_length = len(top_domain)
    num_digits = len(re.findall(r'\d', url))
    num_letters = len(re.findall(r'[a-zA-Z]', url))
    num_dots = url.count('.')
    num_hyphens = url.count('-')

    # Shortened domain like 'amazon.com' or just 'x' for 'x.com'
    shortened_url = domain
    return [domain_length, top_domain_length, has_www, num_digits, num_letters, num_dots, num_hyphens], shortened_url



def analyze_website_features(website_url: str) -> dict:
    """
    Analyzes a website using the Gemini API to check for specific features.

    Args:
        website_url: The URL of the website to analyze.

    Returns:
        A dictionary containing the analysis results or an error message.
    """
    # Simplified prompt. We will instruct the model to use JSON output directly.
    prompt = f"""
Analyze the website at the following URL: {website_url}

Based on the content of the site, determine the availability of the following features.
- Credit card payment
- Money-back option
- Cash on delivery
- Cryptocurrency payment
- A free contact email (like gmail, yahoo, etc.)
- A company logo

Return a JSON object with the following keys and boolean values (1 or 0):
"Has credit card payment"
"Has money-back option"
"Has cash on delivery"
"Accepts crypto"
"Has free contact email"
"Has logo"

If you are unsure about a feature, the value should be false(0).
If a website url seems to be a typo, then ignore that and consider only teh raw URL provided to you. 
Lets say I give you a url aamazon, consider it only as aamazon and don't correct it to amazon
"""

    try:
        # Configure the model to output a JSON response directly.
        # This is more reliable than parsing a manually formatted string.
        generation_config = genai.types.GenerationConfig(response_mime_type="application/json")

        # Generate content using the model. This is for a single-turn request.
        response = model.generate_content(prompt, generation_config=generation_config)
        
        # The generated text is in response.text, which is now a valid JSON string.
        text_content = response.text

        # Parse the JSON string into a Python dictionary.
        print(len(json.loads(text_content)))
        return json.loads(text_content)

    except json.JSONDecodeError as e:
        return {
            "Has credit card payment": 0,
            "Has money-back option": 0,
            "Has cash on delivery": 0,
            "Accepts crypto": 0,
            "Has free contact email": 0,
            "Has logo": 0
}
    except Exception as e:
        # Catch other potential errors from the API call, including value errors for unsupported formats.
        return  {
            "Has credit card payment": 0,
            "Has money-back option": 0,
            "Has cash on delivery": 0,
            "Accepts crypto": 0,
            "Has free contact email": 0,
            "Has logo": 0
}



# url = "https://www.amazon.com/shopping/product/123"
# result = analyze_url(url)
# print(result)
