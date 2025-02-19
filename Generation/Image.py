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

def get_random_images(num_images, image_sizes, science_folder="Generation/science_images", non_science_folder="Generation/non_science_images"):
    global call_count
    call_count += 1
    base_dir = "Generation"
    image_dir = os.path.join(base_dir, "image")
    os.makedirs(image_dir, exist_ok=True)
    image_paths = []

    # Get lists of science and non-science images
    science_images = [os.path.join(science_folder, f) for f in os.listdir(science_folder) if f.endswith(('.jpg', '.png', '.jpeg'))]
    non_science_images = [os.path.join(non_science_folder, f) for f in os.listdir(non_science_folder) if f.endswith(('.jpg', '.png', '.jpeg'))]

    # Ensure there are enough images in the folders
    if not science_images:
        raise ValueError("No science images found in the specified folder.")
    if not non_science_images:
        raise ValueError("No non-science images found in the specified folder.")

    for i in range(num_images):
        # Decide whether to pick a science or non-science image (90% science, 10% non-science)
        if random.random() < config["split"]:
            image_path = random.choice(science_images)
        else:
            image_path = random.choice(non_science_images)

        # Open the image
        img = Image.open(image_path)

        # Get target size and define extra space for text (fixed at 20px)
        target_width, target_height = image_sizes[i % len(image_sizes)]  # Cycle through sizes
        text_height = 20
        resized_height = target_height - text_height  # Image height before adding text

        # Resize image first
        img = img.resize((target_width, resized_height), Image.LANCZOS)

        # Create a new image with extra space for text
        new_img = Image.new("RGB", (target_width, target_height), "white")
        new_img.paste(img, (0, 0))

        # Draw text in the extra space
        draw = ImageDraw.Draw(new_img)
        fig_id = config["text_id"].format(call_count=call_count, index = i+1)

        # Load font
        try:
            font = ImageFont.truetype("arial.ttf", 14)  # Fixed font size
        except IOError:
            font = ImageFont.load_default()

        # Center the text horizontally
        text_width, text_height = draw.textsize(fig_id, font=font)
        text_x = ((target_width - text_width) // 2) + config["text_x_pos"]
        text_y = resized_height + (text_height // 2) + config["text_y_pos"] # Place in the extra space

        draw.text((text_x, text_y), fig_id, fill="black", font=font)

        # Save the final image
        save_path = os.path.join(image_dir, f"{call_count}_{i+1}.jpg")
        new_img.save(save_path)
        image_paths.append(save_path)

    return image_paths

# Example usage
#science_folder = "Generation/science_images"
#non_science_folder = "Generation/non_science_images"
#image_sizes = [[300, 300], [400, 400], [500, 500], [600, 600]]
#image_paths = get_random_images(5, image_sizes, science_folder, non_science_folder)
#print(f"Generated images: {image_paths}")
