import os
import random
import numpy as np
from PIL import Image
import json5
import matplotlib
matplotlib.use('Agg')  # Use the Agg backend for non-GUI rendering
import matplotlib.pyplot as plt
from graphs import generate_random_line_plot, generate_random_scatter, generate_random_bar_graph, generate_random_histogram, generate_random_pie_chart, generate_blank_graph

# Load configuration file
def load_config(config_path):
    with open(config_path, "r") as f:
        config = json5.load(f)  # json5 allows comments
    return config

config = load_config("Generation/config.json5")

# Global counter to track function calls
call_count = 0

# Function to generate graphs using functions from `graphs.py`
def generate_graphs(num_graphs, sizes):
    global call_count
    call_count += 1
    base_dir = "Generation"
    graph_dir = os.path.join(base_dir, "graph")
    os.makedirs(graph_dir, exist_ok=True)
    image_paths = []

    # Randomize seed
    random_seed = random.randint(0, 10000)
    np.random.seed(random_seed)
    random.seed(random_seed)

    # Graph type categories
    graph_functions = {
        'line': generate_random_line_plot,
        'scatter': generate_random_scatter,
        'bar': generate_random_bar_graph,
        'histogram': generate_random_histogram,
        'pie': generate_random_pie_chart,
        'blank' : generate_blank_graph
    }
    graph_type = None
    for i in range(num_graphs):
        graph_type = random.choice(list(graph_functions.keys()))  # Pick a single graph type per image
        plt = graph_functions[graph_type]()  # Generate graph using `graphs.py` function

        # Set title and labels
        fig, ax = plt.gca().figure, plt.gca()
        ax.set_title(f"Graph {call_count}_{i+1}", fontsize=14)

        # Add figure number text
        #fig_id = config["fig_id"].format(call_count=call_count, index=i+1)
        #ax.text(config["x_pos"], config["y_pos"], fig_id, transform=ax.transAxes, fontsize=config["font_size"], ha='right', va='top', color='black')

        # Save the graph
        graph_path = os.path.join(graph_dir, f"{call_count}_{i+1}.jpg")
        fig.savefig(graph_path, bbox_inches='tight', pad_inches=0.1, dpi=150)
        plt.close(fig)

        # Resize the image
        img = Image.open(graph_path)
        img_size = sizes[i % len(sizes)]  # Cycle through sizes if fewer sizes than images
        img = img.resize(img_size, Image.BICUBIC)

        # Save resized image
        save_path = os.path.join(graph_dir, f"{call_count}_{i+1}.jpg")
        img.save(save_path)
        image_paths.append(save_path)

    return image_paths, graph_type

# Example usage
#image_sizes = [[200, 200], [300, 300], [400, 400], [500, 500], [1600, 100]]
#image_paths = generate_graphs(5, image_sizes)
#print(f"Generated images: {image_paths}")
