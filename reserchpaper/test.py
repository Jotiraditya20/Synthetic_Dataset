import os
from PIL import Image, ImageDraw, ImageFont

# Page settings
PAGE_WIDTH = 900
PAGE_HEIGHT = 1200

# Image paths
TEXT_1_PATH = "Generation/text/1_1.jpg"
TEXT_2_PATH = "Generation/text/1_2.jpg"
TEXT_3_PATH = "Generation/text/1_3.jpg"
TEXT_4_PATH = "Generation/text/1_4.jpg"
GRAPH_1_PATH = "reserchpaper/images/1/graph1_1.png"
GRAPH_2_PATH = "reserchpaper/images/1/graph1_2.png"

def resize_image_keep_aspect(image_path, width, height):
    """Resizes an image to exact dimensions."""
    image = Image.open(image_path).resize((width, height), Image.LANCZOS)
    return image

def generate_research_page():
    page = Image.new("RGB", (PAGE_WIDTH, PAGE_HEIGHT), "white")
    draw = ImageDraw.Draw(page)

    # Load and place text sections
    text1 = resize_image_keep_aspect(TEXT_1_PATH, 391, 440)
    text2 = resize_image_keep_aspect(TEXT_2_PATH, 391, 271)
    text3 = resize_image_keep_aspect(TEXT_3_PATH, 380, 380)
    text4 = resize_image_keep_aspect(TEXT_4_PATH, 400, 350)
    page.paste(text1, (70, 420))
    page.paste(text2, (70, 878))
    page.paste(text3, (470, 420))
    page.paste(text4, (470, 800))

    # Load and place images
    graph1 = resize_image_keep_aspect(GRAPH_1_PATH, 350, 300)
    graph2 = resize_image_keep_aspect(GRAPH_2_PATH, 370, 300)
    
    page.paste(graph1, (100, 100))
    page.paste(graph2, (450, 100))
   

    # Save the final page
    output_path = "reserchpaper/gen images/1.png"
    page.save(output_path)
    print(f"Research page saved at {output_path}")

# Generate the research page
generate_research_page()