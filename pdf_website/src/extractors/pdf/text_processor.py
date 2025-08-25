from pypdf import PdfReader

class TextProcessor:
    def __init__(self):
        self.chunk_size = 1024
        self.overlap_percentage = 20
    
    def input_and_extraction(self):
        """Input taking and text extraction with chunk overlap and metadata"""
        file_path = input("Enter file path (.pdf or .txt): ").strip()
        
        chunks_with_metadata = []
        if file_path.endswith('.pdf'):
            print(f"\nProcessing PDF: {file_path}")
            reader = PdfReader(file_path)
            page_texts = []
            for i, page in enumerate(reader.pages):
                page_text = page.extract_text()
                if page_text:
                    page_texts.append((page_text, i + 1))
            
            # Create chunks with page tracking
            for page_text, page_num in page_texts:
                page_chunks = self._create_chunks_with_metadata(page_text, f"Page {page_num}")
                chunks_with_metadata.extend(page_chunks)
                
        elif file_path.endswith('.txt'):
            print(f"\nProcessing text file: {file_path}")
            with open(file_path, 'r', encoding='utf-8') as f:
                full_text = f.read()
            chunks_with_metadata = self._create_chunks_with_metadata(full_text, "Text File")
        else:
            print("Unsupported file format")
            return []
        
        print(f"Created {len(chunks_with_metadata)} overlapping chunks with metadata")
        return chunks_with_metadata
    
    def _create_chunks_with_metadata(self, text, metadata):
        """Create overlapping chunks with metadata"""
        chunks = []
        overlap_size = int(self.chunk_size * self.overlap_percentage / 100)
        start = 0
        
        while start < len(text):
            end = start + self.chunk_size
            chunk = text[start:end].strip()
            
            if len(chunk) > 50:
                chunks.append((chunk, metadata))
            
            start = end - overlap_size
            if end >= len(text):
                break
        
        return chunks