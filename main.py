from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from utils.extractor import extract_invoice_info

app = FastAPI()

# Enable CORS for the Cloudflare Worker
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class InvoiceRequest(BaseModel):
    invoice_text: str

@app.post("/extract")
async def extract(request: InvoiceRequest):
    try:
        data = extract_invoice_info(request.invoice_text)
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))