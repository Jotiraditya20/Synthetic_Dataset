import os
import random
from PIL import Image, ImageDraw, ImageFont
import json5

try:
    with open('Generation/corpus.txt', 'r') as f:
        corpus_words = [line.strip() for line in f if line.strip()]
except Exception:
    corpus_words = ["Time", "Measurement", "Experiment", "Data", "Result"]

if not corpus_words:
    corpus_words = ["Time", "Measurement", "Experiment", "Data", "Result"]

# Loading JSON file
def load_config(config_path):
    with open(config_path, "r") as f:
        config = json5.load(f)  # json5 allows comments
    return config

config = load_config("Generation/config.json5")

# Global counter to track function calls
call_count = 0

import os
import random
from PIL import Image, ImageDraw, ImageFont

# Make sure to define or initialize call_count (if it's used globally)
call_count = 0

def get_random_images(num_images, image_sizes, caption_texts=None, caption_height=20, font_path="arial.ttf", font_size=14,
                      science_folder="Generation/science_images", non_science_folder="Generation/non_science_images"):
    """
    Returns a list of images with captions already embedded.
    Each image is resized to a given target size which includes extra caption space at the bottom.
    
    :param num_images: Number of images to pick.
    :param image_sizes: List of tuples (target_width, total_height) for the final images.
    :param caption_texts: Optional list of captions. If not provided, default captions will be generated.
    :param caption_height: Height (in pixels) reserved for caption text.
    :param font_path: Path to the font used for caption.
    :param font_size: Font size for caption.
    :returns: List of file paths to the generated images.
    """
    global call_count
    call_count += 1
    base_dir = "Generation"
    image_dir = os.path.join(base_dir, "image")
    os.makedirs(image_dir, exist_ok=True)
    image_paths = []

    # List science and non-science images
    science_images = [os.path.join(science_folder, f) for f in os.listdir(science_folder) if f.lower().endswith(('.jpg', '.png', '.jpeg'))]
    non_science_images = [os.path.join(non_science_folder, f) for f in os.listdir(non_science_folder) if f.lower().endswith(('.jpg', '.png', '.jpeg'))]

    if not science_images:
        raise ValueError("No science images found in the specified folder.")
    if not non_science_images:
        raise ValueError("No non-science images found in the specified folder.")

    for i in range(num_images):
        # 90% chance to pick a science image, else non-science.
        if random.random() < config["split"]:
            image_path = random.choice(science_images)
        else:
            image_path = random.choice(non_science_images)

        img = Image.open(image_path)

        # Get target dimensions (target_width, total_height)
        target_width, target_total_height = image_sizes[i % len(image_sizes)]
        target_width = int(target_width)
        target_total_height = int(target_total_height)
        target_img_height = target_total_height - caption_height  # Space reserved for caption

        # Resize the image for the graphic region.
        img = img.resize((target_width, target_img_height), Image.LANCZOS)

        # Create a new canvas that provides space for the caption.
        new_img = Image.new("RGB", (target_width, target_total_height), "white")
        new_img.paste(img, (0, 0))

        # Determine the caption text.
        if caption_texts and i < len(caption_texts):
            caption = caption_texts[i]
        else:
            # Create a default caption using random corpus words.
            default_caption = f"Fig {call_count}_{i+1}: " + " ".join(random.sample(corpus_words, random.randint(1, 5)))
            caption = default_caption

        # Draw the caption on new_img
        draw = ImageDraw.Draw(new_img)
        try:
            font = ImageFont.truetype(font_path, font_size)
        except IOError:
            font = ImageFont.load_default()
        text_bbox = draw.textbbox((0, 0), caption, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        # Center the caption horizontally
        x_text = (target_width - text_width) // 2
        y_text = target_img_height + (caption_height - font_size) // 2
        draw.text((x_text, y_text), caption, fill="black", font=font)

        # Save final image
        save_path = os.path.join(image_dir, f"{call_count}_{i+1}.jpg")
        new_img.save(save_path)
        image_paths.append(save_path)

    return image_paths
# Example usage
#science_folder = "Generation/science_images"
#non_science_folder = "Generation/non_science_images"
#image_sizes = [[200, 200], [400, 400], [500, 500], [600, 600]]
#image_paths = get_random_images(5, image_sizes, science_folder, non_science_folder)
#print(f"Generated images: {image_paths}")
