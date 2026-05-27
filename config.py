import os

# Base directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Data paths
DATA_DIR = os.path.join(BASE_DIR, 'data')
RAW_DATA_PATH = os.path.join(DATA_DIR, 'raw', 'sample_data.csv')
PROCESSED_DATA_DIR = os.path.join(DATA_DIR, 'processed')

# FAISS and Delta Lake paths
FAISS_INDEX_PATH = os.path.join(PROCESSED_DATA_DIR, 'vector_index.faiss')
DELTA_TABLE_PATH = os.path.join(PROCESSED_DATA_DIR, 'metadata.delta')

# Model for embeddings
EMBEDDING_MODEL = 'all-MiniLM-L6-v2'