# Knowledge Base Sync Pipeline & AI Assistant

Automated ETL pipeline to ingest Zendesk Help Center articles, normalize to Markdown, sync delta changes to an OpenAI Vector Store, and power OptiBot.

## Architecture & Chunking Strategy
- **Extraction:** Ingests articles directly via Zendesk API, cleans HTML elements (`<script>`, `<nav>`, ads), and normalizes internal links.
- **Chunking Strategy:** Uses **Static Chunking** (`max_chunk_tokens: 800`, `chunk_overlap_tokens: 200`). This ensures code blocks and procedural instructions remain contiguous while providing sufficient semantic context across chunk boundaries.
- **Delta Detection:** Tracks content via `SHA-256` hashing in `data/state.json`. Unaltered articles are skipped; modified ones are deleted remotely and re-embedded.

## Local Setup & Run

1. Clone and install dependencies:
   ```bash
   cp .env.sample .env
   # Add your OPENAI_API_KEY in .env
   pip install -r requirements.txt