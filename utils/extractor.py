import os
import dateutil.parser # Ensure you run: pip install python-dateutil
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

def extract_invoice_info(text: str) -> InvoiceData:
    # 1. Instruct the model to convert dates to ISO 8601 (YYYY-MM-DD)
    prompt = f"""
    Extract the following fields from the invoice text. 
    Convert all dates into 'YYYY-MM-DD' format. 
    If a field is missing, return null.
    
    Invoice Text: {text}
    """
    
    response = client.models.generate_content(
        model="gemini-1.5-flash",
        contents=prompt,
        config={
            "response_mime_type": "application/json",
            "response_schema": InvoiceData,
        },
    )
    
    # 2. Parse and validate
    data = InvoiceData.model_validate_json(response.text)
    
    # 3. Fallback: If model failed to format the date correctly, parse it manually
    if data.date:
        try:
            data.date = dateutil.parser.parse(data.date).strftime("%Y-%m-%d")
        except:
            pass # Keep original if parsing fails
            
    return data