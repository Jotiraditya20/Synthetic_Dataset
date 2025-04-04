import os
import random
import json
from PIL import Image, ImageDraw, ImageFont
from Text import generate_text_images
from Image import get_random_images
from Graph import generate_graphs
import json5

#Using for id in coco
page_count = 0
elem_count = 0

#Loading json file
def load_config(config_path):
    with open(config_path, "r") as f:
        config = json5.load(f)  # json5 allows comments
    return config
config = load_config("Generation/dataset3_config.json5")

# Paths
BASE_DIR = "dataset"
os.makedirs(BASE_DIR, exist_ok=True)

# Research paper page size
PAGE_WIDTH = config["PAGE_WIDTH"]
PAGE_HEIGHT = config["PAGE_HEIGHT"]
MARGIN = config["MARGIN"]

coco_template = config["coco_template"]
coco_data = coco_template.copy()

#Adds images to the coco data
def add_image(image_id, file_name, width, height):
    coco_data["images"].append({
        "id": image_id,
        "file_name": file_name,
        "width": width,
        "height": height,
        "license": 1,
        "date_captured": "2025-02-27T00:00:00+00:00"
    })
#Adds Annotations to the coco data
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
# generates research paper rows
def row_generater(PAGE_HEIGHT = PAGE_HEIGHT, min = 300, max = 500, MARGIN = 50):
    rows = [MARGIN]
    while(rows[-1] < PAGE_HEIGHT - MARGIN):
        next = random.randint(min, max) + rows[-1]
        if next > PAGE_HEIGHT - MARGIN:
            next = PAGE_HEIGHT - MARGIN
        rows.append(next)
    #print("Rows:", end = " ")
    #print(rows)
    return rows

#Generates Single columns for text and n columns for graph and images
def generate_research_page_single(page_id):
    global page_count
    global elem_count
    #Blank Page
    page = Image.new("RGB", (PAGE_WIDTH, PAGE_HEIGHT), "white")
    draw = ImageDraw.Draw(page)

    #Generates Rows Randomly
    rows = row_generater(PAGE_HEIGHT, config["min_row"], config["max_row"], MARGIN)

    #Font for the page
    fonts = config["Fonts"]
    font_path = random.choice(fonts)
    font_size = random.randint(config["min_font_size"], config["max_font_size"])

    #Elememts To store all elements
    elements = []

    #cocoAnotations
    image_id = f"page_{page_id}.jpg"
    #Adding page to the coco file
    add_image(page_count, image_id, config["PAGE_WIDTH"], config["PAGE_HEIGHT"])
    
    #Iterating and Filling Rows
    for i in range(1,len(rows)):

        #Hieght and width limit of row 
        ROW_HEIGHT = rows[i] - rows[i-1]
        ROW_WIDTH = PAGE_WIDTH - (2 * MARGIN)

        #postioning Limits
        vertical_pos_limits = [rows[i-1], rows[i]]
        horizontal_pos_limits = [0+MARGIN, PAGE_WIDTH - MARGIN]

        # 0 is picture or graph and 2 is Text
        element_type = random.choices([0, 2], weights=config["weights"])[0]

        #To Avoid very small images to be created causing errors and to highly blurry images
        if ROW_HEIGHT < 200:
            element_type = 2
            #print("Selected Text")
        
        if element_type == 0: # Picture Left Oriented
            width_left = ROW_WIDTH

            if config["same_size"] == 1 and config["square"] == 1:
                pic_height = random.randint(min(ROW_HEIGHT, config["min_pic_height"]), min(ROW_HEIGHT, config["max_pic_height"]))
                pic_width = pic_height
            elif config["same_size"] == 1 and config["square"] != 1:
                pic_height = random.randint(min(ROW_HEIGHT, config["min_pic_height"]), min(ROW_HEIGHT, config["max_pic_height"]))
                pic_width = random.randint(min(ROW_WIDTH, config["min_pic_width"]), min(ROW_WIDTH, config["max_pic_width"]))
            else:
                print("Invalid Config")
                break
            
            while(width_left > 0):
                if config["same_size"] != 1 and config["square"] == 1:
                    pic_height = random.randint(min(ROW_HEIGHT, config["min_pic_height"]), min(ROW_HEIGHT, config["max_pic_height"]))
                    pic_width = pic_height
                elif config["same_size"] != 1 and config["square"] != 1:
                    pic_height = random.randint(min(ROW_HEIGHT, config["min_pic_height"]), min(ROW_HEIGHT, config["max_pic_height"]))
                    pic_width = random.randint(min(ROW_WIDTH, config["min_pic_width"]), min(ROW_WIDTH, config["max_pic_width"]))
                
                pos_possible_vertical = ROW_HEIGHT - pic_height
                pos_possible_horizontal = horizontal_pos_limits[0] + ROW_WIDTH - width_left
                if config["offset"] == 1:
                    y_pos = vertical_pos_limits[0] + random.randint(0,pos_possible_vertical)
                    x_pos = pos_possible_horizontal
                    width_left = width_left - pic_width
                    if width_left < 0:
                        break
                elif config["offset"] == 2:
                    print("Implementation Phase")
                else:
                    y_pos = vertical_pos_limits[0]
                    x_pos = pos_possible_horizontal
                    width_left = width_left - pic_width
                    if width_left < 0:
                        break
                #print("pic_height: " + str(pic_height))
                #print("pic_width: " + str(pic_width))
                #0 is or image and 1 is for graph
                element_type = element_type = random.choices([0, 1], weights=config["pic_weights"])[0]
                if element_type == 0:
                    image_path = get_random_images(1, [(pic_width, pic_height)], "Generation/science_images",
                                                   "Generation/non_science_images")[0]    
                else:
                    image_path = generate_graphs(1, [(pic_width, pic_height)])[0]
                elements.append({
                "type": element_type,
                "path": image_path,
                "bbox": (x_pos, y_pos, pic_width, pic_height)
                })

        elif element_type == 2: # Text
            text_height = random.randint(ROW_HEIGHT - config["min_hieght_reduce"], ROW_HEIGHT - config["max_hieght_reduce"])
            text_width = random.randint(ROW_WIDTH - config["min_width_reduce"], ROW_WIDTH - config["max_width_reduce"])
            pos_possible_vertical = ROW_HEIGHT -  text_height
            pos_possible_horizontal = ROW_WIDTH - text_width

            if config["offset"] == 1:
                y_pos = vertical_pos_limits[0] + random.randint(0,pos_possible_vertical)
                x_pos = horizontal_pos_limits[0] + random.randint(0, pos_possible_horizontal)
            elif config["offset"] == 2:
                print("Implementation Phase")
            else:
                y_pos = vertical_pos_limits[0]
                x_pos = horizontal_pos_limits[0]

            try:
                image_path = generate_text_images(1, [(text_width, text_height)],font_path, font_size)[0]
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
    print(elements)

    #To Add all elements and update the coco file
    
    for elem in elements:
        try:
            img = Image.open(elem["path"])
            page.paste(img, (elem["bbox"][0], elem["bbox"][1]))

            # Add COCO annotation
            add_annotation(elem_count, page_count, elem["type"], elem["bbox"])
            elem_count = elem_count + 1
        except Exception as e:
            print(f"Error placing element {elem['path']}: {e}")

    # Save the page
    page_path = os.path.join(BASE_DIR, f"page_{page_id}.jpg")
    page.save(page_path)
    page_count = page_count + 1

def generate_research_page_N_columns(page_id, n = config["N"]):
    global page_count
    global elem_count
    #Blank Page
    page = Image.new("RGB", (PAGE_WIDTH, PAGE_HEIGHT), "white")
    draw = ImageDraw.Draw(page)

    #Generates Rows Randomly
    rowss = []
    for i in range(0, n):
        row = row_generater(PAGE_HEIGHT, config["min_row"], config["max_row"], MARGIN)
        rowss.append(row)


    #Font for the page
    fonts = config["Fonts"]
    font_path = random.choice(fonts)
    font_size = random.randint(config["min_font_size"], config["max_font_size"])
    font_bold = random.randint(30, 40)

    #Elememts To store all elements
    elements = []

    #cocoAnotations
    image_id = f"page_{page_id}.jpg"

    #Adding page to the coco file
    add_image(page_count, image_id, config["PAGE_WIDTH"], config["PAGE_HEIGHT"])

    #Iterating 
    for j in range(0, n):
        for i in range(1, len(rowss[j])):
            rows = rowss[j]
        #Calculating limits and size of boxes
            ROW_HEIGHT = rows[i] - rows[i - 1]
            ROW_WIDTH = (PAGE_WIDTH - (2 * MARGIN) - (n*config["col_offset"]))//n
            HEIGHT_LIMITS = [rows[i - 1], rows[i]]
            
            WIDTH_LIMITS = [MARGIN + (j * ROW_WIDTH) + (j*config["col_offset"]), MARGIN + ((j+1) * ROW_WIDTH)]

            #0 is picture and 2 is text
            element_type = random.choices([0, 2], weights=config["weights"])[0]

            bold = False
            if ROW_HEIGHT < 150:
                element_type = 2
                
                bold = random.choices([True, False], weights=[70, 30])[0]
                #print("Selected Bold Text and Increased Font Size")

            if element_type == 0: #Pic selected left oriented
                width_left = ROW_WIDTH

                if config["same_size"] == 1 and config["square"] == 1:
                    pic_height = random.randint(min(ROW_HEIGHT, config["min_pic_height"]), min(ROW_HEIGHT, config["max_pic_height"]))
                    pic_width = pic_height
                elif config["same_size"] == 1 and config["square"] != 1:
                    pic_height = random.randint(min(ROW_HEIGHT, config["min_pic_height"]), min(ROW_HEIGHT, config["max_pic_height"]))
                    pic_width = random.randint(min(ROW_WIDTH, config["min_pic_width"]), min(ROW_WIDTH, config["max_pic_width"]))
                else:
                    print("Invalid Config")
                    break
                #Iterating for pictures
                while(width_left > 0):
                    if config["same_size"] != 1 and config["square"] == 1:
                        pic_height = random.randint(min(ROW_HEIGHT, config["min_pic_height"]), min(ROW_HEIGHT, config["max_pic_height"]))
                        pic_width = pic_height
                    elif config["same_size"] != 1 and config["square"] != 1:
                        pic_height = random.randint(min(ROW_HEIGHT, config["min_pic_height"]), min(ROW_HEIGHT, config["max_pic_height"]))
                        pic_width = random.randint(min(ROW_WIDTH, config["min_pic_width"]), min(ROW_WIDTH, config["max_pic_width"]))
                    pos_possible_vertical = ROW_HEIGHT - pic_height
                    pos_possible_horizontal = WIDTH_LIMITS[0] + ROW_WIDTH - width_left     
                    if config["offset"] == 1:
                        y_pos = HEIGHT_LIMITS[0] + random.randint(0,pos_possible_vertical)
                        x_pos = pos_possible_horizontal
                        width_left = width_left - pic_width
                        if width_left < 0:
                            break
                    elif config["offset"] == 2:
                        print("Implementation Phase")
                    else:
                        y_pos = HEIGHT_LIMITS[0]
                        x_pos = pos_possible_horizontal
                        width_left = width_left - pic_width
                        if width_left < 0:
                            break
                    #print("pic_height: " + str(pic_height))
                    #print("pic_width: " + str(pic_width))
                    #0 is or image and 1 is for graph
                    element_type = element_type = random.choices([0, 1], weights=config["pic_weights"])[0]
                    if element_type == 0:
                        image_path = get_random_images(1, [(pic_width, pic_height)], "Generation/science_images",
                                                "Generation/non_science_images")[0]    
                    else:
                        image_path = generate_graphs(1, [(pic_width, pic_height)])[0]
                    elements.append({
                    "type": element_type,
                    "path": image_path,
                    "bbox": (x_pos, y_pos, pic_width, pic_height)
                    })

            elif element_type == 2: #Text selected
                #Calculation of Text boxe sizes
                text_height = random.randint(ROW_HEIGHT - config["min_hieght_reduce1"], ROW_HEIGHT - config["max_hieght_reduce1"])
                text_width = random.randint(ROW_WIDTH - config["min_width_reduce1"], ROW_WIDTH - config["max_width_reduce1"])
                pos_possible_vertical = ROW_HEIGHT -  text_height
                pos_possible_horizontal = ROW_WIDTH - text_width
                if config["offset"] == 1:
                    y_pos = HEIGHT_LIMITS[0] + random.randint(0,pos_possible_vertical)
                    x_pos = WIDTH_LIMITS[0] + random.randint(0, pos_possible_horizontal)
                elif config["offset"] == 2:
                    print("Implementation Phase")
                else:
                    y_pos = HEIGHT_LIMITS[0]
                    x_pos = WIDTH_LIMITS[0]
                try:
                    if bold == False:
                        image_path = generate_text_images(1, [(text_width, text_height)],font_path, font_size, bold = bold)[0]
                    else:
                        image_path = generate_text_images(1, [(text_width, text_height)],font_path, font_bold, bold = bold)[0]
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

    #Adding page number
    if config["page_number_position"] == "right":
        x_min = PAGE_WIDTH - (100)
        y_min = PAGE_HEIGHT - (MARGIN)
        elements.append(generate_page_number_image(page_id, x_min, y_min, font_size= 14, font_path=font_path))
    print(elements)

    #To Add all elements and update the coco file
    
    for elem in elements:
        try:
            img = Image.open(elem["path"])
            page.paste(img, (elem["bbox"][0], elem["bbox"][1]))

            # Add COCO annotation
            add_annotation(elem_count, page_count, elem["type"], elem["bbox"])
            elem_count = elem_count + 1
        except Exception as e:
            print(f"Error placing element {elem['path']}: {e}")

    # Save the page
    page_path = os.path.join(BASE_DIR, f"page_{page_id}.jpg")
    page.save(page_path)
    page_count = page_count + 1


#Adding Page No to pages
def generate_page_number_image(page_number, x_min, y_min,font_size=30, font_path="arial.ttf", text_color="black", bg_color="white", output_dir="Generation/page"):
    text = f"Page {page_number}"

    try:
        font = ImageFont.truetype(font_path, font_size)
    except IOError:
        font = ImageFont.load_default()  # Fallback if font is missing

    # Determine text size using textbbox
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
        generate_research_page_N_columns(page_id, n= (page_id%N) + 1)
        #generate_research_page_single(page_id)
    
    coco_path = os.path.join(BASE_DIR, "annotations.json")
    with open(coco_path, "w") as f:
        json.dump(coco_data, f, indent=4)
    
    print(f"Dataset generated with {num_pages} pages. COCO annotations saved to {coco_path}.")

generate_dataset(5000)
#generate_research_page_N_columns(config["N"], 1)