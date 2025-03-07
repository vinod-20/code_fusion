from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import requests
import os

# Load environment variables (or use hardcoded credentials)
TWILIO_WHATSAPP_NUMBER = "whatsapp:+14155238886"  # Replace with your Twilio WhatsApp number
API_KEY = "AIzaSyCq4DvjcxxjWmhiYb_-6d6MTkT0wFJruos"  # Replace with your actual Gemini API key

app = Flask(__name__)

# Function to get chatbot response from Gemini API
def get_chatbot_response(user_input):
    url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={API_KEY}"
    
    headers = {
        "Content-Type": "application/json"
    }

    payload = {
        "contents": [{"parts": [{"text": user_input}]}]
    }

    response = requests.post(url, json=payload, headers=headers)
    
    if response.status_code == 200:
        return response.json()["candidates"][0]["content"]["parts"][0]["text"]
    else:
        return "Error: Unable to fetch response from Gemini API."

# WhatsApp webhook route
@app.route('/whatsapp', methods=['POST'])
def whatsapp_webhook():
    user_input = request.form.get("Body")
    
    if not user_input:
        return "No input received", 400
    
    bot_response = get_chatbot_response(user_input)
    
    # Respond using Twilio's messaging response
    twilio_resp = MessagingResponse()
    twilio_resp.message(bot_response)
    
    return str(twilio_resp)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
