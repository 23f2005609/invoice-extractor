import os
import json
import dateutil.parser
from dotenv import load_dotenv
from google import genai
from pydantic import BaseModel

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# Define a strict model to force the LLM to think about these specific fields
class InvoiceSchema(BaseModel):
    invoice_no: str | None
    date: str | None
    vendor: str | None
    amount: float | None
    tax: float | None
    currency: str | None

def extract_invoice_info(text: str) -> dict:
    prompt = f"""
    You are an expert invoice parser. Extract the following fields from the text.
    If a field exists, extract it exactly. If it is absolutely not in the text, use null.
    
    Required fields:
    - invoice_no: Look for "Invoice No:", "Invoice #:", or similar.
    - date: Convert to YYYY-MM-DD.
    - vendor: The company name.
    - amount: The subtotal amount (number only).
    - tax: The tax amount (number only).
    - currency: The currency code (e.g., INR, USD).
    
    Invoice Text:
    {text}
    """
    
    response = client.models.generate_content(
        model="gemini-1.5-flash",
        contents=prompt,
        config={"response_mime_type": "application/json"},
    )
    
    try:
        data = json.loads(response.text)
        
        # Clean up date format if it exists
        if data.get('date'):
            try:
                data['date'] = dateutil.parser.parse(str(data['date'])).strftime("%Y-%m-%d")
            except:
                pass
        
        # Return the dictionary directly
        return data
    except:
        # Fallback to empty structure
        return {"invoice_no": None, "date": None, "vendor": None, "amount": None, "tax": None, "currency": None}