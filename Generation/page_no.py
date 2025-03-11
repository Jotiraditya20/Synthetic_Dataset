import os
from PIL import Image, ImageDraw, ImageFont

def generate_page_number_image(page_number, font_size=30, font_path="arial.ttf", text_color="black", bg_color="white", output_dir="Generation/page"):

    text = f"Page No {page_number}"

    try:
        font = ImageFont.truetype(font_path, font_size)
    except IOError:
        font = ImageFont.load_default()  # Fallback if font is missing

    # Determine text size using textbbox (new in Pillow 10)
    dummy_img = Image.new("RGB", (1, 1))
    draw = ImageDraw.Draw(dummy_img)
    bbox = draw.textbbox((0, 0), text, font=font)  # (x_min, y_min, x_max, y_max)
    text_width, text_height = bbox[2] - bbox[0], bbox[3] - bbox[1]

    # Create an image with appropriate size
    img = Image.new("RGB", (text_width + 20, text_height + 10), bg_color)  # Add padding
    draw = ImageDraw.Draw(img)

    # Draw text in the center
    draw.text((10, 5), text, fill=text_color, font=font)

    # Ensure the output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Save the image
    image_path = os.path.join(output_dir, f"page_number_{page_number}.jpg")
    img.save(image_path)

    return image_path

# Example usage
page_image_path = generate_page_number_image(1)
print(f"Page number image saved at: {page_image_path}")
