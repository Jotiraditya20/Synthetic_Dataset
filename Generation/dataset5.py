import os
import random
import json
from PIL import Image, ImageDraw, ImageFont
from Text import generate_text_images
from Image import get_random_images
from graphs1 import generate_graphs
import json5

# Load configuration
config = json5.load(open("./Generation/dataset3_config.json5"))
CORPUS_FILE = "Generation/corpus.txt"
BASE_DIR = "dataset"

# Initialize COCO dataset
coco_data = config["coco_template"]
coco_data["categories"] = [c for c in coco_data["categories"] if c["id"] in [0,1,2]]

class ResearchPaperGenerator:
    def __init__(self):
        self.page_count = 0
        self.elem_count = 0
        self.current_font = None
        self.title_height = 100
        self.corpus = self._load_corpus()
        
    def _load_corpus(self):
        with open(CORPUS_FILE, "r") as f:
            return [line.strip() for line in f if line.strip()]
    
    def _get_random_text(self, min_words=5, max_words=15):
        num_words = random.randint(min_words, max_words)
        return ' '.join(random.choices(self.corpus, k=num_words)).capitalize()

    def _setup_page_style(self):
        self.current_font = random.choice(config["Fonts"])
        self.font_sizes = {
            'title': random.randint(24, 28),
            'header': random.randint(config["min_font_size"], config["max_font_size"]),
            'body': random.randint(config["min_font_size"]-2, config["max_font_size"]-2),
            'caption': random.randint(config["min_font_size"]-4, config["max_font_size"]-4)
        }

    def _create_layout_grid(self, num_cols):
        col_width = (config["PAGE_WIDTH"] - 2*config["MARGIN"] - 
                    (num_cols-1)*config["col_offset"]) // num_cols
        return [
            (config["MARGIN"] + i*(col_width + config["col_offset"]),
             config["MARGIN"] + (i+1)*col_width + i*config["col_offset"])
            for i in range(num_cols)
        ]

    def _calculate_available_space(self, current_y):
        return config["PAGE_HEIGHT"] - current_y - config["MARGIN"]

    def _fit_element(self, element_height, current_y):
        return min(element_height, self._calculate_available_space(current_y))

    def _add_title_section(self, page):
        title_width = config["PAGE_WIDTH"] - 2*config["MARGIN"]
        title_img = generate_text_images(
            1, [(title_width, self.title_height)],
            self.current_font, self.font_sizes['title'],
            bold=True, text=self._get_random_text(3, 8)
        )[0]
        self._place_element(page, title_img, 
                          (config["MARGIN"], config["MARGIN"], 
                           title_width, self.title_height), 2)

    def _place_element(self, page, img_path, bbox, category):
        try:
            img = Image.open(img_path)
            page.paste(img, (bbox[0], bbox[1]))
            self._add_coco_annotation(bbox, category)
        except Exception as e:
            print(f"Error placing element: {e}")

    def _add_coco_annotation(self, bbox, category):
        coco_data["annotations"].append({
            "id": self.elem_count,
            "image_id": self.page_count,
            "category_id": category,
            "bbox": [bbox[0], bbox[1], bbox[2], bbox[3]],
            "area": bbox[2] * bbox[3],
            "segmentation": [],
            "iscrowd": 0
        })
        self.elem_count += 1

    def _add_page_number(self, page, page_id):
        try:
            font = ImageFont.truetype(self.current_font, self.font_sizes['caption'])
        except:
            font = ImageFont.load_default()
        
        d = ImageDraw.Draw(page)
        footer_text = str(page_id)
        text_width = d.textlength(footer_text, font=font)
        x = min(
            config["PAGE_WIDTH"] - text_width - config["x_positioning"],
            config["PAGE_WIDTH"] - config["MARGIN"] - text_width
        )
        y = config["PAGE_HEIGHT"] - config["MARGIN"] - 20
        d.text((x, y), footer_text, fill="black", font=font)

    def generate_page(self, page_id):
        page = Image.new("RGB", (config["PAGE_WIDTH"], config["PAGE_HEIGHT"]), "white")
        self._setup_page_style()
        self._add_title_section(page)

        # Column setup
        num_cols = random.choice([1, 2] if config["N"] == 2 else [1])
        columns = self._create_layout_grid(num_cols)
        y_pos = 2*config["MARGIN"] + self.title_height

        for col_idx, (x1, x2) in enumerate(columns):
            current_y = y_pos
            col_width = x2 - x1
            
            while current_y < config["PAGE_HEIGHT"] - config["MARGIN"]:
                max_height = self._calculate_available_space(current_y)
                if max_height < config["min_element_height"]:
                    break

                element_type = random.choices(
                    ['text', 'figure'], 
                    weights=config["weights"], 
                    k=1
                )[0]
                
                if element_type == 'text':
                    # Header check
                    if random.random() < 0.3 and current_y == y_pos:
                        header_img = generate_text_images(
                            1, [(col_width, 40)],
                            self.current_font, self.font_sizes['header'],
                            text=self._get_random_text(1, 4), bold=True
                        )[0]
                        self._place_element(page, header_img, 
                                          (x1, current_y, col_width, 40), 2)
                        current_y += 45
                        max_height = self._calculate_available_space(current_y)

                    text_height = self._fit_element(
                        random.randint(config["min_row"], config["max_row"]),
                        current_y
                    )
                    text_img = generate_text_images(
                        1, [(col_width, text_height)],
                        self.current_font, self.font_sizes['body'],
                        text=self._get_random_text(50, 200)
                    )[0]
                    self._place_element(page, text_img, 
                                      (x1, current_y, col_width, text_height), 2)
                    current_y += text_height + config["element_spacing"]
                
                else:  # Figure element
                    fig_height = self._fit_element(
                        random.randint(config["min_pic_height"], config["max_pic_height"]),
                        current_y
                    )
                    fig_width = fig_height if config["square"] else random.randint(
                        config["min_pic_width"], config["max_pic_width"])
                    fig_width = min(fig_width, col_width)

                    
                    if config["offset"]:
                        x_offset = x1 + random.randint(0, max(0, col_width - fig_width)) 
                    else:
                        x_offset = x1

                    # Generate figure
                    fig_type = random.choices(['image', 'graph'], 
                                            weights=config["pic_weights"], k=1)[0]
                    fig_img = (get_random_images(1, [(fig_width, fig_height)])[0] 
                            if fig_type == 'image' else generate_graphs(1, [(fig_width, fig_height)])[0])
                    
                    self._place_element(page, fig_img, 
                                      (x_offset, current_y, fig_width, fig_height), 
                                      1 if fig_type == 'image' else 0)
                    
                    # Add caption if space permits
                    caption_y = current_y + fig_height + 5
                    if caption_y < config["PAGE_HEIGHT"] - 35:
                        caption_img = generate_text_images(
                            1, [(fig_width, 30)],
                            self.current_font, self.font_sizes['caption'],
                            text=f"Fig. {self.elem_count}: {self._get_random_text(4, 8)}"
                        )[0]
                        self._place_element(page, caption_img, 
                                          (x_offset, caption_y, fig_width, 30), 2)

                    current_y += fig_height + 40

        self._add_page_number(page, page_id)
        
        # Save page
        page.save(os.path.join(BASE_DIR, f"page_{page_id}.jpg"))
        coco_data["images"].append({
            "id": self.page_count,
            "file_name": f"page_{page_id}.jpg",
            "width": config["PAGE_WIDTH"],
            "height": config["PAGE_HEIGHT"]
        })
        self.page_count += 1

def generate_dataset(num_pages):
    os.makedirs(BASE_DIR, exist_ok=True)
    generator = ResearchPaperGenerator()
    
    for page_id in range(num_pages):
        print(f"Generating page {page_id}")
        generator.generate_page(page_id)
    
    with open(os.path.join(BASE_DIR, "annotations.json"), "w") as f:
        json.dump(coco_data, f)

if __name__ == "__main__":
    generate_dataset(10)