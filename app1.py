from flask import Flask, render_template, request, jsonify
from twilio.twiml.messaging_response import MessagingResponse
import google.generativeai as genai
import Schemes
from deep_translator import GoogleTranslator
from gtts import gTTS
import os
import speech_recognition as sr
from datetime import datetime
from langdetect import detect, DetectorFactory
import config
import tempfile
import requests
from pydub import AudioSegment

# Initialize Flask and configure AI
DetectorFactory.seed = 0
app = Flask(__name__)
genai.configure(api_key=config.API_KEY)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/ask', methods=['POST'])
def ask():
    """Handle browser requests"""
    try:
        data = request.json
        user_input = data.get('query', '').strip()
        lang = detect(user_input)
        
        # Process input
        translated_query = translate(user_input, lang, 'en')
        response = generate_response(translated_query, lang)
        translated_response = translate(response, 'en', lang)
        
        return jsonify({
            'response': translated_response,
            'language': lang,
            'timestamp': datetime.now().strftime("%I:%M %p")
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/whatsapp', methods=['POST'])
def whatsapp():
    """Handle WhatsApp requests"""
    resp = MessagingResponse()
    
    try:
        # Handle text/voice input
        user_input = get_whatsapp_input(request)
        if not user_input:
            raise ValueError("No valid input detected")
            
        lang = detect(user_input) if user_input else 'en'
        
        # Generate response
        translated_query = translate(user_input, lang, 'en')
        response = generate_response(translated_query, lang)
        translated_response = translate(response, 'en', lang)
        
        resp.message(translated_response)
        
    except Exception as e:
        resp.message("Error processing request. Please try again.")
        
    return str(resp)

@app.route('/voice', methods=['POST'])
def voice_input():
    """Handle voice input from browser"""
    try:
        recognizer = sr.Recognizer()
        audio_file = request.files['audio']
        
        with tempfile.NamedTemporaryFile(suffix=".webm") as tmp:
            audio_file.save(tmp.name)
            
            # Convert audio format using pydub
            sound = AudioSegment.from_file(tmp.name)
            wav_path = tmp.name + ".wav"
            sound.export(wav_path, format="wav")
            
            with sr.AudioFile(wav_path) as source:
                audio_data = recognizer.record(source)
                text = recognizer.recognize_google(audio_data, language='auto')
                lang = detect(text)
                
            os.remove(wav_path)
            
        return jsonify({
            'text': text,
            'language': lang
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/speak', methods=['POST'])
def speak():
    """Generate speech from text"""
    try:
        data = request.json
        text = data.get('text', '')
        lang = data.get('language', 'en')
        
        tts = gTTS(text=text, lang=lang)
        filename = f"static/response_{datetime.now().timestamp()}.mp3"
        tts.save(filename)
        
        return jsonify({'audio': filename})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def generate_response(query, target_lang='en'):
    """Generate language-consistent structured response"""
    try:
        if 'scheme' in query.lower():
            scheme_response = Schemes.get_details(query)
            return translate(scheme_response, 'en', target_lang)
            
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(f"""
            Provide detailed information about: {query}
            Structure your response in this exact format:
            
            [Overview]
            • Comprehensive explanation in simple {target_lang}
            
            [Requirements]
            • List of required documents/qualifications
            
            [Process]
            • Step-by-step application procedure
            
            [Important Notes]
            • Key considerations and deadlines
            
            [Contact]
            • Relevant authorities/website links
            
            Use only bullet points (•) in {target_lang}
            Keep language natural and conversational
            Include all essential details but be concise
        """).text
        
        # Ensure consistent bullet points
        return response.replace('- ', '• ').replace('*', '•')
        
    except Exception as e:
        return translate("Could not generate response. Please try again.", 'en', target_lang)

def translate(text, source, target):
    """Enhanced translation with formatting preservation"""
    try:
        if source == target:
            return text
            
        # Preserve bullet points during translation
        translated = GoogleTranslator(source=source, target=target).translate(text)
        return translated.replace('•', '•')  # Maintain bullet characters
        
    except Exception as e:
        print(f"Translation Error: {str(e)}")
        return text

def get_whatsapp_input(request):
    """Process WhatsApp input with better voice handling"""
    if request.values.get('NumMedia') == '1':
        return process_whatsapp_voice(request.values.get('MediaUrl0'))
    return request.values.get('Body', '').strip()

def process_whatsapp_voice(url):
    """Process WhatsApp voice messages with format conversion"""
    try:
        with tempfile.NamedTemporaryFile(suffix='.ogg') as ogg_file:
            # Download the voice message
            audio_data = requests.get(url).content
            ogg_file.write(audio_data)
            ogg_file.seek(0)
            
            # Convert OGG to WAV
            audio = AudioSegment.from_ogg(ogg_file.name)
            with tempfile.NamedTemporaryFile(suffix='.wav') as wav_file:
                audio.export(wav_file.name, format="wav")
                
                # Recognize audio
                recognizer = sr.Recognizer()
                with sr.AudioFile(wav_file.name) as source:
                    audio_data = recognizer.record(source)
                    return recognizer.recognize_google(audio_data, language='auto')
                    
    except Exception as e:
        print(f"Voice processing error: {str(e)}")
        return None

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)