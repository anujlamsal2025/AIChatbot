from flask import Flask, render_template, request, jsonify
import google.generativeai as genai
import json, re, os, random

app = Flask(__name__)

# --- Configuration ---
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "AIzaSyAfdSjyViGbtyktFAyRudfkNyW-rLFbpoI")
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel("models/gemini-2.5-flash")

# --- Intents Loading ---
def load_intents(file_path="test\intents.json"):
    """Load chatbot intents from a JSON file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        print(f"✅ Loaded {len(data.get('intents', []))} intents.")
        return data
    except Exception as e:
        print(f"❌ Failed to load intents: {e}")
        return {"intents": []}

intents_data = load_intents()

# --- Intent Matching ---
def get_intent_response(user_input, intents):
    """Return a predefined response if user input matches an intent pattern."""
    user_input = user_input.lower()
    for intent in intents.get("intents", []):
        for pattern in intent.get("patterns", []):
            if pattern.lower() in user_input:
                return random.choice(intent["responses"])
    return None

# --- Response Formatter ---
def format_response(text):
    """Apply HTML formatting for chatbot responses."""
    if not text:
        return ""
    
    text = text.strip()
    text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', text)
    text = re.sub(r'\*(.*?)\*', r'<em>\1</em>', text)
    text = re.sub(r'`(.*?)`', r'<code>\1</code>', text)
    text = re.sub(r'(\d+)\.\s', r'<br>\1. ', text)
    text = re.sub(r'[\-\•]\s', r'<br>• ', text)
    text = text.replace('\n\n', '<br><br>').replace('\n', '<br>')
    return text

# --- Gemini Query ---
def query_google_gemini(prompt):
    """Send a query to Gemini API and return formatted response."""
    try:
        formatted_prompt = (
            f"Answer the following clearly and concisely using bullet points if needed:\n\n{prompt}"
        )
        response = model.generate_content(formatted_prompt)
        text = response.text.strip() if response and response.text else "I'm not sure how to respond."
        return format_response(text)
    except Exception as e:
        return format_response(f"API error: {e}")

# --- Flask Routes ---
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/ask', methods=['POST'])
def ask():
    user_message = request.json.get('message', '').strip()
    if not user_message:
        return jsonify({'reply': "Please enter a message.", 'source': 'system'})
    
    intent_reply = get_intent_response(user_message, intents_data)
    if intent_reply:
        return jsonify({'reply': format_response(intent_reply), 'source': 'intent'})
    
    gemini_reply = query_google_gemini(user_message)
    return jsonify({'reply': gemini_reply, 'source': 'gemini'})

@app.route('/intents')
def show_intents():
    """Debug endpoint to show loaded intents."""
    return jsonify({
        'count': len(intents_data.get("intents", [])),
        'intents': intents_data.get("intents", [])
    })

# --- CLI Mode ---
def command_line_chat():
    """Run chatbot in command-line mode."""
    print("🤖 Chatbot ready. Type 'exit' to quit.")
    while True:
        user_input = input("You: ").strip()
        if user_input.lower() == 'exit':
            print("Goodbye 👋")
            break
        reply = get_intent_response(user_input, intents_data) or query_google_gemini(user_input)
        print("Bot:", reply)

# --- Run Mode ---
if __name__ == '__main__':
    if len(os.sys.argv) > 1 and os.sys.argv[1] == '--cli':
        command_line_chat()
    else:
        print(f"🚀 Server running at: http://127.0.0.1:5000")
        app.run(debug=True)
