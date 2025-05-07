from google import genai
from google.genai import types
from PIL import Image
from io import BytesIO
import base64
import json
import os
import time

# ==== CONFIGURATION ====
def read_api_key(path="Generation/api.json"):
    if not os.path.exists(path):
        raise FileNotFoundError(f"API key file not found: {path}")
    with open(path, "r") as f:
        data = json.load(f)
    return data.get("GEMINI_API_KEY", None)

API_KEY = read_api_key()
client = genai.Client(api_key=API_KEY)

# ==== PATHS ====
PROMPT_FILE = "C:/Users/jotir/Downloads/simplified_prompts.json"
SAVE_DIR = "generated_images"
os.makedirs(SAVE_DIR, exist_ok=True)

# ==== IMAGE GENERATION FUNCTIONS ====
def generate_with_gemini(prompt, index):
    """Generate images using Gemini 2.0 Flash Experimental (text+image interleaved)"""
    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash-exp-image-generation",
            contents=prompt,
            config=types.GenerateContentConfig(
                response_modalities=['Text', 'Image']
            )
        )

        if response.candidates:
            for i, part in enumerate(response.candidates[0].content.parts):
                if part.inline_data:
                    save_path = os.path.join(SAVE_DIR, f"gemini_{index:04}_{1}.png")
                    Image.open(BytesIO(part.inline_data.data)).save(save_path)
                    print(f"Saved Gemini image: {save_path}")
        time.sleep(2)
        
    except Exception as e:
        print(f"Gemini Error: {e}")

def generate_with_imagen(prompt, index):
    """Generate images using Imagen 3 (high quality)"""
    try:
        response = client.models.generate_images(
            model="imagen-3.0-generate-002",
            prompt=prompt,
            config=types.GenerateImagesConfig(
                number_of_images=1,  # Can be 1-4
                aspect_ratio="1:1",  # Options: 1:1, 3:4, 4:3, 9:16, 16:9
                person_generation="ALLOW_ADULT"
            )
        )

        for i, img in enumerate(response.generated_images):
            save_path = os.path.join(SAVE_DIR, f"imagen_{index:04}_{1}.png")
            Image.open(BytesIO(img.image.image_bytes)).save(save_path)
            print(f"Saved Imagen image: {save_path}")
        time.sleep(1.5)
        
    except Exception as e:
        print(f"Imagen Error: {e}")

# ==== MAIN EXECUTION ====
with open(PROMPT_FILE, "r") as f:
    prompts = json.load(f)

for i, prompt in enumerate(prompts):
    print(f"\nProcessing prompt {i+1}/{len(prompts)}")
    
    # Generate with both models
    generate_with_gemini(prompt, i)
    #generate_with_imagen(prompt, i)

print("✅ All generations completed!")