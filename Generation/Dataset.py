import os
import random
import json
import copy
from PIL import Image, ImageDraw
from Text import generate_text_images
from Image import get_random_images
from Graph import generate_graphs

# Global counter to track function calls
call_count = 0

# Paths
BASE_DIR = "dataset"
os.makedirs(BASE_DIR, exist_ok=True)

# Research paper page size
PAGE_WIDTH = 1200
PAGE_HEIGHT = 1600

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

# Initialize COCO data with a deep copy
coco_data = copy.deepcopy(coco_template)


# Function to check if a new element overlaps with existing ones
def is_overlapping(new_bbox, occupied_areas):
    new_x, new_y, new_width, new_height = new_bbox
    for area in occupied_areas:
        x, y, width, height = area
        if not (new_x + new_width < x or new_x > x + width or new_y + new_height < y or new_y > y + height):
            return True
    return False


# Function to generate random sizes for graphs (1/16 to 1/8 of the page)
def generate_random_graph_sizes(num_graphs):
    return [(random.randint(PAGE_WIDTH // 4, PAGE_WIDTH // 2),
             random.randint(PAGE_HEIGHT // 4, PAGE_HEIGHT // 2)) for _ in range(num_graphs)]


# Function to generate random sizes for images (1/4 to 1/2 of the page)
def generate_random_image_sizes(num_images):
    return [(random.randint(PAGE_WIDTH // 4, PAGE_WIDTH // 2),
             random.randint(PAGE_HEIGHT // 4, PAGE_HEIGHT // 2)) for _ in range(num_images)]


# Function to generate random text block sizes
def generate_random_text_sizes(num_texts):
    return [(PAGE_WIDTH - random.randint(80, 150), random.randint(150, 400)) for _ in range(num_texts)]


# Function to generate a research paper page
def generate_research_page(page_id):
    global call_count
    call_count += 1

    # Create a blank page
    page = Image.new("RGB", (PAGE_WIDTH, PAGE_HEIGHT), "white")
    draw = ImageDraw.Draw(page)

    # Randomize the number of elements
    num_graphs = random.randint(0, 3)
    num_images = random.randint(0, 2)
    num_text_blocks = random.randint(1, 5)  # At least one text block

    # Generate elements
    graph_sizes = generate_random_graph_sizes(num_graphs)
    graph_paths = generate_graphs(num_graphs, graph_sizes)

    image_sizes = generate_random_image_sizes(num_images)
    science_folder = "Generation/science_images"  # Replace with actual path
    non_science_folder = "Generation/non_science_images"  # Replace with actual path
    image_paths = get_random_images(num_images, image_sizes, science_folder, non_science_folder)

    text_sizes = generate_random_text_sizes(num_text_blocks)
    text_paths = generate_text_images(num_text_blocks, text_sizes)

    # Ensure only valid paths are used
    image_paths = [p for p in image_paths if os.path.exists(p)]
    graph_paths = [p for p in graph_paths if os.path.exists(p)]
    text_paths = [p for p in text_paths if os.path.exists(p)]

    # Combine all elements into a single list with their types
    elements = []
    for path, size in zip(graph_paths, graph_sizes):
        elements.append({"type": "Graph", "path": path, "size": size})
    for path, size in zip(image_paths, image_sizes):
        elements.append({"type": "Image", "path": path, "size": size})
    for path, size in zip(text_paths, text_sizes):
        elements.append({"type": "Text", "path": path, "size": size})

    # Randomize the order of elements
    random.shuffle(elements)

    # Place elements on the page
    placed_elements = []
    occupied_areas = []  # Track occupied areas to prevent overlapping

    for element in elements:
        element_type = element["type"]
        element_path = element["path"]
        element_width, element_height = element["size"]

        # Ensure the element fits within the page
        if element_width > PAGE_WIDTH - 100 or element_height > PAGE_HEIGHT - 100:
            continue  # Skip this element if it's too large

        # Try placing the element without overlapping
        max_attempts = 100  # Maximum attempts to place the element
        placed = False
        for _ in range(max_attempts):
            x_offset = random.randint(50, PAGE_WIDTH - element_width - 50)  # Leave 50px margin
            y_offset = random.randint(50, PAGE_HEIGHT - element_height - 50)  # Random y position
            new_bbox = (x_offset, y_offset, element_width, element_height)

            if not is_overlapping(new_bbox, occupied_areas):
                try:
                    element_img = Image.open(element_path)
                    page.paste(element_img, (x_offset, y_offset))
                    placed_elements.append({"type": element_type, "bbox": [x_offset, y_offset, element_width, element_height]})
                    occupied_areas.append(new_bbox)
                    placed = True
                    break  # Exit loop once placed
                except Exception as e:
                    print(f"Error loading image {element_path}: {e}")

        if not placed:
            print(f"Warning: Could not place {element_type}. Skipping...")

    # Save the page only if elements were placed
    if placed_elements:
        page_path = os.path.join(BASE_DIR, f"page_{page_id}.jpg")
        page.save(page_path)

        # Add to COCO annotations
        image_id = len(coco_data["images"]) + 1
        coco_data["images"].append({
            "id": image_id,
            "file_name": f"page_{page_id}.jpg",
            "width": PAGE_WIDTH,
            "height": PAGE_HEIGHT
        })

        for element in placed_elements:
            annotation_id = len(coco_data["annotations"]) + 1
            x, y, width, height = element["bbox"]
            coco_data["annotations"].append({
                "id": annotation_id,
                "image_id": image_id,
                "category_id": 1 if element["type"] == "Image" else 2 if element["type"] == "Graph" else 3,
                "bbox": [x, y, width, height],
                "area": width * height,
                "iscrowd": 0
            })

        return page_path

    return None  # If no elements were placed, return None


# Function to generate the dataset
def generate_dataset(num_pages):
    for page_id in range(1, num_pages + 1):
        print(f"Generating page {page_id}...")
        generate_research_page(page_id)

    # Save COCO annotations
    coco_path = os.path.join(BASE_DIR, "annotations.json")
    with open(coco_path, "w") as f:
        json.dump(coco_data, f, indent=4)

    print(f"Dataset generated with {num_pages} pages. COCO annotations saved to {coco_path}.")


# Example usage
generate_dataset(10)  # Generate 10 pages
