from google import genai
from google.genai import types
import os
from dotenv import load_dotenv
#import easyocr until we fix import errors
import folium

load_dotenv('api.env')

# Try to get the API key from environment variables
# First checks api.env file, then system environment variables
google_api_key = os.getenv('GOOGLE_API_KEY')

# Validate that the API key was found
if not google_api_key:
    print("Please set GOOGLE_API_KEY in api.env file or as an environment variable")
    exit(1)

client = genai.Client(api_key=google_api_key)
#reader = easyocr.Reader(['en'], verbose=False)

with open('sample3.jpg', 'rb') as f:
    image_bytes = f.read()

#read ocr results
# ocr_results = reader.readtext('sample.jpg')
#ocr_texts = [text for (_, text, _) in ocr_results]
#ocr_block = "\n".join(ocr_texts) if ocr_texts else "NO TEXT FOUND"
ocr_block = ""#temporary

response = client.models.generate_content(
    model='gemini-2.5-flash',
    contents=[
        
        types.Part.from_bytes(
            data=image_bytes,
            mime_type='image/jpeg',
        ),
        # Prompt the model to analyze the image and OCR text to find the location
        # Expected output format: https://www.google.com/maps/search/?api=1&query=25.0285,121.5714
        f'''
        {ocr_block}

        
OCR TEXT FROM IMAGE:
{ocr_block}

    Your task: 
    Infer the MOST LIKELY CAMERA LOCATION where this photo was taken, NOT THE LANDMARK ITSELF IF PRESENTED.

    Instructions:
    1. Identify any signs (what is shown) visible.
    2. Estimate the direction the camera is facing (e.g., toward the west at sunset).
    3. Determine the camera's approximate POSITION based on:
        - perspective and viewing angle
        - height relative to horizon
        - distance implied by scale of buildings
        - direction of shadows
         - elevation (hill, tower, drone, roof)
        - relative position of skyline features

    The image may show:
        - a landmark,
        - a random road,
        - a forest,
        - a city skyline,
        - a residential street,
        - a commercial area,
        - an indoor/outdoor scene,
        - or a highly obscure place.

    No matter what type of image it is, ALWAYS estimate the camera's coordinates.


    ANALYZE THE IMAGE USING:

    1. **Landmarks (if present):**
        - Identify any recognizable buildings, towers, mountains, bridges, monuments.
        - Use them ONLY as reference points to triangulate where the photographer stood.
        - DO NOT return the landmark's own coordinates.

    2. **Road & Infrastructure Clues:**
        - Road markings (solid lines, dashed lines, shoulder style)
        - Sign shape, color, typography (USA uses MUTCD signs, EU uses Vienna Convention)
        - Speed limit sign design
        - Guardrail style
        - Road curvature, width, asphalt color
        - Shoulder type (gravel, grass, concrete)

    3. **Environmental & Landscape Clues:**
        - Tree species and density
        - Grass color
        - Desert vs alpine vs coastal vs plains
        - Mountain shapes and snowline
        - Vegetation typical of certain regions

    4. **Urban/Suburban Clues (if applicable):**
        - Traffic lights, crosswalks, streetlamp style
        - Fences, sidewalks, benches
        - Storefront colors, neon signs
        - Vehicle models and license plate shapes (blurred or not)

    5. **Directional + Lighting Clues:**
        - Sun angle (estimate time of day)
        - Shadows for cardinal direction
        - Orientation toward major landmarks or sunsets

    6. **OCR TEXT (optional):**
        If text is present, use it to narrow down region.
        If no text, ignore OCR gracefully.

        --------------------------
        OUTPUT REQUIREMENTS:
        --------------------------

     - Latitude and longitude must be decimal numbers.
        - PROVIDE AN EXPLANATION of your reasoning STEPS in arriving at the estimated camera location.
        - IF UNSURE, make your best estimate based on available clues
        - DO NOT output the coordinates of a landmark unless the camera was physically AT that landmark AS AN EXAMPLE.

    then, at the end of the response return only coordinates comma-separated like so between brackets(ensure there are no other brackets in response to avoid find() method errors): 
        [<LATITUDE>,<LONGITUDE>]

        '''
    ]
)   

url = "https://www.google.com/maps/search/?api=1&query=%LATITUDE%,%LONGITUDE%"
coord_str = response.text
#coord_str = "25.0285,121.5714"
first_bracket = coord_str.find('[')
first_comma = coord_str.find(',', first_bracket)
Latitude = float(coord_str[first_bracket+1:first_comma])#find(value, start, end)
Longitude = float(coord_str[first_comma+1:coord_str.len()-1])

#complete url
url.replace("%LATITUDE%", Latitude)
url.replace("%LONGITUDE%", Longitude)

#create folium map
m = folium.Map(
    location=(Latitude, Longitude),
    width= 800,
    height= 600
)

#get map components
m.get_root().render()
header = m.get_root().header.render()
body_html = m.get_root().html.render()
script = m.get_root().script.render()

#https://www.google.com/maps/search/?api=1&query=25.0285,121.5714 for sample.jpg
maps_container = """
    <div class="maps-container">
        <ul>
            <li>
                <a href="%GOOGLE_URL%"></a>
                    <p>
                        Google Maps Query
                    </p>
                </a>
            <li>
            <li>
                %MAP_BODY%
            </li>
        <ul>
    </div>
"""
html_frame = ""
with open("maps.html", "r") as f:
    html_frame = f.read()

html_frame.replace("%MAP_META%", header)
maps_container.replace("%MAP_BODY%", body_html)
html_frame.replace("%MAP_SCRIPT%", script)

maps_container.replace("%GOOGLE_URL%",url)
#note: you probably need to use a stronger AI model to be able to more accurately depict location from images; however, does somewhat work 

print(response.text)
print("\nPage:\n")
print(maps_container)