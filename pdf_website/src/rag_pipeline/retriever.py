import google.generativeai as genai
import os
from dotenv import load_dotenv

class Retriever:
    def __init__(self, conn, cur):
        load_dotenv()
        self.api_key = os.getenv('GOOGLE_API_KEY')
        genai.configure(api_key=self.api_key)
        self.embedding_model = "models/embedding-001"
        self.conn = conn
        self.cur = cur
    
    def retrieve_chunks(self, question):
        """Retrieve relevant chunks with metadata from database"""
        try:
            query_embedding_response = genai.embed_content(
                model=self.embedding_model,
                content=question,
                task_type="RETRIEVAL_QUERY"
            )
            query_embedding = query_embedding_response['embedding']
            
            self.cur.execute(
                "SELECT content, metadata, embedding <=> %s as distance FROM enhanced_documents ORDER BY embedding <=> %s LIMIT 5",
                (str(query_embedding), str(query_embedding))
            )
            results = self.cur.fetchall()
            
            if not results:
                return []
            
            # Use more lenient similarity threshold
            if results[0][2] > 1.5:
                return []
            
            # Return top 3 most relevant chunks for better context
            chunks_with_metadata = [(row[0], row[1]) for row in results[:3] if row[2] <= 1.5]
            
            # Display retrieved chunks for user
            for i, (chunk, metadata) in enumerate(chunks_with_metadata, 1):
                print(f"\nChunk {i} (Source: {metadata}): {chunk[:100]}...")
            
            return chunks_with_metadata
                
        except Exception as e:
            print(f"Error retrieving chunks: {e}")
            return []