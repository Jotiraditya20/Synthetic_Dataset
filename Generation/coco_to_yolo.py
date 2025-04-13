import json
import os
import shutil

# Paths
COCO_JSON = "dataset/annotations.json"
DATASET_FOLDER = "dataset"  # Folder where images are originally stored
OUTPUT_FOLDER = "atraining"

# Create necessary folders
os.makedirs(f"{OUTPUT_FOLDER}/train/images", exist_ok=True)
os.makedirs(f"{OUTPUT_FOLDER}/train/labels", exist_ok=True)

# Load COCO JSON
with open(COCO_JSON, "r") as f:
    data = json.load(f)

# Get category mapping
category_map = {category["id"]: category["name"] for category in data["categories"]}

# Process annotations
image_annotations = {img["id"]: [] for img in data["images"]}

for ann in data["annotations"]:
    img_id = ann["image_id"]
    category_id = ann["category_id"]
    bbox = ann["bbox"]  # [x_min, y_min, width, height]

    # Get image width & height
    img_info = next(img for img in data["images"] if img["id"] == img_id)
    img_w, img_h = img_info["width"], img_info["height"]

    # Convert bbox to YOLO format
    x_min, y_min, box_w, box_h = bbox
    x_center = (x_min + box_w / 2) / img_w
    y_center = (y_min + box_h / 2) / img_h
    box_w /= img_w
    box_h /= img_h

    # Append annotation
    image_annotations[img_id].append(f"{category_id} {x_center:.6f} {y_center:.6f} {box_w:.6f} {box_h:.6f}")

# Write YOLO label files and move images
for img in data["images"]:
    image_name = img["file_name"]
    label_name = os.path.splitext(image_name)[0] + ".txt"

    # Move image to training folder
    src_path = os.path.join(DATASET_FOLDER, image_name)
    dst_path = os.path.join(OUTPUT_FOLDER, "train/images", image_name)
    if os.path.exists(src_path):
        shutil.copy(src_path, dst_path)

    # Write label file
    with open(os.path.join(OUTPUT_FOLDER, "train/labels", label_name), "w") as f:
        f.write("\n".join(image_annotations[img["id"]]))

print("✅ Conversion complete! YOLO annotations are in 'training/labels/train' and images are in 'training/images/train'.")