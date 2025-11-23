from google import genai
from google.genai import types
#for api key retrieval
import os

google_api_key = os.getenv('GOOGLE_API_KEY')
if not google_api_key:
    print(f"Error: cant find api key in environment variables")
    exit(1)

client = genai.Client(api_key=google_api_key)

with open('sample.jpg', 'rb') as f:
    image_bytes = f.read()

response = client.models.generate_content(
    model='gemini-2.5-flash',
    contents=[
        types.Part.from_bytes(
            data=image_bytes,
            mime_type='image/jpeg',
        ),
        ''''
        give your best guess at the location of this image, 
        then return only this url with fields filled in: 
        https://www.google.com/maps/search/?api=1&query=<LATITUDE>,<LONGITUDE>
        '''
    ]
)

print(response.text)
