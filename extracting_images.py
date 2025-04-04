import json
import os
from PIL import Image
from pycocotools.coco import COCO

# Paths (Update these)
annotation_path = "path/to/train.json"
images_folder = "path/to/train-1"
output_folder = "path/to/extracted_figures"

# Load COCO annotations
coco = COCO(annotation_path)

# Get category ID for 'figure'
category_id = next((cat['id'] for cat in coco.loadCats(coco.getCatIds()) if cat['name'] == 'figure'), None)

if category_id is None:
    raise ValueError("No 'figure' category found in annotations.")

# Get image IDs containing figures
image_ids = coco.getImgIds(catIds=[category_id])
os.makedirs(output_folder, exist_ok=True)

# Process each image
for img_id in image_ids:
    img_info = coco.loadImgs(img_id)[0]
    img_path = os.path.join(images_folder, img_info['file_name'])

    if not os.path.exists(img_path):
        continue  # Skip if image is missing

    img = Image.open(img_path)

    # Get annotations for figures in this image
    ann_ids = coco.getAnnIds(imgIds=img_id, catIds=[category_id])
    annotations = coco.loadAnns(ann_ids)

    for idx, ann in enumerate(annotations):
        x, y, w, h = ann['bbox']

        # Ensure bounding box is valid
        if w <= 0 or h <= 0 or x < 0 or y < 0 or (x + w) > img.width or (y + h) > img.height:
            print(f"Skipping invalid bounding box in {img_info['file_name']}: {ann['bbox']}")
            continue  # Skip invalid bounding boxes

        cropped = img.crop((x, y, x + w, y + h))

        # Ensure cropped image is not empty
        if cropped.width == 0 or cropped.height == 0:
            print(f"Skipping empty image from {img_info['file_name']}")
            continue

        save_path = os.path.join(output_folder, f"{img_id}_{idx}.jpg")
        cropped.save(save_path)

print(f"Extraction complete! Saved images to {output_folder}.")

#21591_0.jpg haved checked