import requests
import tkinter as tk
from tkinter import scrolledtext, END

API_URL = "https://api-inference.huggingface.co/models/microsoft/DialoGPT-medium"
HEADERS = {"Authorization": "Bearer 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"} 


def query_huggingface(prompt):
    """Send user message to Hugging Face conversational model."""
    payload = {"inputs": {"text": prompt}}
    try:
        response = requests.post(API_URL, headers=HEADERS, json=payload)
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list) and "generated_text" in data[0]:
                return data[0]["generated_text"]
            elif "generated_text" in data:
                return data["generated_text"]
            else:
                return "I'm not sure how to respond to that."
        else:
            return f"Error: {response.status_code} - {response.text}"
    except Exception as e:
        return f"⚠️ Network error: {e}"


class ChatbotApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Friendly ChatBot 💬")
        self.root.geometry("550x600")
        self.root.config(bg="#1e1e1e")

        self.chat_area = scrolledtext.ScrolledText(
            root, wrap=tk.WORD, width=65, height=25,
            font=("Arial", 10), bg="#2b2b2b", fg="white"
        )
        self.chat_area.pack(pady=10)
        self.chat_area.config(state='disabled')

        self.entry_field = tk.Entry(
            root, font=("Arial", 12),
            bg="#3c3f41", fg="white", insertbackground="white", width=45
        )
        self.entry_field.pack(side=tk.LEFT, padx=10, pady=10)

        self.send_button = tk.Button(
            root, text="Send", command=self.send_message,
            bg="#0078d7", fg="white", font=("Arial", 10, "bold")
        )
        self.send_button.pack(side=tk.LEFT)

        self.root.bind("<Return>", lambda event: self.send_message())

        self.display_message("Bot", "Hey there! 😊 I'm your chatbot friend. How are you today?")

    def display_message(self, sender, message):
        self.chat_area.config(state='normal')
        self.chat_area.insert(END, f"{sender}: {message}\n\n")
        self.chat_area.config(state='disabled')
        self.chat_area.yview(END)

    def send_message(self):
        user_input = self.entry_field.get().strip()
        if user_input:
            self.display_message("You", user_input)
            self.entry_field.delete(0, END)

            response = query_huggingface(user_input)
            self.display_message("Bot", response)


if __name__ == "__main__":
    root = tk.Tk()
    app = ChatbotApp(root)
    root.mainloop()
