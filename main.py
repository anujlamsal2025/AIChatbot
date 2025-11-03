import json
import random
import os

print("Current working directory:", os.getcwd())

def load_intents(file_path):
    with open(file_path, 'r') as f:
        intents = json.load(f)
    return intents

def get_response(user_input, intents):
    user_input = user_input.lower()
    
    for intent in intents["intents"]:
        for pattern in intent["patterns"]:
            if pattern.lower() in user_input:
                return random.choice(intent["responses"])
            
    return "Sorry, I don't understand that."

def chat():
    print("Hello! I am your chatbot. Type 'exit' to end the conversation.")

    intents = load_intents("intents.json")
    
    while True:
        user_input = input("You: ")
        
        if user_input.lower() == 'exit':
            print("Goodbye! See you later.")
            break
        
        response = get_response(user_input, intents)
        print("Bot:", response)

if __name__ == "__main__":
    chat()
