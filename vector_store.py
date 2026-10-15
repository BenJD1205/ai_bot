# vector_store.py
import os
from openai import OpenAI

def get_or_create_vector_store(client: OpenAI, store_name: str = "OptiSigns Help Center"):
    # Tìm vector store đã có hoặc tạo mới
    stores = client.beta.vector_stores.list()
    for s in stores.data:
        if s.name == store_name:
            return s.id
            
    # Tạo mới với chiến lược chunking tĩnh rõ ràng
    vector_store = client.beta.vector_stores.create(
        name=store_name,
        chunking_strategy={
            "type": "static",
            "static": {
                "max_chunk_tokens": 800,
                "chunk_overlap_tokens": 200
            }
        }
    )
    return vector_store.id

def upload_file_to_store(client: OpenAI, vector_store_id: str, file_path: str):
    """Nạp từng file lên OpenAI Storage và đính kèm vào Vector Store"""
    with open(file_path, "rb") as f:
        file_obj = client.files.create(file=f, purpose="assistants")
    
    attached_file = client.beta.vector_stores.files.create_and_poll(
        vector_store_id=vector_store_id,
        file_id=file_obj.id
    )
    return file_obj.id, attached_file.status

def delete_file_from_store(client: OpenAI, vector_store_id: str, file_id: str):
    try:
        client.beta.vector_stores.files.delete(vector_store_id=vector_store_id, file_id=file_id)
        client.files.delete(file_id=file_id)
    except Exception as e:
        print(f"Warning: Failed to delete remote file {file_id}: {e}")