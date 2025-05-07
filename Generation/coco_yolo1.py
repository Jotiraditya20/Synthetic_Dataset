import json
import os
import shutil

# Configuration
COCO_JSON = "dataset/annotations.json"
DATASET_FOLDER = "dataset"
OUTPUT_FOLDER = "atraining"  

# Create output folders
os.makedirs(f"{OUTPUT_FOLDER}/images/train", exist_ok=True)
os.makedirs(f"{OUTPUT_FOLDER}/labels/train", exist_ok=True)

# Load COCO annotations
with open(COCO_JSON, "r") as f:
    data = json.load(f)

# Create image lookup and category map
image_info = {img["id"]: img for img in data["images"]}
category_map = {category["id"]: category["name"] for category in data["categories"]}

# Process all annotations
image_annotations = {img_id: [] for img_id in image_info}

for ann in data["annotations"]:
    img_id = ann["image_id"]
    category_id = ann["category_id"]
    bbox = ann["bbox"]  # COCO format: [x_min, y_min, width, height]
    
    # Get image dimensions
    img_w = image_info[img_id]["width"]
    img_h = image_info[img_id]["height"]
    
    # Convert to YOLO format (normalized center coordinates and dimensions)
    x_center = (bbox[0] + bbox[2] / 2) / img_w
    y_center = (bbox[1] + bbox[3] / 2) / img_h
    width = bbox[2] / img_w
    height = bbox[3] / img_h
    
    # Store annotation
    image_annotations[img_id].append(f"{category_id} {x_center:.6f} {y_center:.6f} {width:.6f} {height:.6f}")

# Save images and labels
for img_id, annotations in image_annotations.items():
    img_data = image_info[img_id]
    image_name = img_data["file_name"]
    base_name = os.path.splitext(image_name)[0]
    
    # Copy image
    src_path = os.path.join(DATASET_FOLDER, image_name)
    dst_path = os.path.join(OUTPUT_FOLDER, "images/train", image_name)
    if os.path.exists(src_path):
        shutil.copy(src_path, dst_path)
    else:
        print(f"Warning: Image not found at {src_path}")
        continue
    
    # Write label file (only if there are annotations)
    if annotations:
        label_path = os.path.join(OUTPUT_FOLDER, "labels/train", f"{base_name}.txt")
        with open(label_path, "w") as f:
            f.write("\n".join(annotations))

print(f"✅ Conversion complete! YOLO annotations are in '{OUTPUT_FOLDER}/labels/train' and images are in '{OUTPUT_FOLDER}/images/train'.")
print(f"Categories used: {category_map}")