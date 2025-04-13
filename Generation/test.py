import json
import os
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from PIL import Image

# Load COCO JSON file
coco_path = "dataset1/annotations.json"  # Change this to your COCO file path
image_dir = "dataset1"  # Change this to your image folder

with open(coco_path, "r") as f:
    coco_data = json.load(f)

# Create a mapping of image IDs to file names
image_id_to_filename = {img["id"]: img["file_name"] for img in coco_data["images"]}

# Function to visualize an image with annotations
def visualize_annotations(image_id):
    if image_id not in image_id_to_filename:
        print(f"Image ID {image_id} not found in annotations.")
        return

    image_file = os.path.join(image_dir, image_id_to_filename[image_id])
    image = Image.open(image_file)
    
    # Create a figure and axes
    fig, ax = plt.subplots(1, figsize=(8, 8))
    ax.imshow(image)

    # Get all annotations for this image
    annotations = [ann for ann in coco_data["annotations"] if ann["image_id"] == image_id]

    # Plot each bounding box
    for ann in annotations:
        bbox = ann["bbox"]  # [x, y, width, height]
        x, y, w, h = bbox
        rect = patches.Rectangle((x, y), w, h, linewidth=2, edgecolor="red", facecolor="none")
        ax.add_patch(rect)
        category_id = ann["category_id"]
        category_name = next((cat["name"] for cat in coco_data["categories"] if cat["id"] == category_id), "Unknown")
        ax.text(x, y - 5, category_name, color="red", fontsize=12, bbox=dict(facecolor="white", alpha=0.5))

    plt.show()

# Example: Visualize annotations for image_id = 0
visualize_annotations(image_id = 0)  # Change this to any valid image ID
