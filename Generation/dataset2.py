import os
import random
import json
from PIL import Image, ImageDraw
from Text import generate_text_images
from Image import get_random_images
from Graph import generate_graphs
import json5

#Loading json file
def load_config(config_path):
    with open(config_path, "r") as f:
        config = json5.load(f)  # json5 allows comments
    return config
config = load_config("Generation/config.json5")

# Paths
BASE_DIR = "dataset"
os.makedirs(BASE_DIR, exist_ok=True)

# Research paper page size
PAGE_WIDTH = 1200
PAGE_HEIGHT = 1600
MARGIN = config["margin"]  # Margin around elements
NUM_ROWS = config["row"]  # Number of horizontal sections
NUM_COLUMNS = config["col"]  # Number of vertical sections

# COCO format template
coco_template = {
    "info": {},
    "licenses": [],
    "images": [],
    "annotations": [],
    "categories": [
        {"id": 1, "name": "Image"},
        {"id": 2, "name": "Graph"},
        {"id": 3, "name": "Text"}
    ]
}

# Initialize COCO data
coco_data = coco_template.copy()

def generate_research_page(page_id):
    """Generates a research paper-style page with a shadow effect, images, graphs, and text blocks."""
    
    shadow_offset = config["shadow_offset"]  # Offset for shadow
    shadow_color = tuple(config["shadow_color"]) # Light gray shadow

    # Create a new image with extra space for the shadow
    page = Image.new("RGB", (PAGE_WIDTH + shadow_offset, PAGE_HEIGHT + shadow_offset), "white")
    draw = ImageDraw.Draw(page)

    # Draw shadow
    shadow_position = (shadow_offset, shadow_offset, PAGE_WIDTH + shadow_offset, PAGE_HEIGHT + shadow_offset)
    draw.rectangle(shadow_position, fill=shadow_color)

    # Draw the main page over the shadow
    page_position = (0, 0, PAGE_WIDTH, PAGE_HEIGHT)
    draw.rectangle(page_position, fill="white")
    
    row_height = (PAGE_HEIGHT - 2 * MARGIN) // NUM_ROWS
    col_width = (PAGE_WIDTH - 2 * MARGIN) // NUM_COLUMNS
    elements = []
    coco_annotations = []
    image_id = len(coco_data["images"]) + 1
    
    for row in range(NUM_ROWS):
        for col in range(NUM_COLUMNS):
            x_position = MARGIN + col * col_width + random.randint(-20, 20)
            y_position = MARGIN + row * row_height + random.randint(-20, 20)
            
            element_type = random.choices([0, 1, 2], weights=[30, 50, 20])[0]
            width = random.randint(200, col_width - 20)
            height = random.randint(200, row_height - 20)

            try:
                if element_type == 0:
                    image_path = get_random_images(1, [(width, height)], "Generation/science_images", "Generation/non_science_images")[0]
                elif element_type == 1:
                    image_path = generate_text_images(1, [(width, height)])[0]
                else:
                    image_path = generate_graphs(1, [(width, height)])[0]

                if not os.path.exists(image_path):
                    print(f"Skipping invalid image path: {image_path}")
                    continue
                
                img = Image.open(image_path)
                img = img.resize((width, height))
                page.paste(img, (x_position, y_position))

                elements.append({
                    "type": element_type,
                    "path": image_path,
                    "bbox": (x_position, y_position, width, height)
                })

                coco_annotations.append({
                    "id": len(coco_data["annotations"]) + 1,
                    "image_id": image_id,
                    "category_id": 1 if element_type == 0 else 2 if element_type == 2 else 3,
                    "bbox": list((x_position, y_position, width, height)),
                    "area": width * height,
                    "iscrowd": 0
                })
            except Exception as e:
                print(f"Error processing element: {e}")
                continue

    page_path = os.path.join(BASE_DIR, f"page_{page_id}.jpg")
    page.save(page_path)
    
    coco_data["images"].append({
        "id": image_id,
        "file_name": f"page_{page_id}.jpg",
        "width": PAGE_WIDTH,
        "height": PAGE_HEIGHT
    })
    coco_data["annotations"].extend(coco_annotations)

def generate_dataset(num_pages):
    """Generates a dataset of research paper-style images."""
    for page_id in range(1, num_pages + 1):
        print(f"Generating page {page_id}...")
        generate_research_page(page_id)
    
    coco_path = os.path.join(BASE_DIR, "annotations.json")
    with open(coco_path, "w") as f:
        json.dump(coco_data, f, indent=4)
    
    print(f"Dataset generated with {num_pages} pages. COCO annotations saved to {coco_path}.")

# Generate dataset
generate_dataset(10)  # Adjust the number of pages as needed
