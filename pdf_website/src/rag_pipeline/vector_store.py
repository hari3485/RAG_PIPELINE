from psycopg2.extras import execute_values

class VectorStore:
    def __init__(self, conn, cur):
        self.conn = conn
        self.cur = cur
    
    def store_in_pgvector(self, chunks_with_metadata, embeddings):
        """Store chunks, embeddings and metadata in PostgreSQL PGVector"""
        if not chunks_with_metadata or not embeddings:
            return False
        
        try:
            data_to_insert = [(chunk, embedding, metadata) for (chunk, metadata), embedding in zip(chunks_with_metadata, embeddings)]
            execute_values(
                self.cur,
                "INSERT INTO enhanced_documents (content, embedding, metadata) VALUES %s",
                data_to_insert
            )
            self.conn.commit()
            print(f"Successfully stored {self.cur.rowcount} documents with metadata in PGVector.")
            return True
        except Exception as e:
            print(f"Error storing in database: {e}")
            self.conn.rollback()
            return False