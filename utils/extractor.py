import os
import dateutil.parser
from dotenv import load_dotenv
from google import genai
from pydantic import BaseModel

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

class InvoiceData(BaseModel):
    invoice_no: str | None = None
    date: str | None = None
    vendor: str | None = None
    amount: float | None = None
    tax: float | None = None
    currency: str | None = None

def extract_invoice_info(text: str) -> dict:
    prompt = f"""
    Extract the following fields from the invoice text.
    Return ONLY valid JSON.
    - invoice_no: string
    - date: string in YYYY-MM-DD format
    - vendor: string
    - amount: number (subtotal)
    - tax: number
    - currency: string (e.g., INR, USD)
    
    If information is missing, use null.
    
    Invoice Text:
    {text}
    """
    
    response = client.models.generate_content(
        model="gemini-1.5-flash",
        contents=prompt,
        config={"response_mime_type": "application/json"},
    )
    
    # Use model_validate_json but catch errors to return a clean dictionary
    try:
        # Load the LLM response
        data_obj = InvoiceData.model_validate_json(response.text)
        data = data_obj.model_dump()
        
        # Final cleanup for the date
        if data.get('date'):
            try:
                data['date'] = dateutil.parser.parse(data['date']).strftime("%Y-%m-%d")
            except:
                pass
        return data
    except Exception as e:
        # If all else fails, return the raw parsed JSON to prevent a 500 error
        import json
        return json.loads(response.text)