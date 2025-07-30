import os
import streamlit as st
import speech_recognition as spr
from gtts import gTTS
from googletrans import Translator
import base64 
import cv2
import numpy as np
import easyocr
import matplotlib.pyplot as plt
from PIL import Image
import io
import tempfile


def recognize_text(image, lang):
    '''Loads an image and recognizes text using EasyOCR.'''
    try:
        reader = easyocr.Reader([lang])
        print(f"EasyOCR initialized for language: {lang}")
        result = reader.readtext(image)
        return result
    except Exception as e:
        print(f"Error initializing EasyOCR: {e}")
        return None


def ocr_text(image_bytes, lang):
    '''Extract text from an image using OCR.'''
    result = recognize_text(image_bytes, lang)
    
    if result is None:
        print("OCR failed or returned no results.")
        return ""  

    extracted_text = ""
    for (bbox, text, prob) in result:
        if prob > 0:
            extracted_text += f"{text}\n"
    return extracted_text.strip()


def file_conversion(doc_file, to_lang):
    try:
        translator = Translator()
        content = doc_file.read().decode("utf-8")
        translated = translator.translate(content, dest=to_lang)
        return translated.text
    except Exception as e:
        return f"An error occurred during translation: {e}"

def set_background(image_file):
    if os.path.exists(image_file):
        with open(image_file, 'rb') as f:
            image_url = f"data:image/png;base64,{base64.b64encode(f.read()).decode()}"
            st.markdown(
                f"""
                <style>
                .stApp {{
                    background-image: url("{image_url}");
                    background-size: cover;
                    background-position: center;
                    background-repeat: no-repeat;
                }}
                </style>
                """,
                unsafe_allow_html=True
            )
    else:
        st.error(f"Background image file '{image_file}' not found. Please check the file path.")

def audio_to_audio(from_lang, to_lang):
    try:
        recog1 = spr.Recognizer()
        mc = spr.Microphone()

        st.info("Please speak a sentence to translate.")
        
        with mc as source:
            recog1.adjust_for_ambient_noise(source, duration=0.2)
            audio = recog1.listen(source)
        get_sentence = recog1.recognize_google(audio, language=from_lang)
        st.success(f"Recognized speech: {get_sentence}")
        translator = Translator()
        text_to_translate = translator.translate(get_sentence, src=from_lang, dest=to_lang)
        translated_text = text_to_translate.text
        st.success(f"Translated text: {translated_text}")
        tts = gTTS(text=translated_text, lang=to_lang, slow=False)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_audio:
            tts.save(temp_audio.name)
            audio_path = temp_audio.name
        audio_file = open(audio_path, "rb")
        audio_bytes = audio_file.read()
        st.audio(audio_bytes, format="audio/mp3")
        os.remove(audio_path)

    except spr.UnknownValueError:
        st.error("Unable to understand the audio input.")
    except spr.RequestError as e:
        st.error(f"Error during speech recognition: {e}")
    except Exception as e:
        st.error(f"An unexpected error occurred: {e}")

selected_tab = st.sidebar.selectbox("Select Tab", ("TEXT-TRANSLATOR", "IMAGE TEXT EXTRACTION", "DOCUMENT TRANSLATOR", "AUDIO-TO-AUDIO"))
path = r"C:\Users\Owner\Desktop\WhatsApp Image 2024-11-27 at 21.20.10_f2454893.jpg"

if selected_tab == "TEXT-TRANSLATOR":
    set_background(path)
    st.markdown("<h1 style='text-align: center; color: #E7F6F2'>Text Translator</h1>", unsafe_allow_html=True)
    st.markdown("<h2 style='text-align: center; color: #DA0037;'>Enter Text for Translation</h2>", unsafe_allow_html=True)
    
    from_text = st.text_area("Enter the text to translate:")
    to_lang = st.text_input("Enter the target language code (e.g., 'en' for English, 'hi' for Hindi,'bn' for bengali, 'kn' for kannada, 'ml' for malayalam, 'mr' for marathi, 'or' for odia, 'pa' for 'punjabi', 'ta' for tamil, 'te' for telugu):")
    
    if st.button("Translate Text"):
        if from_text and to_lang:
            try:
                from deep_translator import GoogleTranslator
                translated_text = GoogleTranslator(source='auto', target=to_lang).translate(from_text)
                st.write("### Translated Text")
                st.write(translated_text)
            except Exception as e:
                st.error(f"An error occurred during translation: {e}")
        else:
            st.error("Please enter both text and target language.")

elif selected_tab == "IMAGE TEXT EXTRACTION":
#     path = r"C:\Users\Owner\Downloads\DALL·E 2024-11-26 15.25.56 - An elegant abstract background for a web application, featuring flowing waves of blue, green, and gold with a soft, glowing effect. The design should .webp"
    set_background(path)  
    st.markdown("<h1 style='text-align: center; color: #E7F6F2;'>Image Text Detection</h1>", unsafe_allow_html=True)
    st.markdown("<h2 style='text-align: center; color: #DA0037;'>Upload an Image to Detect and Translate</h2>", unsafe_allow_html=True)
    file = st.file_uploader("Please upload an image", type=['jpeg', 'jpg', 'png'])
    if file is not None:
        temp_file_path = os.path.join("temp_dir", file.name)
        os.makedirs("temp_dir", exist_ok=True)
        with open(temp_file_path, "wb") as f:
            f.write(file.getbuffer())
    from_lang = st.text_input("Enter the target language code (e.g., 'en' for English")
    to_lang = st.text_input("Enter the target language code (e.g., 'en' for English, 'hi' for Hindi,'bn' for bengali, 'kn' for kannada, 'ml' for malayalam, 'mr' for marathi, 'or' for odia, 'pa' for 'punjabi', 'ta' for tamil, 'te' for telugu):")
    
    if st.button("Extract and Translate Text"):
        if file is not None and from_lang and to_lang:
            try:
                file_bytes = file.read()
                image = Image.open(io.BytesIO(file_bytes)).convert('RGB')
                st.image(image, caption='Uploaded Image', use_column_width=True)
                
                text = ocr_text(temp_file_path, from_lang)
                
                if text.strip():
                    st.write("### Extracted Text")
                    st.write(text)
                    from deep_translator import GoogleTranslator
                    translated_text = GoogleTranslator(source='auto', target=to_lang).translate(text)
                    st.write("### Translated Text")
                    st.write(translated_text)
#                 else:
#                     st.warning("No text was detected in the image.")
            except Exception as e:
                st.error(f"An error occurred: {e}")
        else:
            st.warning("Please upload an image and provide valid language codes.")

elif selected_tab == "DOCUMENT TRANSLATOR":
#     path = r"C:\Users\Owner\Downloads\DALL·E 2024-11-26 15.26.01 - A futuristic abstract background for a web page, featuring a dark theme with neon accents in cyan, magenta, and violet. The design includes geometric .webp"
    set_background(path)
    st.markdown("<h1 style='text-align: center;'>Document Translator</h1>", unsafe_allow_html=True)
    st.markdown("<h2 style='text-align: center; color: #DA0037;'>Upload a Document to Translate</h2>", unsafe_allow_html=True)
    
    doc_file = st.file_uploader("Upload a text document", type=["txt"])
    to_lang = st.text_input("Enter the target language code (e.g., 'en' for English, 'hi' for Hindi,'bn' for bengali, 'kn' for kannada, 'ml' for malayalam, 'mr' for marathi, 'or' for odia, 'pa' for 'punjabi', 'ta' for tamil, 'te' for telugu):")
    
    if st.button("Translate Document"):
        if doc_file and to_lang:
            translated_doc = file_conversion(doc_file, to_lang)
            st.write("### Translated Document Text")
            st.write(translated_doc)
        else:
            st.error("Please upload a document and enter the target language code.")

elif selected_tab == "AUDIO-TO-AUDIO":
    st.markdown("<h1 style='text-align: center; color: #E7F6F2'>Audio Translator</h1>", unsafe_allow_html=True)
    st.markdown("<h2 style='text-align: center; color: #DA0037;'>Speak to Translate</h2>", unsafe_allow_html=True)
    set_background(path)

    from_lang = st.text_input("Enter the source language code (e.g., 'en' for English, 'hi' for Hindi,'bn' for bengali, 'kn' for kannada, 'ml' for malayalam, 'mr' for marathi, 'or' for odia, 'pa' for 'punjabi', 'ta' for tamil, 'te' for telugu):")
    to_lang = st.text_input("Enter the target language code (e.g., 'en' for English, 'hi' for Hindi,'bn' for bengali, 'kn' for kannada, 'ml' for malayalam, 'mr' for marathi, 'or' for odia, 'pa' for 'punjabi', 'ta' for tamil, 'te' for telugu):")

    if st.button("Start Audio Translation"):
        if from_lang and to_lang:
            st.info("Initializing audio translation...")
            audio_to_audio(from_lang, to_lang)
        else:
            st.error("Please enter both source and target language codes.")
