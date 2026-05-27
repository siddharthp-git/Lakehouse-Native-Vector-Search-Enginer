import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from deltalake import DeltaTable
import whisper
import os

# Add base directory to path to import config
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from config import FAISS_INDEX_PATH, DELTA_TABLE_PATH, EMBEDDING_MODEL

class SearchService:
    def __init__(self):
        print("Initializing Search Service...")
        self.model = SentenceTransformer(EMBEDDING_MODEL)
        self.faiss_index = faiss.read_index(FAISS_INDEX_PATH)
        self.delta_table = DeltaTable(DELTA_TABLE_PATH)
        self.whisper_model = whisper.load_model("base")
        print("Search Service initialized.")

    def text_to_embedding(self, text: str):
        return self.model.encode([text])

    def vector_search(self, query_text: str, k: int = 5):
        query_embedding = self.text_to_embedding(query_text)
        distances, ids = self.faiss_index.search(query_embedding, k)
        
        if len(ids[0]) == 0:
            return []

        # Get metadata from Delta Lake
        results_df = self.delta_table.to_pandas(filters=[("id", "in", ids[0].tolist())])
        
        # Create a dictionary for quick lookups
        results_map = {row['id']: row for row in results_df.to_dict('records')}
        
        # Order results based on FAISS output
        ordered_results = [results_map[id] for id in ids[0] if id in results_map]
        return ordered_results

    def hybrid_search(self, query_text: str, category_filter: str, k: int = 5):
        # 1. Filter metadata from Delta Lake
        filtered_df = self.delta_table.to_pandas(filters=[("category", "==", category_filter)])
        
        if filtered_df.empty:
            return []
            
        filtered_ids = filtered_df['id'].values
        
        # This is a simple (but potentially slow) way to filter the index.
        # For large datasets, you'd reconstruct a temporary index or use more advanced FAISS features.
        # Here we remove all vectors *not* in our filtered list.
        ids_to_remove = [i for i in range(self.faiss_index.ntotal) if self.faiss_index.id_map.at(i) not in filtered_ids]
        
        temp_index = faiss.clone_index(self.faiss_index)
        temp_index.remove_ids(np.array(ids_to_remove, dtype=np.int64))
        
        # 2. Perform vector search on the filtered subset
        query_embedding = self.text_to_embedding(query_text)
        distances, ids = temp_index.search(query_embedding, k)
        
        if len(ids[0]) == 0:
            return []

        results_df = self.delta_table.to_pandas(filters=[("id", "in", ids[0].tolist())])
        results_map = {row['id']: row for row in results_df.to_dict('records')}
        ordered_results = [results_map[id] for id in ids[0] if id in results_map]

        return ordered_results

    def transcribe_audio(self, audio_path: str):
        result = self.whisper_model.transcribe(audio_path)
        return result['text']