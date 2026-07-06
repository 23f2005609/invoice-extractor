import os
import json
import dateutil.parser
from dotenv import load_dotenv
from google import genai

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def extract_invoice_info(text: str) -> dict:
    # Use a prompt that explicitly handles the "null" requirement
    prompt = f"""
    You are an invoice extraction API. Extract these fields from the text below.
    If a field is not present, you MUST return null for that field.
    
    Required JSON keys:
    - "invoice_no": string or null
    - "date": string "YYYY-MM-DD" or null
    - "vendor": string or null
    - "amount": number or null (Subtotal before tax)
    - "tax": number or null (Tax amount only)
    - "currency": string or null
    
    Text: {text}
    """
    
    default_response = {
        "invoice_no": None, "date": None, "vendor": None, 
        "amount": None, "tax": None, "currency": None
    }
    
    try:
        response = client.models.generate_content(
            model="gemini-1.5-flash",
            contents=prompt,
            config={"response_mime_type": "application/json"},
        )
        
        data = json.loads(response.text)
        
        # Ensure every required key exists, even if the model missed it
        final = {k: data.get(k) for k in default_response.keys()}
        
        # Force Date format
        if final['date']:
            try:
                final['date'] = dateutil.parser.parse(str(final['date'])).strftime("%Y-%m-%d")
            except:
                final['date'] = None
        
        # Force numeric types
        for k in ['amount', 'tax']:
            if final[k] is not None:
                try:
                    final[k] = float(final[k])
                except:
                    final[k] = None
                    
        return final
        
    except:
        return default_response