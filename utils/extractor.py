import os
import json
import dateutil.parser
from dotenv import load_dotenv
from google import genai

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def extract_invoice_info(text: str) -> dict:
    # 1. Ask the model for a strict JSON format
    prompt = f"""
    You are an invoice extraction API. Extract these fields from the text below.
    If a field is not found, you MUST return null.
    
    Fields:
    - invoice_no: string or null
    - date: string "YYYY-MM-DD" or null
    - vendor: string or null
    - amount: number or null (Subtotal before tax)
    - tax: number or null (Tax amount only)
    - currency: string or null
    
    Invoice Text:
    {text}
    """
    
    # Define the default structure
    empty_result = {
        "invoice_no": None, "date": None, "vendor": None, 
        "amount": None, "tax": None, "currency": None
    }
    
    try:
        response = client.models.generate_content(
            model="gemini-1.5-flash",
            contents=prompt,
            config={"response_mime_type": "application/json"},
        )
        
        # Parse JSON
        data = json.loads(response.text)
        
        # Build the final dictionary manually to guarantee all 6 keys exist
        final_output = {
            "invoice_no": data.get("invoice_no"),
            "date": data.get("date"),
            "vendor": data.get("vendor"),
            "amount": float(data["amount"]) if data.get("amount") is not None else None,
            "tax": float(data["tax"]) if data.get("tax") is not None else None,
            "currency": data.get("currency")
        }
        
        # Clean the date
        if final_output["date"]:
            try:
                final_output["date"] = dateutil.parser.parse(str(final_output["date"])).strftime("%Y-%m-%d")
            except:
                final_output["date"] = None
                    
        return final_output
        
    except Exception:
        # CRITICAL: Return the default structure instead of crashing with a 500
        return empty_result