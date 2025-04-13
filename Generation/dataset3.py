import os
import random
import json
from PIL import Image, ImageDraw, ImageFont
from Text import generate_text_images
from Image import get_random_images
from Graph1 import generate_graphs
import json5
from PIL import Image, ImageFilter, ImageDraw, ImageCms, ImageEnhance
import tempfile

graph_counter = 0
# Using for id in coco
page_count = 0
elem_count = 0
fig_count = 1  # Global figure counter for captions

try:
    with open('Generation/corpus.txt', 'r') as f:
        corpus_words = [line.strip() for line in f if line.strip()]
except Exception:
    corpus_words = ["Time", "Measurement", "Experiment", "Data", "Result"]

if not corpus_words:
    corpus_words = ["Time", "Measurement", "Experiment", "Data", "Result"]

def apply_digital_artifacts(page, page_id):
    """Digital-born PDF processing with error handling"""
    try:
        # Convert to RGB first
        page = page.convert("RGB")
        
        # 1. Safe anti-aliasing
        page = page.filter(ImageFilter.SMOOTH_MORE)

        # 2. Pixel noise with bounds checking
        pixels = page.load()
        for _ in range(int(0.002 * page.width * page.height)):
            x = random.randint(0, page.width-1)
            y = random.randint(0, page.height-1)
            r, g, b = pixels[x, y]
            pixels[x, y] = (
                min(255, max(0, r + random.randint(-3, 3))),
                min(255, max(0, g + random.randint(-3, 3))),
                min(255, max(0, b + random.randint(-3, 3)))
            )

        # 3. Safer PDF render simulation
        if random.random() < 0.4:
            page = page.transform(
                page.size,
                Image.AFFINE,
                data=(1, random.uniform(-0.02, 0.02), 0,
                      random.uniform(-0.02, 0.02), 1, 0),
                resample=Image.BILINEAR
            )

        # 4. CMS handling with fallback
        try:
            if random.random() < 0.5:  # 50% chance
                srgb_profile = ImageCms.createProfile("sRGB")
                page = ImageCms.profileToProfile(
                    page, 
                    srgb_profile, 
                    srgb_profile,  # Same profile = safe transform
                    outputMode="RGB"
                )
        except Exception as cms_error:
            print(f"Color profile error: {cms_error}")

        # 5. JPEG compression fallback
        try:
            with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmp:
                page.save(tmp.name, quality=random.randint(85, 95))
                tmp.close()  # Explicitly close before reopening
                page = Image.open(tmp.name).convert("RGB")
            os.unlink(tmp.name)  # Delete after processing
        except Exception as compression_error:
            print(f"Compression failed: {compression_error}")

        # 6. Final adjustments
        enhancer = ImageEnhance.Sharpness(page)
        return enhancer.enhance(random.uniform(0.95, 1.05))

    except Exception as e:
        print(f"Artifact pipeline failed: {e}")
        return page  # Return original if errors occur

# Loading json file




def load_config(config_path):
    with open(config_path, "r") as f:
        config = json5.load(f)  # json5 allows comments
    return config
config = load_config("./Generation/dataset3_config.json5")

# Paths
BASE_DIR = "dataset"
os.makedirs(BASE_DIR, exist_ok=True)

# Research paper page size
PAGE_WIDTH = config["PAGE_WIDTH"]
PAGE_HEIGHT = config["PAGE_HEIGHT"]
MARGIN = config["MARGIN"]

coco_template = config["coco_template"]
coco_data = coco_template.copy()

# Adds images to the coco data
def add_image(image_id, file_name, width, height):
    coco_data["images"].append({
        "id": image_id,
        "file_name": file_name,
        "width": width,
        "height": height,
        "license": 1,
        "date_captured": "2025-02-27T00:00:00+00:00"
    })
# Adds annotations to the coco data
def add_annotation(annotation_id, image_id, category_id, bbox):
    x, y, w, h = bbox
    area = w * h  # Calculate area
    coco_data["annotations"].append({
        "id": annotation_id,
        "image_id": image_id,
        "category_id": category_id,
        "bbox": bbox,
        "area": area,
        "segmentation": [],
        "iscrowd": 0
    })
# Generates research paper rows
def row_generater(PAGE_HEIGHT=PAGE_HEIGHT, min=300, max=500, MARGIN=50):
    rows = [MARGIN]
    while rows[-1] < PAGE_HEIGHT - MARGIN:
        next_row = random.randint(min, max) + rows[-1]
        if next_row > PAGE_HEIGHT - MARGIN:
            next_row = PAGE_HEIGHT - MARGIN
        rows.append(next_row)
    return rows

# Generates single columns for text and n columns for graph and images
# --- Changes inside generate_research_page_N_columns ---

def generate_research_page_N_columns(page_id, n=config["N"]):
    global page_count, elem_count, fig_count, corpus_words, graph_counter
    # Blank Page
    page = Image.new("RGB", (PAGE_WIDTH, PAGE_HEIGHT), "white")
    draw = ImageDraw.Draw(page)

    # Generates Rows Randomly for each column
    rowss = []
    for i in range(0, n):
        row = row_generater(PAGE_HEIGHT, config["min_row"], config["max_row"], MARGIN)
        rowss.append(row)

    # Font for the page
    fonts = config["Fonts"]
    font_path = random.choice(fonts)
    font_size = random.randint(config["min_font_size"], config["max_font_size"])
    font_bold = random.randint(30, 40)

    # Elements to store all elements
    elements = []

    # COCO Annotations
    image_id = f"page_{page_id}.jpg"
    add_image(page_count, image_id, config["PAGE_WIDTH"], config["PAGE_HEIGHT"])

    # Iterate over columns and rows
    for j in range(0, n):
        rows = rowss[j]
        for i in range(1, len(rows)):
            ROW_HEIGHT = rows[i] - rows[i - 1]
            ROW_WIDTH = (PAGE_WIDTH - (2 * MARGIN) - (n * config["col_offset"])) // n
            HEIGHT_LIMITS = [rows[i - 1], rows[i]]
            WIDTH_LIMITS = [MARGIN + (j * ROW_WIDTH) + (j * config["col_offset"]),
                            MARGIN + ((j + 1) * ROW_WIDTH)]
            # 0 is image/graph and 2 is text
            chosen_type = random.choices(['image', 'text'], weights=config["weights"])[0]

            bold = False
            if ROW_HEIGHT < 150:
                chosen_type = 'text'
                bold = random.choices([True, False], weights=[70, 30])[0]

            if chosen_type == "image":  # Picture/Graph block
                width_left = ROW_WIDTH

                # Reserve space for caption by reducing available height for the graphic.
                # For example, let’s reserve ~25 pixels for captions.
                caption_reserved = 25
                effective_height = ROW_HEIGHT - caption_reserved

                if config["same_size"] == 1 and config["square"] == 1:
                    pic_height = random.randint(min(effective_height, config["min_pic_height"]),
                                                min(effective_height, config["max_pic_height"]))
                    pic_width = pic_height
                elif config["same_size"] == 1 and config["square"] != 1:
                    pic_height = random.randint(min(effective_height, config["min_pic_height"]),
                                                min(effective_height, config["max_pic_height"]))
                    pic_width = random.randint(min(ROW_WIDTH, config["min_pic_width"]),
                                               min(ROW_WIDTH, config["max_pic_width"]))
                else:
                    print("Invalid Config")
                    break

                while width_left > 0:
                    # If not same size or square, recalculate dimensions for variability.
                    if config["same_size"] != 1 and config["square"] == 1:
                        pic_height = random.randint(min(effective_height, config["min_pic_height"]),
                                                    min(effective_height, config["max_pic_height"]))
                        pic_width = pic_height
                    elif config["same_size"] != 1 and config["square"] != 1:
                        pic_height = random.randint(min(effective_height, config["min_pic_height"]),
                                                    min(effective_height, config["max_pic_height"]))
                        pic_width = random.randint(min(ROW_WIDTH, config["min_pic_width"]),
                                                   min(ROW_WIDTH, config["max_pic_width"]))
                    pos_possible_vertical = effective_height - pic_height
                    pos_possible_horizontal = WIDTH_LIMITS[0] + ROW_WIDTH - width_left
                    if config["offset"] == 1:
                        y_pos = HEIGHT_LIMITS[0] + random.randint(0, pos_possible_vertical)
                        x_pos = pos_possible_horizontal
                        width_left -= pic_width
                        if width_left < 0:
                            break
                    elif config["offset"] == 2:
                        print("Implementation Phase")
                    else:
                        y_pos = HEIGHT_LIMITS[0]
                        x_pos = pos_possible_horizontal
                        width_left -= pic_width
                        if width_left < 0:
                            break

                    # Decide between image and graph
                    pic_type = random.choices(['image', 'graph'], weights=config["pic_weights"])[0]
                    if pic_type == 'image':
                        element_type = 1
                        image_path = get_random_images(num_images=1, image_sizes=[(pic_width, pic_height)],
                                                       science_folder="Generation/science_images",
                                                       non_science_folder="Generation/non_science_images")[0]
                        caption_size = 20
                    else:
                        element_type = 0
                        image_path = generate_graphs(1, [(pic_width, pic_height)])[0]
                        graph_counter += 1
                        caption_size = 25

                    # Append the image/graph element
                    elements.append({
                        "type": element_type,
                        "path": image_path,
                        "bbox": (x_pos, y_pos, pic_width, pic_height-caption_size)
                    })
                    elements.append({
                        "type": 2,
                        "path": None,
                        "bbox": (x_pos, y_pos + pic_height - caption_size, pic_width, caption_size)
                    })

            elif chosen_type == "text":  # Text element block
                element_type = 2
                text_height = random.randint(ROW_HEIGHT - config["min_hieght_reduce1"],
                                             ROW_HEIGHT - config["max_hieght_reduce1"])
                text_width = random.randint(ROW_WIDTH - config["min_width_reduce1"],
                                            ROW_WIDTH - config["max_width_reduce1"])
                pos_possible_vertical = ROW_HEIGHT - text_height
                pos_possible_horizontal = ROW_WIDTH - text_width
                if config["offset"] == 1:
                    y_pos = HEIGHT_LIMITS[0] + random.randint(0, pos_possible_vertical)
                    x_pos = WIDTH_LIMITS[0] + random.randint(0, pos_possible_horizontal)
                elif config["offset"] == 2:
                    print("Implementation Phase")
                else:
                    y_pos = HEIGHT_LIMITS[0]
                    x_pos = WIDTH_LIMITS[0]
                try:
                    if not bold:
                        image_path = generate_text_images(1, [(text_width, text_height)],
                                                           font_path, font_size, bold=False)[0]
                    else:
                        image_path = generate_text_images(1, [(text_width, text_height)],
                                                           font_path, font_bold, bold=True)[0]
                except Exception as e:
                    print(f"Error generating Text element: {e}")
                    continue
                elements.append({
                    "type": element_type,
                    "path": image_path,
                    "bbox": (x_pos, y_pos, text_width, text_height)
                })
            else:
                print("Invalid Type")

    # Adding page number element (as text) at the end
    if config["page_number_position"] == "right":
        x_min = PAGE_WIDTH - 100
        y_min = PAGE_HEIGHT - MARGIN
        elements.append(generate_page_number_image(page_id, x_min, y_min, font_size=14, font_path=font_path))

    # --- NEW: Sort elements to ensure text elements (type 2) are pasted last ---
    # Sorting by type ensures that image/graph elements are drawn before text elements
    elements = sorted(elements, key=lambda e: e["type"])

    # Add all elements to the page and update the coco file
    for elem in elements:
        try:
            if elem["path"] !=None:
                img = Image.open(elem["path"])
                page.paste(img, (elem["bbox"][0], elem["bbox"][1]))
            add_annotation(elem_count, page_count, elem["type"], elem["bbox"])
            elem_count += 1
        except Exception as e:
            print(f"Error placing element {elem['path']}: {e}")

    # Save the page
    page_path = os.path.join(BASE_DIR, f"page_{page_id}.jpg")
    processed_page = apply_digital_artifacts(page, page_id)
    page_path = os.path.join(BASE_DIR, f"page_{page_id}.jpg")
    processed_page.save(page_path, quality=100, subsampling=0, dpi=(300, 300))
    page_count += 1

def generate_page_number_image(page_number, x_min, y_min, font_size=30, font_path="arial.ttf",
                               text_color="black", bg_color="white", output_dir="Generation/page"):
    text = f"Page {page_number}"
    try:
        font = ImageFont.truetype(font_path, font_size)
    except IOError:
        font = ImageFont.load_default()  # Fallback if font is missing
    dummy_img = Image.new("RGB", (1, 1))
    draw = ImageDraw.Draw(dummy_img)
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width, text_height = bbox[2] - bbox[0], bbox[3] - bbox[1]
    img = Image.new("RGB", (text_width + 20, text_height + 10), bg_color)  # Add padding
    draw = ImageDraw.Draw(img)
    draw.text((10, 5), text, fill=text_color, font=font)
    os.makedirs(output_dir, exist_ok=True)
    image_path = os.path.join(output_dir, f"page_number_{page_number}.jpg")
    img.save(image_path)
    img_size = img.size
    return {"type": 2,
            "path": image_path,
            "bbox": (x_min, y_min, img_size[0], img_size[1])
            }

def generate_dataset(num_pages):
    """Generates a dataset of research paper-style images."""
    for page_id in range(1, num_pages + 1):
        N = 2
        print(f"Generating page {page_id}...")
        generate_research_page_N_columns(page_id, n=(page_id % N) + 1)
    coco_path = os.path.join(BASE_DIR, "annotations.json")
    with open(coco_path, "w") as f:
        json.dump(coco_data, f, indent=4)
    print(f"Dataset generated with {num_pages} pages. COCO annotations saved to {coco_path}.")

generate_dataset(5000)
