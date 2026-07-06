import os
import json
import dateutil.parser
from dotenv import load_dotenv
from google import genai

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def extract_invoice_info(text: str) -> dict:
    prompt = f"""
    Extract the following fields from the invoice text.
    Return ONLY valid JSON.
    Fields: invoice_no, date (YYYY-MM-DD), vendor, amount (number), tax (number), currency.
    If a field is missing, use null.
    
    Invoice Text: {text}
    """
    
    try:
        response = client.models.generate_content(
            model="gemini-1.5-flash",
            contents=prompt,
            config={"response_mime_type": "application/json"},
        )
        
        # Parse the JSON response
        data = json.loads(response.text)
        
        # Clean the date
        if data.get('date'):
            try:
                data['date'] = dateutil.parser.parse(str(data['date'])).strftime("%Y-%m-%d")
            except:
                pass
        
        # Ensure numbers are floats
        for field in ['amount', 'tax']:
            if data.get(field) is not None:
                data[field] = float(data[field])
        
        return data
        
    except Exception as e:
        # Return a default object if LLM fails, instead of crashing
        return {
            "invoice_no": None, "date": None, "vendor": None, 
            "amount": None, "tax": None, "currency": None
        }