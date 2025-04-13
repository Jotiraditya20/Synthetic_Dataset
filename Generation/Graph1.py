import os
import random
import uuid
import matplotlib 
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from PIL import Image, ImageDraw, ImageFont

def generate_graphs(num_graphs, sizes, caption_texts=None, caption_height=25, font_path="arial.ttf", font_size=14):
    """
    Generates graphs with embedded captions.
    Each graph is produced with a unique filename. The final image has extra space at the bottom for the caption.
    
    :param num_graphs: number of graphs to generate.
    :param sizes: list of tuples for the desired (width, total_height) for the final output image.
                  (total_height includes space for caption)
    :param caption_texts: Optional list of captions (strings). If None, default captions will be used.
    :param caption_height: Height (in pixels) reserved for caption text.
    :param font_path: Path to the font file.
    :param font_size: Font size for caption.
    :returns: List of file paths for the generated graphs.
    """
    # Dictionary mapping graph types to generation functions
    from graphs1 import generate_journal_line_plot, generate_journal_scatter_plot, generate_journal_bar_plot, generate_journal_pie_plot
    graph_functions = {
        #'scatter': generate_journal_scatter_plot,
        'line': generate_journal_line_plot,
        'bar': generate_journal_bar_plot,
        #'pie': generate_journal_pie_plot
    }
    
    os.makedirs("Generation/graph", exist_ok=True)
    image_paths = []
    
    for i in range(num_graphs):
        gtype = random.choice(list(graph_functions.keys()))
        # Generate a new figure
        fig = graph_functions[gtype]()
        
        # Generate a unique id
        unique_id = uuid.uuid4().hex
        temp_path = f"Generation/graph/temp_{gtype}_{unique_id}.png"
        
        # Save the graph temporarily
        fig.savefig(temp_path, dpi=600, bbox_inches='tight', facecolor='white')
        plt.close(fig)
        
        # Open and convert the saved figure to RGB
        img = Image.open(temp_path).convert("RGB")
        
        # Get target dimensions for the final image (width and total height which includes caption space)
        target_width, target_total_height = sizes[i % len(sizes)]
        target_img_height = target_total_height - caption_height  # height available for the graph
        
        # Resize the graph
        img = img.resize((target_width, target_img_height), Image.LANCZOS)
        
        # Create a new canvas with extra space for caption at the bottom
        final_img = Image.new("RGB", (target_width, target_total_height), "white")
        final_img.paste(img, (0, 0))
        
        # Determine the caption text: use provided one if available; otherwise use default caption.
        if caption_texts and i < len(caption_texts):
            caption = caption_texts[i]
        else:
            # Default caption construction, for example "Fig <unique_id[:4]>: <random words>"
            default_caption = f"Fig {unique_id[:4]}: " + " ".join(random.sample(["Time", "Measurement", "Experiment", "Data", "Result"], random.randint(1, 5)))
            caption = default_caption
        
        # Draw the caption
        draw = ImageDraw.Draw(final_img)
        try:
            font = ImageFont.truetype(font_path, font_size)
        except IOError:
            font = ImageFont.load_default()
        
        # You can measure text and center it horizontally if desired:
        text_bbox = draw.textbbox((0, 0), caption, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        x_text = (target_width - text_width) // 2  # center horizontally
        y_text = target_img_height + (caption_height - font_size) // 2  # vertically centered in caption area
        
        draw.text((x_text, y_text), caption, fill="black", font=font)
        
        # Save final version
        final_path = f"Generation/graph/{gtype}_{unique_id}.jpg"
        final_img.save(final_path, quality=95)
        image_paths.append(final_path)
        
        # Remove the temporary file
        os.remove(temp_path)
    
    return image_paths