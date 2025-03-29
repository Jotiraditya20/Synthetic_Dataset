import numpy as np
import matplotlib.pyplot as plt
import random
from Text import load_corpus
import scipy.stats as stats
# Sample words for random titles and labels
CORPUS_FILE = "Generation/corpus.txt"
words = load_corpus(CORPUS_FILE)

def generate_random_text(word_count):
    """Generate a random title or label with a given number of words."""
    return " ".join(random.sample(words, word_count))

import numpy as np
import matplotlib.pyplot as plt
import random


def generate_random_scatter():
    """Generates a research-style scatter plot with realistic formatting and randomized parameters."""
    
    # Generate a random number of points (between 50 and 400)
    num_points = random.randint(50, 400)

    # Choose a distribution type (avoiding excessive repetition across multiple plots)
    distribution_type = random.choice(["uniform", "normal", "skewed_normal", "exponential"])
    
    # Define reasonable x and y ranges
    min_x, max_x = random.randint(-50, 50), random.randint(200, 800)
    min_y, max_y = random.randint(-50, 50), random.randint(200, 800)

    if distribution_type == "uniform":
        x = np.random.uniform(min_x, max_x, num_points)
        y = np.random.uniform(min_y, max_y, num_points)
    elif distribution_type == "normal":
        x = np.random.normal(loc=(min_x + max_x) / 2, scale=(max_x - min_x) / 4, size=num_points)
        y = np.random.normal(loc=(min_y + max_y) / 2, scale=(max_y - min_y) / 4, size=num_points)
    elif distribution_type == "skewed_normal":
        x = np.random.normal(loc=(min_x + max_x) / 2, scale=(max_x - min_x) / 6, size=num_points)
        y = np.random.normal(loc=(min_y + max_y) / 2, scale=(max_y - min_y) / 6, size=num_points)
        x = np.abs(x) if random.random() < 0.5 else -np.abs(x)
        y = np.abs(y) if random.random() < 0.5 else -np.abs(y)
    else:  # Exponential
        scale_factor = random.uniform(10, 40)
        x = np.random.exponential(scale=scale_factor, size=num_points) * np.random.choice([-1, 1], num_points)
        y = np.random.exponential(scale=scale_factor, size=num_points) * np.random.choice([-1, 1], num_points)

    # Research-friendly color scheme (grayscale & dark muted colors for publication clarity)
    research_colors = ['black', 'dimgray', 'navy', 'darkred', 'forestgreen']

    # Choose a limited number of distinct colors for clarity
    num_colors = random.randint(1, 2)  # 1-2 colors for clarity in research figures
    colors = random.choices(research_colors, k=num_colors)
    point_colors = random.choices(colors, k=num_points)

    # Adjust marker sizes (smaller & subtle for research figures)
    marker_types = ['o', 's', '^', 'D', '*', 'v', 'P', 'x']  # Removed 'x' from problematic markers
    marker = random.choice(marker_types)
    marker_size = random.uniform(5, 8)

    # Check if marker supports edge colors
    if marker in ['x', 'P']:  
        edgecolor = None  # Avoids warning
    else:
        edgecolor = 'k'  # Black edge for contrast

    # Generate structured research-style labels and titles
    title = generate_random_text(random.randint(2, 4))  # 2 to 4 words
    xlabel = generate_random_text(random.randint(1, 3))  # 1 to 3 words
    ylabel = generate_random_text(random.randint(1, 3))  # 1 to 3 words

    # Create scatter plot
    plt.figure(figsize=(7, 5))
    plt.scatter(x, y, c=point_colors, alpha=0.7, edgecolors=edgecolor, marker=marker, s=marker_size)

    # Set random labels and title
    plt.title(title + f" ({distribution_type} Distribution)", fontsize=14, fontweight='bold')
    plt.xlabel(xlabel, fontsize=12)
    plt.ylabel(ylabel, fontsize=12)

    # Random grid choice, but subtle
    if random.random() < 0.7:
        plt.grid(True, linestyle='--', alpha=0.4)

    return plt

def generate_random_line_plot():
    """Generates a professional research-style line plot with realistic formatting and randomized parameters."""
    
    num_lines = random.randint(1, 2)  # Random number of lines in the plot
    plt.figure(figsize=(7, 5))  # Research paper size

    # Research-friendly colors (good contrast in print)
    research_colors = ['black', 'dimgray', 'darkblue', 'darkred', 'darkgreen']
    
    # Line styles and subtle marker options
    line_styles = ['-', '--', '-.', ':']
    marker_types = ['o', 's', '^', 'x', '*', 'P']  # Small, subtle markers

    for _ in range(num_lines):
        num_points = random.randint(50, 200)  # Number of points in each line

        # Choose a random distribution with meaningful parameters
        distribution_type = random.choice(["uniform", "normal", "exponential", "skewed_normal"])
        min_x, max_x = random.randint(0, 10), random.randint(50, 300)  # Avoid extreme x-ranges
        min_y, max_y = random.randint(0, 10), random.randint(50, 500)  # Logical y-range

        if distribution_type == "uniform":
            x = np.linspace(min_x, max_x, num_points)
            y = np.random.uniform(min_y, max_y, num_points)
        elif distribution_type == "normal":
            mean = random.uniform(min_y + 20, max_y - 20)
            std_dev = random.uniform(10, 40)  # Keeps the variation reasonable
            x = np.linspace(min_x, max_x, num_points)
            y = np.random.normal(loc=mean, scale=std_dev, size=num_points)
        elif distribution_type == "skewed_normal":
            x = np.linspace(min_x, max_x, num_points)
            mean = random.uniform(min_y + 20, max_y - 20)
            std_dev = random.uniform(10, 40)
            skewness = random.uniform(-2, 2)  # Avoids extreme skews
            y = mean + std_dev * np.random.standard_t(df=5, size=num_points) * skewness
        else:  # Exponential
            x = np.linspace(min_x, max_x, num_points)
            scale_factor = random.uniform(10, 50)
            y = np.random.exponential(scale=scale_factor, size=num_points)

        # Random colors, line styles, and markers (subtle sizes)
        line_color = random.choice(research_colors)
        line_style = random.choice(line_styles)
        marker = random.choice(marker_types) if random.random() < 0.5 else ''  # 50% chance of markers
        marker_size = random.uniform(3, 6) if marker else 0  # Smaller markers

        # Plot the line with controlled transparency for readability
        plt.plot(x, y, linestyle=line_style, color=line_color, marker=marker, markersize=marker_size, alpha=0.85, label=f"Line ({distribution_type})")

    # Generate a structured research-style title and labels
    title = generate_random_text(random.randint(2, 4))  # 2 to 4 words
    xlabel = generate_random_text(random.randint(1, 3))  # 1 to 3 words
    ylabel = generate_random_text(random.randint(1, 3))  # 1 to 3 words

    plt.title(title, fontsize=14, fontweight='bold')
    plt.xlabel(xlabel, fontsize=12)
    plt.ylabel(ylabel, fontsize=12)
    plt.legend(fontsize=10, loc="best")
    grid = random.choices([True, False])[0]
    #print(grid)
    if(grid):
        plt.grid(True, linestyle='--', alpha=0.5)  # Subtle grid for research clarity

    return plt

def generate_random_bar_graph():
    """Generates a research-style bar graph with randomized distributions, stacking, colors, and layout."""

    # Number of bars (categories) between 2 and 12
    num_bars = random.randint(2, 12)

    # Choose a distribution for bar heights
    distribution_type = random.choice(["uniform", "normal", "skewed_normal", "exponential"])
    
    if distribution_type == "uniform":
        values = np.random.uniform(10, 100, num_bars)
    elif distribution_type == "normal":
        values = np.abs(np.random.normal(50, 20, num_bars))  # Avoid negatives
    elif distribution_type == "skewed_normal":
        values = np.random.normal(30, 10, num_bars) ** 1.5  # Skewed effect
    else:  # Exponential
        values = np.random.exponential(scale=30, size=num_bars)
    
    # Randomly decide if bars should be **stacked, grouped, or single**
    bar_type = random.choice(["single", "stacked", "grouped"])
    
    # Research-friendly colors
    research_colors = ['black', 'dimgray', 'slategray', 'navy', 'darkred']
    
    # Generate structured bar labels
    bar_labels = [generate_random_text(1) for _ in range(num_bars)]
    
    # Generate title and axis labels
    title = generate_random_text(random.randint(2, 4))  # 2 to 4 words
    xlabel = generate_random_text(random.randint(1, 3))  # 1 to 3 words
    ylabel = generate_random_text(random.randint(1, 3))  # 1 to 3 words

    # Create the figure
    plt.figure(figsize=(8, 6))
    
    if bar_type == "single":
        # Single-colored bars
        bar_color = random.choice(research_colors)
        plt.bar(bar_labels, values, color=bar_color, alpha=0.85, edgecolor='black')

    elif bar_type == "stacked":
        # Stacked bars with random segments
        num_stacks = random.randint(2, 4)
        stack_values = [values * np.random.uniform(0.3, 1, num_bars) for _ in range(num_stacks)]
        bottom = np.zeros(num_bars)
        
        for stack in stack_values:
            plt.bar(bar_labels, stack, bottom=bottom, color=random.choice(research_colors), edgecolor='black', alpha=0.85)
            bottom += stack  # Add height for stacking

    elif bar_type == "grouped":
        # Grouped bars with 2-4 variations per category
        num_groups = random.randint(2, 4)
        width = 0.8 / num_groups  # Adjust bar width
        
        for i in range(num_groups):
            offset = (i - (num_groups - 1) / 2) * width  # Offset for grouping
            plt.bar(np.arange(num_bars) + offset, values * np.random.uniform(0.5, 1.5, num_bars), 
                    width=width, color=random.choice(research_colors), edgecolor='black', alpha=0.85)

        plt.xticks(ticks=np.arange(num_bars), labels=bar_labels, rotation=30, ha='right')

    # Set title and labels
    plt.title(title + f" ({distribution_type} Distribution)", fontsize=14, fontweight='bold')
    plt.xlabel(xlabel, fontsize=12)
    plt.ylabel(ylabel, fontsize=12)

    # Rotate labels for better readability if too many bars
    if num_bars > 5:
        plt.xticks(rotation=30, ha='right')

    # Random grid style
    if random.random() < 0.7:
        plt.grid(True, linestyle='--', alpha=0.4, axis='y')

    return plt

def generate_random_histogram():
    """Generates a research-style frequency histogram with random data distribution, bins, and colors."""
    
    # Number of data points
    num_points = random.randint(200, 1000)

    # Choose a random distribution
    distribution_type = random.choice(["uniform", "normal", "skewed_normal", "exponential", "poisson"])
    
    if distribution_type == "uniform":
        data = np.random.uniform(10, 100, num_points)
    elif distribution_type == "normal":
        data = np.random.normal(50, 15, num_points)  # Mean=50, Std Dev=15
    elif distribution_type == "skewed_normal":
        data = stats.skewnorm.rvs(a=random.uniform(4, 10), loc=50, scale=15, size=num_points)  # Skewed normal
    elif distribution_type == "exponential":
        data = np.random.exponential(scale=30, size=num_points)
    else:  # Poisson
        data = np.random.poisson(lam=30, size=num_points)

    # Random number of bins (between 5 and 20)
    num_bins = random.randint(5, 20)

    # Research-friendly colors
    research_colors = ['black', 'dimgray', 'slategray', 'navy', 'darkred']
    bar_color = random.choice(research_colors)

    # Generate structured labels
    title = generate_random_text(random.randint(2, 4))  # 2 to 4 words
    xlabel = generate_random_text(random.randint(1, 3))  # 1 to 3 words
    ylabel = "Frequency"

    # Create the figure
    plt.figure(figsize=(8, 6))
    plt.hist(data, bins=num_bins, color=bar_color, edgecolor='black', alpha=0.85)

    # Set title and labels
    plt.title(title + f" ({distribution_type.capitalize()} Distribution)", fontsize=14, fontweight='bold')
    plt.xlabel(xlabel, fontsize=12)
    plt.ylabel(ylabel, fontsize=12)

    # Random grid style
    if random.random() < 0.5:
        plt.grid(True, linestyle='--', alpha=0.4, axis='y')

    return plt

def generate_random_pie_chart():
    """Generates a research-style pie chart with randomized categories, values, and colors."""
    
    # Random number of segments (between 2 and 8)
    num_categories = random.randint(2, 8)

    # Generate random values (proportions)
    values = np.random.randint(5, 50, num_categories)  # Each category gets between 5-50 units
    values = values / values.sum() * 100  # Normalize to 100%

    # Generate random category labels
    labels = [generate_random_text(random.randint(1, 3)) for _ in range(num_categories)]

    # Research-friendly muted colors
    research_colors = ['dimgray', 'slategray', 'navy', 'darkred', 'teal', 'darkgreen', 'chocolate', 'purple']
    colors = random.sample(research_colors, k=num_categories)

    # Random explode effect (sometimes highlighting one slice)
    explode = [0.1 if random.random() < 0.3 else 0 for _ in range(num_categories)]

    # Random start angle
    start_angle = random.randint(0, 360)

    # Generate title
    title = generate_random_text(random.randint(2, 4)) + " Distribution"

    # Create figure
    plt.figure(figsize=(7, 7))
    plt.pie(values, labels=labels, colors=colors, autopct='%1.1f%%', startangle=start_angle, explode=explode, wedgeprops={'edgecolor': 'black'})

    # Set title
    plt.title(title, fontsize=14, fontweight='bold')

    return plt


    """
    Generates a blank graph with only a title, axis labels, and x/y axis lines.
    """
    fig, ax = plt.subplots()

    # Generate random ranges for axes
    x_min, x_max = sorted(np.random.uniform(-1000, 1000, 2))
    y_min, y_max = sorted(np.random.uniform(-1000, 1000, 2))
    
    # Set limits based on the generated ranges
    ax.set_xlim(x_min, x_max)
    ax.set_ylim(y_min, y_max)

    # Draw X and Y axis lines
    ax.axhline(0, color='black', linewidth=1, linestyle='--')  # X-axis
    ax.axvline(0, color='black', linewidth=1, linestyle='--')  # Y-axis

    # Randomly assign title and labels
    title = random.choice(["Data Analysis", "Statistical Overview", "Performance Metrics", "Trend Analysis", "Empty Graph"])
    x_label = random.choice(["Time (s)", "Distance (m)", "Size (cm)", "Value (units)"])
    y_label = random.choice(["Frequency (Hz)", "Amplitude (dB)", "Count", "Intensity (lux)"])

    ax.set_title(title, fontsize=14)
    ax.set_xlabel(x_label, fontsize=12)
    ax.set_ylabel(y_label, fontsize=12)

    # Hide tick marks
    ax.set_xticks([])
    ax.set_yticks([])

    return plt

def generate_blank_graph():
    """
    Generates a blank graph with a random title, axis labels, and x/y axis lines with values.
    """
    fig, ax = plt.subplots()

    # Generate random ranges for axes
    x_min, x_max = sorted(np.random.uniform(-1000, 1000, 2))
    y_min, y_max = sorted(np.random.uniform(-1000, 1000, 2))

    # Set limits based on the generated ranges
    ax.set_xlim(x_min, x_max)
    ax.set_ylim(y_min, y_max)

    # Draw X and Y axis lines
    ax.axhline(0, color='black', linewidth=1, linestyle='--')  # X-axis
    ax.axvline(0, color='black', linewidth=1, linestyle='--')  # Y-axis

    # Generate random tick intervals
    x_ticks_interval = random.choice([50, 100, 200, 500])
    y_ticks_interval = random.choice([50, 100, 200, 500])

    # Set tick values
    x_ticks = np.arange(x_min, x_max, x_ticks_interval)
    y_ticks = np.arange(y_min, y_max, y_ticks_interval)
    ax.set_xticks(x_ticks)
    ax.set_yticks(y_ticks)

    # Generate random title and labels
    title = generate_random_text(random.randint(2, 5))  # 2 to 5 words
    x_label = generate_random_text(random.randint(1, 3))  # 1 to 3 words
    y_label = generate_random_text(random.randint(1, 3))  # 1 to 3 words

    ax.set_title(title, fontsize=14)
    ax.set_xlabel(x_label, fontsize=12)
    ax.set_ylabel(y_label, fontsize=12)

    # Display grid for clarity (optional)
    if random.choice([True, False]):
        ax.grid(True, linestyle="--", alpha=0.3)

    return plt

# Example usage:
#plot = generate_blank_graph()
#plot.show()
