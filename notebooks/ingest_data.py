import pandas as pd
import faiss
from sentence_transformers import SentenceTransformer
from deltalake.writer import write_deltalake
import os
import sys

# Add base directory to path to import config
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config import RAW_DATA_PATH, FAISS_INDEX_PATH, DELTA_TABLE_PATH, EMBEDDING_MODEL, PROCESSED_DATA_DIR

def create_index_and_metadata():
    """
    Reads raw data, generates embeddings, creates a FAISS index,
    and stores metadata in a Delta Lake table.
    """
    print("Starting data ingestion and indexing...")

    # Ensure processed data directory exists
    os.makedirs(PROCESSED_DATA_DIR, exist_ok=True)

    # 1. Load data
    try:
        df = pd.read_csv(RAW_DATA_PATH)
        print(f"Loaded {len(df)} records from {RAW_DATA_PATH}")
    except FileNotFoundError:
        print(f"Error: Raw data file not found at {RAW_DATA_PATH}")
        return

    # 2. Generate embeddings
    print(f"Loading sentence transformer model: {EMBEDDING_MODEL}")
    model = SentenceTransformer(EMBEDDING_MODEL)
    embeddings = model.encode(df['text'].tolist(), show_progress_bar=True)
    
    # Get embedding dimension
    d = embeddings.shape[1]
    print(f"Embeddings generated with dimension: {d}")

    # 3. Build FAISS index
    print("Building FAISS index...")
    index = faiss.IndexFlatL2(d)
    index = faiss.IndexIDMap(index) # Map vectors to original IDs
    index.add_with_ids(embeddings, df['id'].values)
    
    print(f"FAISS index built with {index.ntotal} vectors.")

    # 4. Save FAISS index
    faiss.write_index(index, FAISS_INDEX_PATH)
    print(f"FAISS index saved to {FAISS_INDEX_PATH}")

    # 5. Save metadata to Delta Lake
    print("Saving metadata to Delta Lake...")
    # We only need metadata, not the full text for faster filtering
    metadata_df = df[['id', 'category', 'text']] 
    write_deltalake(DELTA_TABLE_PATH, metadata_df, mode='overwrite')
    print(f"Metadata saved to Delta table at {DELTA_TABLE_PATH}")
    
    print("\nIngestion and indexing complete.")

if __name__ == "__main__":
    create_index_and_metadata()