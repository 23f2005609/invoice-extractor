import os
from dotenv import load_dotenv
from google import genai
from pydantic import BaseModel

# 1. Load the .env file explicitly
load_dotenv()

# 2. Get the key and validate it
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("GEMINI_API_KEY is missing! Make sure your .env file is in the same directory as main.py")

# 3. Initialize the client
client = genai.Client(api_key=api_key)

class InvoiceData(BaseModel):
    invoice_no: str | None = None
    date: str | None = None
    vendor: str | None = None
    amount: float | None = None
    tax: float | None = None
    currency: str | None = None

def extract_invoice_info(text: str) -> InvoiceData:
    response = client.models.generate_content(
        model="gemini-3.5-flash",
        contents=f"Extract the following invoice details. IMPORTANT: You must convert all dates to 'YYYY-MM-DD' format. Input text: {text}",
        config={
            "response_mime_type": "application/json",
            "response_schema": InvoiceData,
        },
    )
    # The SDK will now force the model to adhere to the schema
    return InvoiceData.model_validate_json(response.text)