import logging
from chatbot import get_bot_response
from sentence_transformers import SentenceTransformer, util
from fuzzywuzzy import fuzz
# from rapidfuzz import fuzz  # Use this instead if you installed rapidfuzz
import re

# Load BERT model for semantic similarity
model = SentenceTransformer('all-MiniLM-L6-v2')

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Test data
test_cases = [
    {
        "input": "hello",
        "expected": "Hello! I'm the Alumni Assistant. How can I help you today?"
    },
    {
        "input": "What are the upcoming events",
        "expected": (
            "Here are the upcoming events:\n"
            "• Alumni Meetup - June 10, 2025 at New York\n"
            "• Career Fair - July 22, 2025 at Online"
        )
    },
    {
        "input": "How do I change my email ID in my alumni profile?",
        "expected": (
             "Email the support team"
    "Send an email to support@srecalumni.org.in to change your ID"
    "Please contact our support to update your alumni profile email."
    "Email the support team at support@srecalumni.org.in with your request."
        )
    },
    {
        "input": "Can you help me?",
        "expected": (
            "I can help you with:\n"
            "• Alumni benefits and services\n"
            "• Upcoming events\n"
            "• Updating your profile\n"
            "• Getting involved\n\n"
            "What would you like to ask about?"
        )
    },
    {
        "input": "Can I donate to the alumni fund?",
        "expected": (
            "Yes, donations can be made through the 'Donate Now' section on the alumni website. "
        )
    }
]

# Normalize text for fuzzy match
def normalize(text):
    if not text:
        return ""
    text = text.lower()
    text = text.replace('\n', ' ')
    text = re.sub(r'[^\w\s]', '', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

# Main test function
def run_tests():
    logger.info("Running fuzzy + BERT chatbot response accuracy test...\n")
    total = len(test_cases)
    correct = 0

    for i, case in enumerate(test_cases, 1):
        input_query = case["input"]
        expected = case["expected"]
        predicted = get_bot_response(input_query).get("text", "")

        # Normalize for fuzzy match
        norm_pred = normalize(predicted)
        norm_exp = normalize(expected)

        # Fuzzy match score
        fuzzy_score = fuzz.ratio(norm_pred, norm_exp)

        # Semantic similarity
        emb_pred = model.encode(predicted, convert_to_tensor=True)
        emb_exp = model.encode(expected, convert_to_tensor=True)
        semantic_score = util.cos_sim(emb_pred, emb_exp).item()

        # Pass if either fuzzy or semantic scores exceed threshold
        passed = fuzzy_score >= 85 or semantic_score >= 0.85
        if passed:
            correct += 1

        print(f"{'✅' if passed else '❌'} Test {i}:")
        print(f"   Input:            {input_query}")
        print(f"   Predicted:        {predicted}")
        print(f"   Expected:         {expected}")
        print(f"   Fuzzy Score:      {fuzzy_score:.1f}")
        print(f"   Semantic Score:   {semantic_score:.4f}\n")

    accuracy = correct / total * 100
    print(f"📊 Combined Response Accuracy: {accuracy:.2f}%")

# Run script
if __name__ == "__main__":
    run_tests()
