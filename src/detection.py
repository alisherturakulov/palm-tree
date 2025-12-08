import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from google import genai
from google.genai import types
from dotenv import load_dotenv
from image_resize import resize_image

load_dotenv("api.env")

app = Flask(__name__)
CORS(app)

google_api_key = os.getenv("GOOGLE_API_KEY")
if not google_api_key:
    print("No API key. Fix your life.")
    exit(1)

client = genai.Client(api_key = google_api_key)


def analyze_image_with_gemini(image_bytes, mime):
    # Resize before sending to AI model
    image_bytes = resize_image(image_bytes, max_size=1024)

    ocr_block = ""  # your temp placeholder

    response = client.models.generate_content(
        model = 'gemini-2.5-flash',
        contents = [
            types.Part.from_bytes(
                data = image_bytes,
                mime_type = mime,
            ),
            f'''
            {ocr_block}

            OCR TEXT FROM IMAGE:
            {ocr_block}

            Your task: 
            Infer the MOST LIKELY CAMERA LOCATION where this photo was taken, NOT THE LANDMARK ITSELF IF PRESENTED.

            Instructions:
            1. Identify any signs (what is shown) visible.
            2. Estimate the direction the camera is facing.
            3. Determine the camera's approximate POSITION based on:
                - perspective
                - horizon height
                - distance scaling
                - shadows
                - elevation
                - skyline relative position

            Image may show anything. ALWAYS estimate the camera's coordinates.

            ANALYZE USING:
            - Landmarks
            - Roads
            - Tree species
            - Geography
            - Urban features
            - Lighting direction
            - OCR text (if present)

            OUTPUT REQUIREMENTS:
            - Provide explanation of reasoning.
            - Then at the end return ONLY:
              [<LATITUDE>,<LONGITUDE>]
            '''
        ]
    )

    text = response.text.strip()
    return text

@app.route("/analyze", methods=["POST"])
def analyze_api():
    if "image" not in request.files:
        return jsonify({"error": "No file sent."}), 400

    img = request.files["image"]
    image_bytes = img.read()
    mime = img.mimetype

    gemini_output = analyze_image_with_gemini(image_bytes, mime)

    # Extract coordinates from brackets
    try:
        first = gemini_output.find("[")
        comma = gemini_output.find(",", first)
        last = gemini_output.find("]", comma)

        lat = float(gemini_output[first + 1 : comma])
        lon = float(gemini_output[comma + 1 : last])

    except Exception as exc:
        return jsonify({
            "error": "Model returned invalid coordinate format",
            "model_output": gemini_output
        }), 500

    return jsonify({
        "result": gemini_output,
        "latitude": lat,
        "longitude": lon
    })


if __name__ == "__main__":
    app.run(debug = True)
