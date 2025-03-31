import os
import random
from PIL import Image, ImageDraw, ImageFont
import json5

# Load json configuration file
def load_config(config_path):
    with open(config_path, "r") as f:
        config = json5.load(f)  # json5 allows comments
    return config

config = load_config("Generation/config.json5")

# Global counter to track function calls
call_count = 0

# Path to the corpus file
CORPUS_FILE = "Generation/corpus.txt"

# Function to load words from the corpus file
def load_corpus(corpus_file):
    with open(corpus_file, "r") as file:
        words = [line.strip() for line in file if line.strip()]
    return words

# Wrap text to fit within max width
def wrap_text(text, font, max_width):
    lines = []
    words = text.split()
    current_line = words[0]

    for word in words[1:]:
        bbox = font.getbbox(current_line + " " + word)
        text_width = bbox[2] - bbox[0]
        if text_width <= max_width:
            current_line += " " + word
        else:
            lines.append(current_line)
            current_line = word

    lines.append(current_line)
    return lines

# Function to justify text and draw on image
def justify_text(draw, text, font, x, y, max_width, image_height):
    lines = wrap_text(text, font, max_width)
    line_height = font.getbbox("hg")[3] - font.getbbox("hg")[1] + 5  # Increased spacing

    # Calculate total text height
    total_text_height = len(lines) * line_height

    # Check if text fits within the image height, if not, reduce lines
    if total_text_height > image_height - 10:  # Keeping 10px bottom margin
        lines = lines[: (image_height - 10) // line_height]

    for line in lines:
        words_in_line = line.split()
        if len(words_in_line) > 1:
            total_text_width = sum(font.getbbox(word)[2] - font.getbbox(word)[0] for word in words_in_line)
            total_spacing = max_width - total_text_width
            space_between_words = total_spacing // (len(words_in_line) - 1) if len(words_in_line) > 1 else 0

            x_offset = x
            for word in words_in_line:
                draw.text((x_offset, y), word, font=font, fill="black")
                x_offset += font.getbbox(word)[2] - font.getbbox(word)[0] + space_between_words
        else:
            draw.text((x, y), line, font=font, fill="black")

        y += line_height  # Adjusted for more spacing

# Generate a text image with proper spacing
def generate_text_image(text, image_size, font_path="times.ttf", font_size=14, bold=False):
    image = Image.new("RGB", image_size, "white")
    draw = ImageDraw.Draw(image)

    try:
        if bold:
            # Attempt 1: Load dedicated bold font (e.g., "timesbd.ttf")
            bold_font_variants = [
                font_path.replace(".ttf", "bd.ttf"),  # Common pattern (timesbd.ttf)
                font_path.replace(".ttf", "-bold.ttf"),  # Alternate pattern (times-bold.ttf)
                os.path.join(os.path.dirname(font_path), "Bold", os.path.basename(font_path))  # Bold subfolder
            ]
            
            for bold_font_path in bold_font_variants:
                try:
                    font = ImageFont.truetype(bold_font_path, font_size)
                    break  # Successfully loaded bold font
                except IOError:
                    continue
            else:
                # Attempt 2: Fake bold effect if no bold font found
                font = ImageFont.truetype(font_path, font_size)
                # Draw text twice with slight offset for bold effect
                justify_text(draw, text, font, 11, 10, image_size[0] - 20, image_size[1])  # Offset right
                justify_text(draw, text, font, 10, 10, image_size[0] - 20, image_size[1])  # Original
                return image  # Early return since we manually drew bold text
        else:
            font = ImageFont.truetype(font_path, font_size)
    except IOError:
        print(f"Font {font_path} not found. Using default font.")
        font = ImageFont.load_default()

    justify_text(draw, text, font, 10, 10, image_size[0] - 20, image_size[1])
    return image

# Generate multiple text images
def generate_text_images(num_images, image_sizes, font="times.ttf", size=14):
    global call_count
    call_count += 1  # Increment call count for unique filenames

    base_dir = "Generation"
    text_dir = os.path.join(base_dir, "text")
    os.makedirs(text_dir, exist_ok=True)
    image_paths = []

    words = load_corpus(CORPUS_FILE)
    if not words:
        raise ValueError("Corpus file is empty or not found.")

    for i in range(num_images):
        img_size = image_sizes[i % len(image_sizes)]
        num_words = random.randint(800, 1200)
        text = " ".join(random.choices(words, k=num_words))

        img = generate_text_image(text, img_size, font, size)

        save_path = os.path.join(text_dir, f"{call_count}_{i+1}.jpg")  # Modified filename format
        img.save(save_path)
        image_paths.append(save_path)

    return image_paths

# Example usage
#image_sizes = [[391, 440], [391, 271], [380, 380], [400, 350], [600, 250], [600, 350]]
#image_paths = generate_text_images(6, image_sizes)
#print(f"Generated text images: {image_paths}")
