import os
import json
import dateutil.parser
from dotenv import load_dotenv
from google import genai

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def extract_invoice_info(text: str) -> dict:
    # 1. Explicitly ask for nulls if not found
    prompt = f"""
    Extract the following fields from the invoice text.
    Return ONLY valid JSON.
    Fields: invoice_no, date, vendor, amount, tax, currency.
    If a field is NOT found, set its value to null.
    
    Invoice Text:
    {text}
    """
    
    try:
        response = client.models.generate_content(
            model="gemini-1.5-flash",
            contents=prompt,
            config={"response_mime_type": "application/json"},
        )
        
        data = json.loads(response.text)
        
        # 2. Force the structure to ensure all 6 keys exist
        keys = ["invoice_no", "date", "vendor", "amount", "tax", "currency"]
        final_output = {key: data.get(key) for key in keys}
        
        # 3. Clean the date if it exists
        if final_output['date']:
            try:
                final_output['date'] = dateutil.parser.parse(str(final_output['date'])).strftime("%Y-%m-%d")
            except:
                pass
        
        return final_output
        
    except Exception as e:
        # Return all keys as null instead of crashing
        return {key: None for key in ["invoice_no", "date", "vendor", "amount", "tax", "currency"]}