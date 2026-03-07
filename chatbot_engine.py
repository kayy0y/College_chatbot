import nltk
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import re

# Download required NLTK data (run once)
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')
    nltk.download('stopwords')

from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

class ChatbotEngine:
    def __init__(self, faqs):
        """
        Initialize the chatbot engine
        faqs: list of tuples (question, answer, category)
        """
        self.questions = [faq[0] for faq in faqs]
        self.answers = [faq[1] for faq in faqs]
        self.categories = [faq[2] for faq in faqs]
        
        # Initialize TF-IDF Vectorizer
        self.vectorizer = TfidfVectorizer(
            lowercase=True,
            stop_words='english',
            ngram_range=(1, 2)  # Use both unigrams and bigrams
        )
        
        # Fit vectorizer on all questions
        self.question_vectors = self.vectorizer.fit_transform(self.questions)
        
        # Confidence threshold
        self.CONFIDENCE_THRESHOLD = 0.3
        
    def preprocess_text(self, text):
        """Clean and preprocess user input"""
        # Convert to lowercase
        text = text.lower()
        # Remove special characters
        text = re.sub(r'[^a-z0-9\s]', '', text)
        # Remove extra spaces
        text = ' '.join(text.split())
        return text
    
    def get_response(self, user_query):
        """
        Get response for user query
        Returns: (answer, confidence, matched_question)
        """
        # Preprocess query
        processed_query = self.preprocess_text(user_query)
        
        # Transform query to TF-IDF vector
        query_vector = self.vectorizer.transform([processed_query])
        
        # Calculate cosine similarity with all questions
        similarities = cosine_similarity(query_vector, self.question_vectors)[0]
        
        # Get best match
        best_match_idx = similarities.argmax()
        confidence = similarities[best_match_idx]
        
        # Check if confidence is above threshold
        if confidence >= self.CONFIDENCE_THRESHOLD:
            return {
                'answer': self.answers[best_match_idx],
                'confidence': float(confidence),
                'matched_question': self.questions[best_match_idx],
                'category': self.categories[best_match_idx],
                'success': True
            }
        else:
            return {
                'answer': "I'm not sure about that. Please contact our admission office at admissions@college.edu or call +91-9876543210 for more information.",
                'confidence': float(confidence),
                'matched_question': None,
                'category': 'unmatched',
                'success': False
            }

# Test the engine
if __name__ == '__main__':
    from database import get_all_faqs
    
    faqs = get_all_faqs()
    engine = ChatbotEngine(faqs)
    
    # Test queries
    test_queries = [
        "What is the fee for btech?",
        "Tell me about hostel",
        "How to apply?",
        "Random gibberish query"
    ]
    
    for query in test_queries:
        result = engine.get_response(query)
        print(f"\nQuery: {query}")
        print(f"Confidence: {result['confidence']:.2f}")
        print(f"Answer: {result['answer'][:100]}...")