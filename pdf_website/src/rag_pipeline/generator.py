from flotorch_core.inferencer.gateway_inferencer import GatewayInferencer
from dotenv import load_dotenv
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from config.prompts import prompts
import os

load_dotenv()

class Generator:
    def __init__(self):
        pass
    
    def generate_response(self, question, retrieved_chunks_with_metadata):
        """Generate response using LLM with chunks and include source metadata"""
        if not retrieved_chunks_with_metadata:
            return "I don't know."
        
        try:
            # Extract chunks and metadata
            chunks = [chunk for chunk, metadata in retrieved_chunks_with_metadata]
            metadata_list = [metadata for chunk, metadata in retrieved_chunks_with_metadata]
            
            # Join all retrieved chunks into a single string
            joined_context = " ".join(chunks)
            context = [{'text': joined_context}]
            
            # System prompt guide object
            n_shot_prompt_guide = {
                "system_prompt": (
                    "You are a helpful assistant that answers questions based strictly on the provided context. "
                    "Provide clear, accurate answers in 2-3 sentences. "
                    "If the context doesn't contain relevant information, respond with 'I don't know.' "
                    "Do not use external knowledge beyond the given context."
                )
            }
            
            print(f"Generating response for: {question}")
            print(f"Using {len(chunks)} chunks from sources: {set(metadata_list)}")
            
            # Initialize GatewayInferencer with only required parameters
            inferencer = GatewayInferencer(
                model_id="bedrock/us.amazon.nova-lite-v1:0",
                api_key=os.getenv("API_KEY"),
                base_url=os.getenv("BASE_URL"),
                n_shot_prompt_guide_obj=n_shot_prompt_guide,
                n_shot_prompts=2
            )
            
            # Generate text with joined context string
            metadata, answer = inferencer.generate_text(question, context)
            
            # Check if response is HTML (API error) or empty
            if not answer or answer.strip().startswith('<!DOCTYPE') or len(answer.strip()) < 5:
                print("Using fallback response generation")
                return self._generate_fallback_answer(question, joined_context, metadata_list)
            
            # Add source information to answer
            sources = ", ".join(set(metadata_list))
            clean_answer = answer.strip()
            final_answer = f"{clean_answer}\n\nSource: {sources}"
            
            return final_answer
            
        except Exception as e:
            print(f"Generation error: {str(e)}")
            chunks = [chunk for chunk, metadata in retrieved_chunks_with_metadata]
            metadata_list = [metadata for chunk, metadata in retrieved_chunks_with_metadata]
            return self._fallback_response_with_metadata(question, " ".join(chunks), metadata_list)
    
    def _generate_fallback_answer(self, question, context, metadata_list):
        """Generate fallback answer using context analysis"""
        # Simple keyword-based response generation
        question_lower = question.lower()
        context_lower = context.lower()
        
        # Find relevant sentences
        sentences = context.split('.')
        relevant_sentences = []
        
        # Look for sentences containing question keywords
        question_words = [word for word in question_lower.split() if len(word) > 3]
        
        for sentence in sentences:
            sentence_lower = sentence.lower()
            if any(word in sentence_lower for word in question_words):
                relevant_sentences.append(sentence.strip())
        
        if relevant_sentences:
            answer = '. '.join(relevant_sentences[:2]) + '.'
        else:
            # Extract first meaningful sentence from context
            meaningful_sentences = [s.strip() for s in sentences if len(s.strip()) > 50]
            answer = meaningful_sentences[0] + '.' if meaningful_sentences else "Information found in the provided context."
        
        sources = ", ".join(set(metadata_list))
        return f"{answer}\n\nSource: {sources}"