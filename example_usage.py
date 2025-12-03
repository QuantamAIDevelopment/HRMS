"""
Example usage of Compliance Documents API

This demonstrates how to:
1. Upload a document (HR Manager/Executive only)
2. List all documents (All users)
3. Download a document (All users)
4. Update a document (HR Manager/Executive only)
5. Delete a document (HR Manager/Executive only)
"""

import requests
import base64

BASE_URL = "http://localhost:8000/api/v1/compliance"

# Example: Encode a file to base64
def encode_file(file_path: str) -> str:
    with open(file_path, 'rb') as f:
        return base64.b64encode(f.read()).decode('utf-8')

# 1. Upload Document (HR Manager/Executive only)
def upload_document():
    # Encode your file
    # base64_content = encode_file("path/to/your/document.pdf")
    base64_content = "SGVsbG8gV29ybGQh"  # Example: "Hello World!" in base64
    
    payload = {
        "title": "Employee Code of Conduct",
        "category": "Policy",
        "description": "Company-wide code of conduct policy",
        "uploaded_document": base64_content
    }
    
    response = requests.post(f"{BASE_URL}/documents", json=payload)
    print("Upload Response:", response.json())
    return response.json()

# 2. List All Documents (All users)
def list_documents(category=None):
    params = {}
    if category:
        params['category'] = category
    
    response = requests.get(f"{BASE_URL}/documents", params=params)
    print("Documents List:", response.json())
    return response.json()

# 3. Download Document (All users)
def download_document(document_id: int):
    response = requests.get(f"{BASE_URL}/documents/{document_id}")
    document = response.json()
    
    # Decode and save file
    base64_content = document['uploaded_document']
    file_data = base64.b64decode(base64_content)
    
    with open(f"downloaded_{document['title']}.pdf", 'wb') as f:
        f.write(file_data)
    
    print(f"Document downloaded: {document['title']}")
    return document

# 4. Update Document (HR Manager/Executive only)
def update_document(document_id: int):
    payload = {
        "title": "Updated Employee Code of Conduct",
        "description": "Updated policy for 2024"
    }
    
    response = requests.put(f"{BASE_URL}/documents/{document_id}", json=payload)
    print("Update Response:", response.json())
    return response.json()

# 5. Delete Document (HR Manager/Executive only)
def delete_document(document_id: int):
    response = requests.delete(f"{BASE_URL}/documents/{document_id}")
    print(f"Delete Status Code: {response.status_code}")

if __name__ == "__main__":
    # Example workflow
    print("=== Compliance Documents API Example ===\n")
    
    # Upload
    doc = upload_document()
    doc_id = doc['document_id']
    
    # List
    list_documents()
    
    # Download
    download_document(doc_id)
    
    # Update
    update_document(doc_id)
    
    # Delete
    delete_document(doc_id)
