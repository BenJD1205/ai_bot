# main.py
from dotenv import load_dotenv
import os
import json
import hashlib
from openai import OpenAI
from scraper import fetch_articles
from vector_store import get_or_create_vector_store, upload_file_to_store, delete_file_from_store

STATE_FILE = "data/state.json"
ARTICLES_DIR = "data/articles"

os.makedirs(ARTICLES_DIR, exist_ok=True)
os.makedirs("data", exist_ok=True)

def compute_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()

def load_state() -> dict:
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r") as f:
            return json.load(f)
    return {}

def save_state(state: dict):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)

def main():
    load_dotenv() # Nạp biến môi trường từ file .env
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("Missing OPENAI_API_KEY environment variable")

    client = OpenAI(api_key=api_key)
    vector_store_id = get_or_create_vector_store(client)
    print(f"Connected to Vector Store ID: {vector_store_id}")

    print("Fetching articles from Zendesk API...")
    articles = fetch_articles(limit=35)
    state = load_state()

    added_count = 0
    updated_count = 0
    skipped_count = 0

    for art in articles:
        art_id = art["id"]
        content_hash = compute_hash(art["markdown"])
        
        file_content = (
            f"---\n"
            f"id: {art_id}\n"
            f"title: \"{art['title']}\"\n"
            f"url: {art['url']}\n"
            f"Article URL: {art['url']}\n"
            f"---\n\n"
            f"# {art['title']}\n\n"
            f"{art['markdown']}\n"
        )
        file_path = os.path.join(ARTICLES_DIR, f"{art['slug']}.md")

        # Kiểm tra trạng thái Delta
        if art_id not in state:
            # 1. BÀI MỚI (ADDED)
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(file_content)
            
            file_id, status = upload_file_to_store(client, vector_store_id, file_path)
            state[art_id] = {
                "hash": content_hash,
                "file_id": file_id,
                "file_path": file_path,
                "updated_at": art["updated_at"]
            }
            added_count += 1
            print(f"[ADDED] {art['slug']} (File ID: {file_id}, Status: {status})")

        elif state[art_id]["hash"] != content_hash:
            # 2. BÀI CÓ THAY ĐỔI NỘI DUNG (UPDATED)
            delete_file_from_store(client, vector_store_id, state[art_id]["file_id"])
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(file_content)
                
            file_id, status = upload_file_to_store(client, vector_store_id, file_path)
            state[art_id].update({
                "hash": content_hash,
                "file_id": file_id,
                "updated_at": art["updated_at"]
            })
            updated_count += 1
            print(f"[UPDATED] {art['slug']} (Re-embedded)")

        else:
            # 3. KHÔNG THAY ĐỔI (SKIPPED)
            skipped_count += 1

    save_state(state)

    # Thống kê tổng hợp (Required Logs)
    store_details = client.beta.vector_stores.retrieve(vector_store_id)
    print("\n" + "="*40)
    print("JOB EXECUTION REPORT")
    print("="*40)
    print(f"Delta Stats   : Added: {added_count} | Updated: {updated_count} | Skipped: {skipped_count}")
    print(f"Remote Store  : Total files indexed: {store_details.file_counts.completed}")
    print("Execution completed successfully.")
    print("="*40)

if __name__ == "__main__":
    main()