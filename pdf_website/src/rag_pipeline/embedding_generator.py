import google.generativeai as genai
import os
from dotenv import load_dotenv

class EmbeddingGenerator:
    def __init__(self):
        load_dotenv()
        self.api_key = os.getenv('GOOGLE_API_KEY')
        genai.configure(api_key=self.api_key)
        self.embedding_model = "models/embedding-001"
    
    def generate_embeddings(self, chunks):
        """Generate embeddings for chunks"""
        if not chunks:
            return []
        
        try:
            print("Generating embeddings...")
            response = genai.embed_content(
                model=self.embedding_model,
                content=chunks,
                task_type="RETRIEVAL_DOCUMENT"
            )
            embeddings = response['embedding']
            print(f"Generated {len(embeddings)} embeddings.")
            return embeddings
        except Exception as e:
            print(f"Error generating embeddings: {e}")
            return []