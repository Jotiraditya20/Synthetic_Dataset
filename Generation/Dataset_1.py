import os
import random
import json
from PIL import Image, ImageDraw
from Text import generate_text_images
from Image import get_random_images
from Graph import generate_graphs

# Paths
BASE_DIR = "dataset"
os.makedirs(BASE_DIR, exist_ok=True)

# Research paper page size
PAGE_WIDTH = 1200
PAGE_HEIGHT = 1600
MARGIN = 50  # Margin around elements
NUM_PARTS = 3  # Number of horizontal sections

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

def check_overlap(x, y, w, h, elements):
    """Checks if a new element overlaps with any previously placed elements."""
    for elem in elements:
        ex, ey, ew, eh = elem["bbox"]
        if not (x + w <= ex or ex + ew <= x or y + h <= ey or ey + eh <= y or x - w >= ex + ew or y - w >= ey + eh):
            return True  # Overlap detected
    return False

def generate_research_page(page_id):
    """Generates a research paper-style page with images, graphs, and text blocks, using randomized offsets."""
    
    page = Image.new("RGB", (PAGE_WIDTH, PAGE_HEIGHT), "white")
    draw = ImageDraw.Draw(page)
    
    part_height = (PAGE_HEIGHT - 2 * MARGIN) // NUM_PARTS
    elements = []
    coco_annotations = []
    image_id = len(coco_data["images"]) + 1
    
    for part in range(NUM_PARTS):
        upper_limit = MARGIN + part * part_height
        lower_limit = upper_limit + part_height - MARGIN
        left_limit = MARGIN
        
        while left_limit < PAGE_WIDTH - MARGIN:
            #Image : 0 Text: 1 Graph: 2
            element_type = random.choices([0, 1, 2], weights=[30, 50, 20])[0]

            # Generate random width and height
            if element_type == 0:  # Image
                width = random.randint(200, 400)
                height = random.randint(200, part_height - 20)
            elif element_type == 1:  # Text
                width = random.randint(300, 600)
                height = random.randint(100, part_height - 30)
            else:  # Graph
                width = random.randint(250, 450)
                height = random.randint(250, part_height - 30)

            if left_limit + width + MARGIN > PAGE_WIDTH:
                break  # No more space in this row, move to next part

            # Randomize height offset (ensuring it stays within part limits)
            height_offset = random.randint(-20, 20)  # Slight vertical variation
            y_position = min(max(upper_limit + height_offset, upper_limit), lower_limit - height)

            # Randomize left offset (slight left-right shifting)
            left_offset = random.randint(-15, 15)
            x_position = max(left_limit + left_offset, MARGIN)

            # Ensure no overlap
            while check_overlap(x_position, y_position, width, height, elements):
                x_position += 10  # Shift right until no overlap
                if x_position + width > PAGE_WIDTH - MARGIN:
                    break  # Avoid going out of bounds

            if x_position + width > PAGE_WIDTH - MARGIN:
                break  # No more space

            # Generate element
            try:
                if element_type == 0:
                    image_path = get_random_images(1, [(width, height)], "Generation/science_images",
                                                   "Generation/non_science_images")[0]
                elif element_type == 1:
                    image_path = generate_text_images(1, [(width, height)])[0]
                else:
                    image_path = generate_graphs(1, [(width, height)])[0]

                if not os.path.exists(image_path):
                    continue  # Skip invalid images

                # Store placement details
                elements.append({
                    "type": element_type,
                    "path": image_path,
                    "bbox": (x_position, y_position, width, height)
                })

                # Move to next position
                left_limit = x_position + width + random.randint(10, 30)

            except Exception as e:
                print(f"Error generating element: {e}")
                continue

    # Place elements on the page
    for elem in elements:
        try:
            img = Image.open(elem["path"])
            page.paste(img, (elem["bbox"][0], elem["bbox"][1]))

            # Add COCO annotation
            coco_annotations.append({
                "id": len(coco_data["annotations"]) + 1,
                "image_id": image_id,
                "category_id": 1 if elem["type"] == 0 else 2 if elem["type"] == 2 else 3,
                "bbox": list(elem["bbox"]),
                "area": elem["bbox"][2] * elem["bbox"][3],
                "iscrowd": 0
            })
        except Exception as e:
            print(f"Error placing element {elem['path']}: {e}")

    # Save the page
    page_path = os.path.join(BASE_DIR, f"page_{page_id}.jpg")
    page.save(page_path)

    # Update COCO dataset
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

    # Save COCO annotations
    coco_path = os.path.join(BASE_DIR, "annotations.json")
    with open(coco_path, "w") as f:
        json.dump(coco_data, f, indent=4)

    print(f"Dataset generated with {num_pages} pages. COCO annotations saved to {coco_path}.")

# Generate dataset
generate_dataset(10)  # Adjust the number of pages as needed