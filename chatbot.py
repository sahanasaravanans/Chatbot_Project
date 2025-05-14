import csv
import logging
import re
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer

# Load Sentence-BERT model
bert_model = SentenceTransformer('all-MiniLM-L6-v2')

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# === Load Q&A dataset from CSV ===
def get_chatbot_data():
    chatbot_data = []
    try:
        with open('chatbot_data.csv', mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                if 'query' in row and 'response' in row:
                    chatbot_data.append({
                        "query": row["query"].strip(),
                        "response": row["response"].strip()
                    })
                else:
                    logger.warning(f"Skipped malformed row: {row}")
    except Exception as e:
        logger.error(f"Error reading chatbot_data.csv: {e}")
    return chatbot_data

# === Clean user input text ===
def clean_text(text):
    if not text:
        return ""
    text = text.lower()
    text = re.sub(r'[^\w\s]', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    filler_words = {
        'a', 'an', 'the', 'is', 'are', 'was', 'were', 'be', 'been', 'am',
        'can', 'could', 'do', 'does', 'did', 'has', 'have', 'had', 'will',
        'would', 'should', 'i', 'you', 'we', 'they', 'it', 'and', 'or', 'but',
        'if', 'then', 'that', 'this', 'these', 'those', 'to', 'for', 'in',
        'on', 'at', 'by', 'with', 'about', 'as', 'into', 'like', 'through', 'after'
    }
    words = [word for word in text.split() if word not in filler_words]
    return ' '.join(words)

# === Try direct string match first ===
def direct_match(query, entries):
    query_clean = clean_text(query)
    for entry in entries:
        if query_clean == clean_text(entry['query']):
            logger.debug(f"Direct match found: {entry['query']}")
            return entry
    return None

# === Use BERT semantic similarity if no exact match ===
def bert_match(query, entries):
    try:
        if not entries or not query.strip():
            return None
        queries = [entry['query'] for entry in entries if entry['query'].strip()]
        if not queries:
            return None
        embeddings = bert_model.encode([query] + queries)
        query_vec = embeddings[0]
        entry_vecs = embeddings[1:]
        scores = cosine_similarity([query_vec], entry_vecs).flatten()
        best_idx = np.argmax(scores)
        best_score = scores[best_idx]
        logger.info(f"BERT match score: {best_score:.4f}")
        if best_score >= 0.6:
            return entries[best_idx]
    except Exception as e:
        logger.error(f"BERT matching failed: {e}")
    return None

# === Special fallback responses ===
def handle_special_queries(query):
    query_lower = clean_text(query)
    if any(word in query_lower for word in ['event', 'events', 'upcoming', 'calendar', 'schedule']):
        return {"text": "Here are the upcoming events:\n• Alumni Meetup - June 10, 2025 at New York\n• Career Fair - July 22, 2025 (Online)"}
    if any(word in query_lower for word in ['help', 'assist', 'support', 'guidance']):
        return {"text": (
            "I can help you with:\n"
            "• Alumni benefits and services\n"
            "• Upcoming events\n"
            "• Updating your profile\n"
            "• Getting involved\n\n"
            "What would you like to ask about?"
        )}
    if any(word in query_lower.split() for word in ['hi', 'hello', 'hey', 'greetings']):
        return {"text": "Hello! I'm the Alumni Assistant. How can I help you today?"}
    return None

# === Core bot function ===
def get_bot_response(query):
    try:
        logger.info(f"Processing query: '{query}'")
        if not query or not query.strip():
            return {"text": "Please ask a question so I can help you."}

        chatbot_data = get_chatbot_data()
        if not chatbot_data:
            return {"text": "I'm sorry, I don't have any information right now."}

        # Try direct match, then BERT match
        match = direct_match(query, chatbot_data)
        if not match:
            match = bert_match(query, chatbot_data)

        # If match found
        if match:
            response = match['response']
            if response.lower().startswith("http") and response.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp')):
                return {"image_url": response}
            else:
                return {"text": response}

        # If special fallback applies
        special = handle_special_queries(query)
        if special:
            return special

        # No match found
        return {"text": "I couldn't find a specific answer. Try asking about events, benefits, or how to contact us."}

    except Exception as e:
        logger.error(f"Chatbot error on query '{query}': {e}", exc_info=True)
        return {"text": "Something went wrong. Please try again later."}

# === Optional CLI Tester ===
if __name__ == "__main__":
    while True:
        user_input = input("\nAsk a question (or type 'exit'): ")
        if user_input.lower() == 'exit':
            break
        response = get_bot_response(user_input)
        if 'image_url' in response:
            print("Bot: [Image]", response["image_url"])
        else:
            print("Bot:", response["text"])
