from flask import Flask, render_template, request, jsonify
import google.generativeai as genai
import json
import re
import os
import random

app = Flask(__name__)

# --- Google Gemini API Configuration ---
GOOGLE_API_KEY = "AIzaSyAfdSjyViGbtyktFAyRudfkNyW-rLFbpoI"  # Your actual API key
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel("models/gemini-2.5-flash")

# --- Intents System ---
def load_intents(file_path="test\intents.json"):
    """Load intents from JSON file"""
    try:
        print("Current working directory:", os.getcwd())
        print("Looking for intents file at:", os.path.abspath(file_path))
        
        with open(file_path, 'r', encoding='utf-8') as f:
            intents = json.load(f)
        
        print(f"✅ Successfully loaded {len(intents.get('intents', []))} intents from {file_path}")
        
        # Print all loaded intents for verification
        if "intents" in intents:
            for i, intent in enumerate(intents["intents"]):
                print(f"  Intent {i+1}: '{intent.get('tag', 'No tag')}'")
                print(f"    Patterns: {intent.get('patterns', [])}")
                print(f"    Responses: {intent.get('responses', [])}")
                print()
        
        return intents
    except FileNotFoundError:
        print(f"❌ Error: {file_path} not found in {os.getcwd()}")
        print("Please make sure intents.json exists in the same directory as app.py")
        return {"intents": []}
    except json.JSONDecodeError as e:
        print(f"❌ Error decoding JSON from {file_path}: {e}")
        return {"intents": []}
    except Exception as e:
        print(f"❌ Error loading intents: {e}")
        return {"intents": []}

def get_intent_response(user_input, intents):
    """Get response from intents based on user input"""
    user_input = user_input.lower()
    print(f"🔍 Searching intents for: '{user_input}'")
    
    for intent in intents["intents"]:
        for pattern in intent["patterns"]:
            if pattern.lower() in user_input:
                response = random.choice(intent["responses"])
                print(f"✅ Intent matched: '{intent['tag']}' -> '{response}'")
                return response
    
    print("❌ No intent match found")
    return None

# Load intents at startup
intents_data = load_intents()

def query_google_gemini(prompt):
    """Query Gemini API for responses"""
    try:
        print(f"🤖 Sending to Gemini API: '{prompt}'")
        response = model.generate_content(prompt)
        result = response.text.strip() if response and response.text else "I'm not sure how to respond."
        print(f"✅ Gemini response: '{result}'")
        return result
    except Exception as e:
        error_msg = f"API error: {str(e)}"
        print(f"❌ Gemini API error: {error_msg}")
        return error_msg

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/ask', methods=['POST'])
def ask():
    user_message = request.json.get('message', '')
    print(f"📨 Received message: '{user_message}'")
    
    # First, try to get response from intents
    intent_response = get_intent_response(user_message, intents_data)
    
    if intent_response:
        # Use intent response
        print("🎯 Using intent response")
        return jsonify({
            'reply': intent_response,
            'source': 'intent'
        })
    else:
        # Fall back to Gemini API
        print("🚀 Falling back to Gemini API")
        response = query_google_gemini(user_message)
        return jsonify({
            'reply': response,
            'source': 'gemini'
        })

@app.route('/intents')
def show_intents():
    """Debug endpoint to show loaded intents"""
    return jsonify({
        'loaded_intents_count': len(intents_data.get("intents", [])),
        'intents': intents_data.get("intents", [])
    })

# --- Command Line Chat Interface (optional) ---
def command_line_chat():
    """Command line version of the chatbot"""
    print("Hello! I am your chatbot. Type 'exit' to end the conversation.")
    
    while True:
        user_input = input("You: ")
        
        if user_input.lower() == 'exit':
            print("Goodbye! See you later.")
            break
        
        # Try intents first
        intent_response = get_intent_response(user_input, intents_data)
        
        if intent_response:
            print("Bot (Intent):", intent_response)
        else:
            # Fall back to Gemini
            gemini_response = query_google_gemini(user_input)
            print("Bot (Gemini):", gemini_response)

if __name__ == '__main__':
    # Check if we're running in command line mode or web mode
    if len(os.sys.argv) > 1 and os.sys.argv[1] == '--cli':
        command_line_chat()
    else:
        print("🚀 Starting Flask web server...")
        print(f"📊 Loaded {len(intents_data.get('intents', []))} intents")
        print("📋 Available intents:", [intent['tag'] for intent in intents_data.get('intents', [])])
        print("🌐 Server running at: http://127.0.0.1:5000")
        print("🔍 Debug intents at: http://127.0.0.1:5000/intents")
        app.run(debug=True)
