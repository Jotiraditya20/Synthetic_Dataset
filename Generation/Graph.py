import os
import random
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
import json5

#Loading config files
def load_config(config_path):
    with open(config_path, "r") as f:
        config = json5.load(f)  # json5 allows comments
    return config
config = load_config("Generation/config.json5")


# Global counter to track function calls
call_count = 0

# Function to generate random graphs and save as .jpg in 'Generation/graph' folder
def generate_graphs(num_graphs, sizes):
    global call_count
    call_count += 1
    base_dir = "Generation"
    graph_dir = os.path.join(base_dir, "graph")
    os.makedirs(graph_dir, exist_ok=True)
    graph_paths = []
    image_dir = os.path.join(base_dir, "graph")
    os.makedirs(image_dir, exist_ok=True)
    image_paths = []

    graph_types = ['line', 'scatter', 'bar', 'hist', 'area', 'step']
    colors = ['b', 'g', 'r', 'c', 'm', 'y', 'k']
    markers = ['o', 's', 'D', 'x', '*', '+']

    # Set a new random seed for each function call
    random_seed = random.randint(0, 10000)
    np.random.seed(random_seed)
    random.seed(random_seed)

    for i in range(num_graphs):
        fig, ax = plt.subplots()
        num_features = random.randint(1, 3)

        for _ in range(num_features):
            num_points = random.randint(10, 50)
            x = np.random.uniform(0, 2000, num_points)
            x.sort()
            pattern = random.choice(['linear', 'exponential', 'sinusoidal'])

            if pattern == 'linear':
                y = np.random.uniform(50, 150) * x + np.random.uniform(-1000, 1000)
            elif pattern == 'exponential':
                y = np.exp(x / np.random.uniform(50, 200)) + np.random.uniform(-500, 500)
            elif pattern == 'sinusoidal':
                y = np.sin(x / np.random.uniform(10, 50)) * np.random.uniform(500, 1500) + np.random.uniform(-500, 500)

            graph_type = random.choice(graph_types)
            color = random.choice(colors)
            marker = random.choice(markers)

            if graph_type == 'line':
                ax.plot(x, y, color=color, marker=marker, label=f"Line {_+1}")
            elif graph_type == 'scatter':
                ax.scatter(x, y, color=color, marker=marker, label=f"Scatter {_+1}")
            elif graph_type == 'bar':
                ax.bar(x, y, color=color, alpha=0.7, label=f"Bar {_+1}")
            elif graph_type == 'hist':
                ax.hist(y, bins=random.randint(10, 30), color=color, alpha=0.7, label=f"Hist {_+1}")
            elif graph_type == 'area':
                ax.fill_between(x, y, color=color, alpha=0.5, label=f"Area {_+1}")
            elif graph_type == 'step':
                ax.step(x, y, color=color, label=f"Step {_+1}")

        ax.set_title(f"Graph {call_count}_{i+1}", fontsize=14)
        ax.set_xlabel(f"X Axis ({random.choice(['Time (s)', 'Distance (m)', 'Size (cm)', 'Value (units)'])})", fontsize=12)
        ax.set_ylabel(f"Y Axis ({random.choice(['Frequency (Hz)', 'Amplitude (dB)', 'Count', 'Intensity (lux)'])})", fontsize=12)
        ax.grid(True, linestyle='--', alpha=0.6)
        ax.legend(loc='upper right', fontsize=10)

        # Add figure number text
        fig_id = config["fig_id"].format(call_count=call_count, index = i+1)
        ax.text(config["x_pos"], config["y_pos"], fig_id, transform=ax.transAxes, fontsize=config["font_size"], ha='right', va='top', color='black')

        # Save the graph
        graph_path = os.path.join(graph_dir, f"{call_count}_{i+1}.jpg")
        plt.savefig(graph_path, bbox_inches='tight', pad_inches=0.1, dpi=150)
        plt.close()

        # Resize the graph image
        img = Image.open(graph_path)
        img_size = sizes[i % len(sizes)]  # Cycle through the sizes if fewer sizes than images
        img = img.resize(img_size, Image.LANCZOS)
        #good to start at 300 orelse becomes blurry

        # Save the resized image
        save_path = os.path.join(image_dir, f"{call_count}_{i+1}.jpg")
        img.save(save_path)
        image_paths.append(save_path)

    return image_paths

# Example usage
#image_sizes = [[200, 200], [300, 300], [400, 400], [500, 500], [1600, 100]]  # List of sizes for the images
#image_paths = generate_graphs(5, image_sizes)
#print(f"Generated images: {image_paths}")