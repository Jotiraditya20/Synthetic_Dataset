import os
import random
from PIL import Image, ImageDraw, ImageFont
import json5

#Loading json file
def load_config(config_path):
    with open(config_path, "r") as f:
        config = json5.load(f)  # json5 allows comments
    return config
config = load_config("Generation/config.json5")

# Global counter to track function calls
call_count = 0

# Path to the corpus file
CORPUS_FILE = "Generation/corpus.txt"

# List of font paths
FONT_PATHS = config["font_paths"]


def load_corpus(corpus_file):
    """Load the corpus file and return a list of words."""
    with open(corpus_file, "r") as file:
        words = [line.strip() for line in file if line.strip()]
    return words


def wrap_text(text, font, max_width):
    """Wrap text to fit within a specified width and justify it."""
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


def justify_text(draw, text, font, x, y, max_width):
    """Draw justified text on the image."""
    lines = wrap_text(text, font, max_width)
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

        y += font.getbbox("hg")[3] - font.getbbox("hg")[1] + 10  # Increased spacing


def generate_text_image(text, image_size):
    """Generate an image with text fully embedded and justified."""
    image = Image.new("RGB", image_size, "white")
    draw = ImageDraw.Draw(image)

    font_path = random.choice(FONT_PATHS) # Paths
    font_size = random.randint(config["min_font_size"], config["max_font_size"])  #font size range
    
    try:
        font = ImageFont.truetype(font_path, font_size)
    except IOError:
        print(f"Font {font_path} not found. Using default font.")
        font = ImageFont.load_default()

    justify_text(draw, text, font, 10, 10, image_size[0] - 30)

    return image


def generate_text_images(num_images, image_sizes):
    global call_count
    call_count += 1
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

        img = generate_text_image(text, img_size)

        save_path = os.path.join(text_dir, f"{call_count}_{i+1}.jpg")
        img.save(save_path)
        image_paths.append(save_path)

    return image_paths


# Example usage
#image_sizes = [[400, 200], [500, 300], [600, 400], [800, 600], [1000, 800]]
#image_paths = generate_text_images(5, image_sizes)
#print(f"Generated text images: {image_paths}")