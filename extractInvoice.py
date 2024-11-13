import fitz  # PyMuPDF
from openai import OpenAI  # Updated import
import json
import os
from typing import Dict, Any

def extract_invoice_data(text: str) -> Dict[str, Any]:
    # Initialize the client
    client = OpenAI()
    
    # System prompt to structure the extraction
    system_prompt = """You are an invoice parsing assistant. Extract the following information from the invoice text into a JSON format:
    - invoice_number
    - date
    - total_amount
    - company_name (sender)
    - customer_name (recipient)
    - line_items (array of items with quantity, description, unit_price, and total)
    - payment_terms
    - due_date
    - tax_amount
    - subtotal
    
    If a field is not found, set it to null."""

    # Updated API call
    try:
        response = client.chat.completions.create(
            model="gpt-4-turbo-preview",  # Changed from invalid "gpt-40-mini" to correct model name
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Parse this invoice:\n\n{text}"}
            ],
            temperature=0.0,  # Keep it deterministic
            response_format={ "type": "json_object" }  # Force JSON response
        )
        
        # Return just the content from the response
        return response.choices[0].message.content
        
    except Exception as e:
        print(f"Error extracting invoice data: {e}")
        return {}

def main():
    # Load PDF
    pdf_path = "data/Invoice_1.pdf"
    doc = fitz.open(pdf_path)

    # Extract text from all pages and combine
    full_text = ""
    for page_number in range(doc.page_count):
        page = doc.load_page(page_number)
        full_text += page.get_text()

    # Extract structured data using LLM
    invoice_data = extract_invoice_data(full_text)

    # Print the extracted data
    print(json.dumps(invoice_data, indent=2))

    doc.close()

if __name__ == "__main__":
    main()