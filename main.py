from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import Optional
from PIL import Image
import io
import base64
import speech_recognition as sr
from deep_translator import GoogleTranslator

app = FastAPI()

# Mock model functions (replace these with actual models)
def process_text_model(text: str) -> str:
    """
    Translate English text into Tamil using GoogleTranslator.
    """
    translated = GoogleTranslator(source='en', target='ta').translate(text)
    return translated

def process_image_model(image_bytes: bytes, size=(256, 256)) -> str:
    """
    Resize image using Pillow (PIL) and return as base64 string.
    """
    image = Image.open(io.BytesIO(image_bytes))
    image = image.resize(size)
    
    # Save the resized image to a bytes buffer
    buffered = io.BytesIO()
    image.save(buffered, format="JPEG")
    # Encode the image to base64
    img_str = base64.b64encode(buffered.getvalue()).decode('utf-8')
    return img_str

def process_audio_model(audio_bytes: bytes) -> str:
    """
    Convert audio to text using SpeechRecognition.
    """
    recognizer = sr.Recognizer()
    audio = sr.AudioFile(io.BytesIO(audio_bytes))

    with audio as source:
        audio_data = recognizer.record(source)
    
    try:
        text = recognizer.recognize_google(audio_data)
        return f"Converted Text: {text}"
    except sr.UnknownValueError:
        return "Could not understand the audio"
    except sr.RequestError:
        return "API request error"

@app.get("/", response_class=HTMLResponse)
async def main():
    html_content = """
    <!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>File Processing App</title>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css" rel="stylesheet">
    <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&display=swap" rel="stylesheet">
    <style>
        body {
            font-family: 'Roboto', sans-serif;
            margin: 0;
            background-color: #e9ecef;
            color: #333;
        }
        .container {
            max-width: 900px;
            margin: 40px auto;
            padding: 30px;
            background-color: #ffffff;
            border-radius: 15px;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
            transition: transform 0.3s;
        }
        .container:hover {
            transform: translateY(-5px);
        }
        h1 {
            text-align: center;
            color: #007bff;
            margin-bottom: 30px;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 2px;
        }
        h2 {
            color: #28a745;
            margin-top: 20px;
            font-weight: 600;
            border-bottom: 2px solid #28a745;
            padding-bottom: 5px;
            transition: color 0.3s;
        }
        h2:hover {
            color: #218838;
        }
        form {
            margin-bottom: 30px;
            border: 1px solid #007bff;
            border-radius: 10px;
            padding: 20px;
            background-color: #f8f9fa;
            transition: background-color 0.3s;
        }
        form:hover {
            background-color: #e2e6ea;
        }
        .text, input[type="file"]{
            width: 98%;
            padding: 12px;
            border-radius: 5px;
            align-items: center;
            border: 1px solid #ced4da;
            margin-top: 10px;
            font-size: 16px;
            transition: border-color 0.3s;
        }

        .text:focus, input[type="file"]:focus, input[type="submit"]:focus {
            border-color: #007bff;
            outline: none;
        }
        .submit{
            width: 50%;
            padding: 12px;
            border-radius: 5px;
            align-items: center;
            border: 1px solid #ced4da;
            margin-top: 10px;
            text-align: center;
            justify-content: center;
            margin-left:25%;
            font-size: 16px;
            transition: border-color 0.3s;            
        }
        input[type="submit"]:hover {
            background-color: #0056b3;
            transform: translateY(-2px);
        }
        .result {
            margin-top: 20px;
            padding: 15px;
            border: 1px solid #ddd;
            background-color: #ffffff;
            border-radius: 5px;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
        }
        img {
            margin-top: 10px;
            max-width: 100%;
            height: auto;
            border-radius: 5px;
        }
        .footer {
            text-align: center;
            margin-top: 40px;
            color: #6c757d;
            font-size: 14px;
        }
    </style>
    <script>
        async function handleFormSubmit(event, formId, resultId) {
            event.preventDefault();
            const form = document.getElementById(formId);
            const resultDiv = document.getElementById(resultId);
            
            let formData = new FormData(form);
            const url = form.action;

            try {
                let response = await fetch(url, {
                    method: 'POST',
                    body: formData
                });
                let result = await response.json();

                // Display the result
                if (result.translated_text) {
                    resultDiv.innerHTML = result.translated_text;
                } else if (result.result) {
                    resultDiv.innerHTML = result.result;

                    // If the result is an image, create an img element
                    if (result.image) {
                        const img = document.createElement("img");
                        img.src = "data:image/jpeg;base64," + result.image;
                        resultDiv.appendChild(img);
                    }
                }
            } catch (error) {
                resultDiv.innerHTML = "Error: " + error.message;
            }
        }
    </script>
</head>
<body>
    <div class="container">
        <h1>File Processing App</h1>

        <h2><i class="fas fa-language"></i> Text (English to Tamil Translation)</h2>
        <form id="text-form" action="/process-text" method="post" onsubmit="handleFormSubmit(event, 'text-form', 'text-result')">
            <input type ='text' class="text" name="content" rows="4" placeholder="Enter English text here..." required></input><br>
            <input class="submit" type="submit" value="Translate to Tamil">
        </form>
        <div class="result" id="text-result"></div>

        <h2><i class="fas fa-image"></i> Image (Resize to 256x256)</h2>
        <form id="image-form" action="/process-image" enctype="multipart/form-data" method="post" onsubmit="handleFormSubmit(event, 'image-form', 'image-result')">
            <input type="file" name="file" accept="image/*" required><br>
            <input class="submit" type="submit" value="Resize Image">
        </form>
        <div class="result" id="image-result"></div>

        <h2><i class="fas fa-volume-up"></i> Audio (Speech-to-Text)</h2>
        <form id="audio-form" action="/process-audio" enctype="multipart/form-data" method="post" onsubmit="handleFormSubmit(event, 'audio-form', 'audio-result')">
            <input type="file" name="file" accept="audio/*" required><br>
            <input class ="submit" type="submit" value="Convert Audio to Text">
        </form>
        <div class="result" id="audio-result"></div>
    </div>
    <div class="footer">
        <p>&copy; 2024 File Processing App. All rights reserved.</p>
    </div>
</body>
</html>

    """
    return HTMLResponse(content=html_content)

# Route for processing text input (English to Tamil translation)
@app.post("/process-text")
async def process_text(content: str = Form(...)):
    try:
        result = process_text_model(content)
        return {"translated_text": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Route for processing image input (Image resizing)
@app.post("/process-image")
async def process_image(file: UploadFile = File(...)):
    try:
        file_content = await file.read()
        img_str = process_image_model(file_content)
        return {"result": " ", "image": img_str}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Route for processing audio input (Speech-to-text)
@app.post("/process-audio")
async def process_audio(file: UploadFile = File(...)):
    try:
        file_content = await file.read()
        result = process_audio_model(file_content)
        return {"result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
