import psycopg2
import os
from dotenv import load_dotenv

class DatabaseSetup:
    def __init__(self):
        load_dotenv()
        db_password = os.getenv('DB_PASSWORD', '3485')
        self.db_connect_string = f"dbname=postgres user=postgres password={db_password} host=localhost port=5433"
        self.conn = None
        self.cur = None
        self.setup_database()
    
    def setup_database(self):
        """Setup database connection and table"""
        try:
            self.conn = psycopg2.connect(self.db_connect_string)
            self.cur = self.conn.cursor()
            print("Database connection successful.")
            
            self.cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")
            # Drop and recreate table to ensure metadata column exists
            self.cur.execute("DROP TABLE IF EXISTS enhanced_documents;")
            self.cur.execute("""
                CREATE TABLE enhanced_documents (
                    id SERIAL PRIMARY KEY,
                    content TEXT,
                    embedding VECTOR(768),
                    metadata TEXT
                );
            """)
            self.conn.commit()
            print("'enhanced_documents' table created with metadata support.")
        except Exception as e:
            print(f"Database setup error: {e}")
            exit()
    
    def get_connection(self):
        return self.conn, self.cur
    
    def close_connection(self):
        """Close database connection"""
        if self.cur:
            self.cur.close()
        if self.conn:
            self.conn.close()
        print("Database connection closed.")