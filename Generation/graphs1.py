import os
import random
from PIL import Image
import numpy as np
import matplotlib 
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy.signal import savgol_filter

random.seed(12345)
np.random.seed(12345)

graph_counter = 0
# -----------------------------------------------------
# Helper: Load corpus for labels and title words from corpus.txt
# Each non-empty line is considered a candidate word/phrase.
try:
    with open('Generation/corpus.txt', 'r') as f:
        corpus_words = [line.strip() for line in f if line.strip()]
except Exception:
    corpus_words = ["Time", "Measurement", "Experiment", "Data", "Result"]

# For axis labels, if we have at least one word we use the corpus words.
if len(corpus_words) == 0:
    corpus_words = ["Time", "Measurement", "Experiment", "Data", "Result"]

# Use the entire corpus as label pool
label_pool = corpus_words

# -----------------------------------------------------
# Define a palette of academic-friendly colors and marker styles
RESEARCH_COLORS = [
    "navy", "darkgreen", "firebrick", "purple", "darkorange",
    "teal", "maroon", "indigo"
]
MARKERS = ['o', 's', '^', 'd', '*', 'v', 'p']

# -----------------------------------------------------
# Define 50 distinct mathematical formulas.
# For formulas that may misbehave on negative inputs, we use safeguards like np.maximum.
formula_funcs = {
    'exponential_decay': lambda x: 5 * np.exp(-0.5 * x),
    'saturation_curve': lambda x: 10 * (1 - np.exp(-0.3 * x)),
    'damped_oscillation': lambda x: 8 * np.exp(-0.2 * x) * np.sin(2 * np.pi * x),
    'linear_increase': lambda x: 0.5 * x,
    'logarithmic_growth': lambda x: 5 * np.log(1 + np.maximum(x, 0)),
    'quadratic': lambda x: 0.1 * x**2,
    'cubic': lambda x: 0.01 * x**3,
    'sin_wave': lambda x: 3 * np.sin(x),
    'cos_wave': lambda x: 3 * np.cos(x),
    'hyperbolic_tangent': lambda x: 4 * np.tanh(x),
    'logistic_growth': lambda x: 10 / (1 + np.exp(-0.8*(x-10))),
    'power_law': lambda x: np.power(np.maximum(x + 1, 0), 1.5),
    'inverse_proportional': lambda x: 10 / (x + 1 + 1e-6),
    'sigmoid': lambda x: 6 / (1 + np.exp(-x)) - 3,
    'gaussian': lambda x: np.exp(-0.5 * ((x-10)/2)**2),
    'double_exponential_decay': lambda x: 7 * np.exp(-0.3 * x) + 3 * np.exp(-0.7 * x),
    'decaying_sine': lambda x: np.exp(-0.1 * x) * np.sin(3 * x),
    'quadratic_increase': lambda x: 0.2 * x**2 + x,
    'decreasing_quadratic': lambda x: -0.2 * x**2 + 10,
    'reciprocal_growth': lambda x: 3 + 5/(x+1 + 1e-6),
    'sawtooth': lambda x: ((x % 2) - 1),
    'oscillatory_growth': lambda x: x * np.sin(x/2),
    'random_walk': lambda x: np.cumsum(np.random.randn(len(x))),
    'chaotic_map': lambda x: np.sin(x) + np.sin(3*x),
    'fractal_noise': lambda x: np.interp(x, np.linspace(x.min(), x.max(), 10), np.random.rand(10)),
    'bessel': lambda x: np.where(np.abs(x)<1e-8, 1, np.sin(x)/x),
    'step_function': lambda x: np.where(x > 5, 1, 0),
    'polynomial': lambda x: 0.05 * x**3 - 0.5 * x**2 + x,
    'piecewise_linear': lambda x: np.piecewise(x, [x < 5, x >= 5], [lambda x: x, lambda x: 5 + 0.2*(x-5)]),
    'sine_squared': lambda x: np.sin(x)**2,
    'cosine_squared': lambda x: np.cos(x)**2,
    'inverse_exponential': lambda x: np.where(
    x < 0, 
    -np.exp(np.clip(x, -100, None)),  # Prevent underflow
    np.exp(-np.clip(x, None, 100))    # Prevent overflow
),
    'parabolic': lambda x: 0.01 * (x - 100)**2,
    'cubic_mod': lambda x: 0.0001 * x**3,
    'sine_decay': lambda x: np.sin(x) * np.exp(-0.001*x),
    'cosine_decay': lambda x: np.cos(x) * np.exp(-0.001*x),
    'exponential_growth': lambda x: 0.01 * np.exp(0.005*x),
    'logistic_variant': lambda x: 8 / (1 + np.exp(-0.01*(x-500))),
    'oscillatory_decay': lambda x: np.exp(-0.005*x)*np.cos(0.05*x),
    'quadratic_offset': lambda x: 0.002*x**2 - 0.5*x + 10,
    'sine_log': lambda x: np.sin(np.log(np.maximum(x+1,1))),
    'cos_log': lambda x: np.cos(np.log(np.maximum(x+1,1))),
    'tangent_line': lambda x: np.tan(0.01*x),
    'arctan_curve': lambda x: np.arctan(0.01*x),
    'sinh_curve': lambda x: np.sinh(0.005*x),
    'cosh_curve': lambda x: np.cosh(0.005*x),
    'log_log': lambda x: np.log(np.maximum(x, 1))**2,
    'sqrt_curve': lambda x: np.sqrt(np.maximum(x, 0)),
    'exp_log': lambda x: np.power(x+1, 0.5),
    'sinc': lambda x: np.sinc(x/50),
    'step_linear': lambda x: np.piecewise(x, [x < 0, x >= 0], [lambda x: -1, lambda x: 1]),
    'sigmoid_variant': lambda x: 4/(1+np.exp(-0.02*x))-2
}

# Mapping formulas to simplified mathtext strings acceptable to matplotlib.
eq_map = {
    'exponential_decay': r'$y = 5e^{-0.5x}$',
    'saturation_curve': r'$y = 10(1-e^{-0.3x})$',
    'damped_oscillation': r'$y = 8e^{-0.2x}\sin(2\pi x)$',
    'linear_increase': r'$y = 0.5x$',
    'logarithmic_growth': r'$y = 5\ln(1+x)$',
    'quadratic': r'$y = 0.1x^2$',
    'cubic': r'$y = 0.01x^3$',
    'sin_wave': r'$y = 3\sin x$',
    'cos_wave': r'$y = 3\cos x$',
    'hyperbolic_tangent': r'$y = 4\tanh x$',
    'logistic_growth': r'$y = \frac{10}{1+e^{-0.8(x-10)}}$',
    'power_law': r'$y = (x+1)^{1.5}$',
    'inverse_proportional': r'$y = \frac{10}{x+1}$',
    'sigmoid': r'$y = \frac{6}{1+e^{-x}}-3$',
    'gaussian': r'$y = \exp\left(-\frac{(x-10)^2}{8}\right)$',
    'double_exponential_decay': r'$y = 7e^{-0.3x}+3e^{-0.7x}$',
    'decaying_sine': r'$y = e^{-0.1x}\sin(3x)$',
    'quadratic_increase': r'$y = 0.2x^2+x$',
    'decreasing_quadratic': r'$y = -0.2x^2+10$',
    'reciprocal_growth': r'$y = 3+\frac{5}{x+1}$',
    'sawtooth': r'$y = \mathrm{sawtooth}(x)$',
    'oscillatory_growth': r'$y = x\sin\frac{x}{2}$',
    'random_walk': r'$y = \sum \epsilon_i$',
    'chaotic_map': r'$y = \sin x+\sin 3x$',
    'fractal_noise': r'$y = \mathrm{interp}(x)$',
    'bessel': r'$y = \frac{\sin x}{x}$',
    'step_function': r"$y = 0,\quad \mathrm{if}\ x \leq 5,\quad y = 1,\quad \mathrm{if}\ x > 5$",
    'polynomial': r'$y = 0.05x^3-0.5x^2+x$',
    'piecewise_linear': r'$y = \mathrm{piecewise\ linear}$',
    'sine_squared': r'$y = \sin^2x$',
    'cosine_squared': r'$y = \cos^2x$',
    'inverse_exponential': r'$y = e^{-|x|}$',
    'parabolic': r'$y = 0.01(x-100)^2$',
    'cubic_mod': r'$y = 0.0001x^3$',
    'sine_decay': r'$y = \sin x\,e^{-0.001x}$',
    'cosine_decay': r'$y = \cos x\,e^{-0.001x}$',
    'exponential_growth': r'$y = 0.01e^{0.005x}$',
    'logistic_variant': r'$y = \frac{8}{1+e^{-0.01(x-500)}}$',
    'oscillatory_decay': r'$y = e^{-0.005x}\cos(0.05x)$',
    'quadratic_offset': r'$y = 0.002x^2-0.5x+10$',
    'sine_log': r'$y = \sin\ln(x+1)$',
    'cos_log': r'$y = \cos\ln(x+1)$',
    'tangent_line': r'$y = \tan(0.01x)$',
    'arctan_curve': r'$y = \arctan(0.01x)$',
    'sinh_curve': r'$y = \sinh(0.005x)$',
    'cosh_curve': r'$y = \cosh(0.005x)$',
    'log_log': r'$y = (\ln x)^2$',
    'sqrt_curve': r'$y = \sqrt{x}$',
    'exp_log': r'$y = (x+1)^{0.5}$',
    'sinc': r'$y = \mathrm{sinc}(x/50)$',
    'step_linear': r'$y=-1\quad (\text{if } x<0),\quad 1\quad (\text{if } x\geq0)$',
    'sigmoid_variant': r'$y = \frac{4}{1+e^{-0.02x}}-2$'
}

# -----------------------------------------------------
def weighted_n_points():
    """
    Select a random integer between 10 and 100.
    Numbers in the range 10-20 have the highest weight.
    For every additional 20 in range, the weight reduces by 10%.
    """
    candidates = np.arange(10, 101)
    weights = []
    for n in candidates:
        if n <= 20:
            weight = 1.0
        elif n <= 40:
            weight = 0.9
        elif n <= 60:
            weight = 0.8
        elif n <= 80:
            weight = 0.7
        else:
            weight = 0.6
        weights.append(weight)
    weights = np.array(weights)
    probabilities = weights / weights.sum()
    return int(np.random.choice(candidates, p=probabilities))

def generate_journal_scatter_plot():
    """
    Generate an academic-style scatter plot with these features:
      1. For each scatter group, choose an independent random x-range from [-200, 2000] with at least a 15-unit range.
      2. The number of points is chosen via a weighted selection that favors values between 10 and 20.
      3. 1 to 3 groups are plotted, with each group generated using its own formula (and noise added).
      4. Each group is plotted as a scatter, with markers, color, and optionally can include a smoothing overlay.
      5. The plot title is built from 1 to 5 random words drawn from the corpus.
    """
    # --- Seeding for reproducibility ---
    fig, ax = plt.subplots(figsize=(6, 4))
    
    # --- Choose a random formula for generating an underlying trend.
    # For scatter plots, we show the points along that trend (plus noise).
    formula_name, func = random.choice(list(formula_funcs.items()))
    
    # --- Choose number of scatter groups (1 to 3) ---
    n_groups = random.randint(1, 3)
    
    # For each scatter group generate its own x, y values.
    for i in range(n_groups):
        # Random x-range: choose min_x and ensure diff >= 15 and max_x <= 2000.
        min_x = random.uniform(-200, 1985)
        diff = random.uniform(15, 2000 - min_x)
        max_x = min_x + diff
        
        n_points = weighted_n_points()
        x = np.linspace(min_x, max_x, n_points)
        
        # Underlying trend plus noise
        base_trend = func(x)
        noise_scale = random.uniform(0.05, 0.2)
        noise = np.random.normal(0, noise_scale * np.abs(base_trend) + 0.01, x.shape)
        y = base_trend + noise
        
        # --- Variation mode for scatter group (0: raw scatter, 1: scatter with error bars,
        #     2: scatter with smoothing overlay, 3: scatter with both smoothing and error bars) ---
        variation_mode = random.randint(0, 3)
        
        # Always add markers for scatter
        marker_style = random.choice(MARKERS)
        scatter_color = random.choice(RESEARCH_COLORS)
        scatter_config = {
            'c': scatter_color,
            's': random.uniform(30, 100),
            'alpha': random.uniform(0.7, 0.95),
            'marker': marker_style,
        }
        ax.scatter(x, y, **scatter_config)
        
        # Variation: Optionally add error bars (using vertical error bars)
        if variation_mode in [1, 3]:
            error = 0.1 * np.abs(y) * np.random.uniform(0.5, 1.5, y.shape)
            ax.errorbar(x, y, yerr=error, fmt='none', ecolor=scatter_color, alpha=0.3)
        
        # Variation: Optionally add smoothing overlay on the scatter
        if variation_mode in [2, 3]:
            possible_windows = [w for w in range(3, min(10, n_points+1)) if w % 2 == 1]
            if possible_windows:
                window_size = random.choice(possible_windows)
                try:
                    smooth_y = savgol_filter(y, window_size, 3)
                    ax.plot(x, smooth_y, color='black', linestyle='--', linewidth=1.2,
                            label='Smoothed Trend' if i == 0 else "")
                except Exception as e:
                    print("Smoothing failed:", e)
    
    # --- Set axis labels using random words from the corpus ---
    
    xlabel = random.choice(label_pool)
    ylabel = random.choice(label_pool)
    if random.random() < 0.5:
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
    
    # --- Build title from 1 to 5 random words from corpus ---
    num_title_words = random.randint(1, 5)
    title_words = random.sample(corpus_words, min(num_title_words, len(corpus_words)))
    title_text = " ".join(title_words)
    ax.set_title(f"{title_text}: {formula_name}", pad=12, fontweight='bold')
    
    # --- Add scientific annotation with the formula's equation ---
    eq_text = eq_map.get(formula_name, f"${formula_name}$")
    ax.text(0.05, 0.85, eq_text,
            transform=ax.transAxes,
            fontsize=10,
            bbox=dict(facecolor='white', edgecolor='none', pad=2))
    
    if random.random() < 0.5:
        ax.grid(True, linestyle='--', alpha=0.3)
    
    plt.tight_layout()
    return fig

# -----------------------------------------------------
# Example usage:

# -----------------------------------------------------
def generate_journal_line_plot():
    """
    Generate an academic-style plot with the following features:
      1. For each line, the x-range is chosen randomly from [-200, 2000] such that 
         the difference between the min and max is at least 15.
      2. The number of x points is weighted to favor values between 10 and 20 (then reducing 10% chance each 20 step).
      3. There is a 20% chance per entire graph to add a shadow area (drawn as an offset duplicate line) behind each line.
      4. 1 to 3 lines are plotted; each line uses its own randomly selected x values.
      5. The plot title is built from 1 to 5 random words chosen from the corpus.
    """

    fig, ax = plt.subplots(figsize=(6, 4))

    # 20% chance for overall shadow effect on all lines
    add_graph_shadow = random.random() < 0.2

    # --- Choose a random formula from the 50 defined ---
    formula_name, func = random.choice(list(formula_funcs.items()))

    # --- Number of lines (1-3) ---
    n_lines = random.randint(1, 2)

    # --- Plot each line independently ---
    for i in range(n_lines):
        # For each line, choose its own x-range:
        # Select a random min_x from -200 to 1985 so that at least 15 is available
        min_x = random.uniform(-200, 1985)
        # Select a difference between 15 and (2000 - min_x)
        diff = random.uniform(15, 2000 - min_x)
        max_x = min_x + diff

        # Determine weighted number of points
        n_points = weighted_n_points()
        x = np.linspace(min_x, max_x, n_points)
        
        # Compute the base trend
        base_trend = func(x)
        # Add controlled noise proportional to the signal's magnitude
        noise_scale = random.uniform(0.05, 0.2)
        noise = np.random.normal(0, noise_scale * np.abs(base_trend) + 0.01, x.shape)
        y = base_trend + noise

        # --- Variation mode (per line) from 0 to 3 ---
        variation_mode = random.randint(0, 3)

        # --- 50% chance for markers ---
        add_marker = random.random() < 0.5
        marker_style = random.choice(MARKERS) if add_marker else None

        # Line configuration
        line_color = random.choice(RESEARCH_COLORS)
        line_config = {
            'color': line_color,
            'linewidth': random.uniform(1.2, 1.8),
            'alpha': random.uniform(0.8, 0.95),
        }
        if marker_style:
            line_config['marker'] = marker_style
            line_config['markersize'] = random.uniform(4, 8)

        # --- Optional shadow effect per line (if graph shadow is enabled) ---
        if add_graph_shadow:
            shadow_offset = 0.5  # offset in x and y for shadow effect
            shadow_config = line_config.copy()
            shadow_config['color'] = 'gray'
            shadow_config['alpha'] = 0.3
            shadow_config['linewidth'] = line_config['linewidth'] + 1.0
            # Plot the shadow line with an offset
            ax.plot(x + shadow_offset, y - shadow_offset, **shadow_config)

        # Plot the main line
        ax.plot(x, y, **line_config)

        # --- Variation 1 & 3: Add error bands to this line ---
        if variation_mode in [1, 3]:
            error = 0.1 * np.abs(y) * np.random.uniform(0.5, 1.5, y.shape)
            ax.fill_between(x, y - error, y + error,
                            color=line_color,
                            alpha=0.2)

        # --- Variation 2 & 3: Add a smoothing (moving average) overlay ---
        if variation_mode in [2, 3]:
            # Choose an odd window size between 3 and min(9, n_points)
            possible_windows = [w for w in range(3, min(10, n_points+1)) if w % 2 == 1]
            if possible_windows:
                window_size = random.choice(possible_windows)
                try:
                    smooth_y = savgol_filter(y, window_size, 3)
                    ax.plot(x, smooth_y, color='black', linestyle='--', linewidth=1.2,
                            label='Smoothed Trend' if i == 0 else "")
                except Exception as e:
                    print("Smoothing failed:", e)

    # --- Set axis labels using random words from the corpus ---
    xlabel = random.choice(label_pool)
    ylabel = random.choice(label_pool)
    if random.random() < 0.5:
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)

    # --- Build title from 1 to 5 random words from corpus ---
    num_title_words = random.randint(1, 5)
    title_words = random.sample(corpus_words, min(num_title_words, len(corpus_words)))
    title_text = " ".join(title_words)
    # Append formula name for clarity
    ax.set_title(f"{title_text}: {formula_name}", pad=12, fontweight='bold')

    # --- Add scientific annotation with the formula's equation ---
    eq_text = eq_map.get(formula_name, f"${formula_name}$")
    ax.text(0.05, 0.85, eq_text,
            transform=ax.transAxes,
            fontsize=10,
            bbox=dict(facecolor='white', edgecolor='none', pad=2))

    
    if random.random() < 0.5:
        ax.grid(True, linestyle='--', alpha=0.3)

    plt.tight_layout()
    return fig


def generate_journal_bar_plot():
    """
    Generate an academic-style bar plot with these features:
      1. 5 to 15 groups on the x-axis.  
      2. For side-by-side (grouped) layout:  
           - Each group has the same fixed number of bars (between 1 and 3).
           - All groups share the same color pattern (the same ordered list of colors).
      3. For a stacked chart:  
           - With 50% chance, all groups follow a fixed number of bars and same color pattern (Option A).  
           - Otherwise (Option B) each group can have a different number of bars and its own color pattern.
      4. Each bar's value is randomly chosen from [100, y_lim] where y_lim is a random integer between 100 and 10,000.
      5. X-axis labels for each group are chosen from the corpus 80% of the time, or are a random number (20% chance).
      6. Axis labels and the title are constructed from random words drawn from the corpus.
      7. The plot is randomly rendered as either grouped (side-by-side) or as a stacked bar chart.
    """
    
    # Randomly choose the number of groups: between 5 and 15
    n_groups = random.randint(5, 15)
    
    # Random y-axis limit: integer between 100 and 10,000.
    y_lim = random.randint(100, 10000)
    
    # Randomly choose layout: "grouped" or "stacked"
    layout_type = random.choice(["grouped", "stacked"])
    
    fig, ax = plt.subplots(figsize=(8, 5))
    
    # x positions for groups
    group_positions = np.arange(n_groups)
    
    # For side-by-side layout: use a fixed number of bars (between 1 and 3) for all groups
    if layout_type == "grouped":
        fixed_n_bars = random.randint(1, 3)
        # For a consistent color pattern across groups, select a color pattern for fixed_n_bars
        if fixed_n_bars == 1:
            fixed_color_pattern = [random.choice(RESEARCH_COLORS)]
        else:
            # Pick distinct colors; if insufficient, random.sample ensures uniqueness.
            fixed_color_pattern = random.sample(RESEARCH_COLORS, fixed_n_bars)
        
        bar_width_total = 0.8
        individual_width = bar_width_total / fixed_n_bars
        
        # Prepare container for x-axis labels
        x_labels = []
        
        for i in range(n_groups):
            # Each group gets fixed_n_bars random heights
            heights = [random.randint(100, y_lim) for _ in range(fixed_n_bars)]
            # In grouped layout, we place bars side by side.
            # Compute offsets to center the set around the group position.
            offsets = np.linspace(-bar_width_total/2 + individual_width/2,
                                  bar_width_total/2 - individual_width/2,
                                  fixed_n_bars)
            for j, (h, offset) in enumerate(zip(heights, offsets)):
                ax.bar(group_positions[i] + offset, h, width=individual_width * 0.9,
                       color=fixed_color_pattern[j], alpha=random.uniform(0.8, 0.95))
            # Generate group label: 80% chance using a random word from corpus, else a random number.
            if random.random() < 0.8:
                label = random.choice(label_pool)
            else:
                label = str(random.randint(0, 100))
            x_labels.append(label)
    
    else:  # stacked layout
        # For stacked layout, choose between Option A (fixed bars, same pattern for all groups) and Option B (varying groups)
        stacked_option = random.choice(["A", "B"])
        x_labels = []
        bar_width = 0.8
        for i in range(n_groups):
            if stacked_option == "A":
                # Option A: fixed number of bars for all groups
                fixed_n_bars = random.randint(1, 3) if i == 0 else fixed_n_bars  # set once
                if i == 0:
                    if fixed_n_bars == 1:
                        fixed_color_pattern = [random.choice(RESEARCH_COLORS)]
                    else:
                        fixed_color_pattern = random.sample(RESEARCH_COLORS, fixed_n_bars)
                n_bars = fixed_n_bars
                # Generate n_bars random heights for this group
                heights = [random.randint(100, y_lim) for _ in range(n_bars)]
                bottom = 0
                for h, col in zip(heights, fixed_color_pattern):
                    ax.bar(group_positions[i], h, bottom=bottom, width=bar_width * 0.8,
                           color=col, alpha=random.uniform(0.8, 0.95))
                    bottom += h
            else:
                # Option B: each group can have a different number of bars and its own color pattern.
                n_bars = random.randint(1, 3)
                heights = [random.randint(100, y_lim) for _ in range(n_bars)]
                # For this group, choose a color pattern (if multiple bars, use distinct colors)
                if n_bars == 1:
                    group_colors = [random.choice(RESEARCH_COLORS)]
                else:
                    group_colors = random.sample(RESEARCH_COLORS, n_bars)
                bottom = 0
                for h, col in zip(heights, group_colors):
                    ax.bar(group_positions[i], h, bottom=bottom, width=bar_width * 0.8,
                           color=col, alpha=random.uniform(0.8, 0.95))
                    bottom += h
            # Generate group label for each group (80% chance word; else, number)
            if random.random() < 0.8:
                label = random.choice(label_pool)
            else:
                label = str(random.randint(0, 100))
            x_labels.append(label)
    
    # Set x ticks and labels
    ax.set_xticks(group_positions)
    ax.set_xticklabels(x_labels)
    
    # Set y-axis limit. Ensure that the maximum of either y_lim or the auto-calculated limit is used.
    current_ylim = ax.get_ylim()[1]
    ax.set_ylim(0, max(y_lim, current_ylim))
    
    # Random axis labels from the corpus
    xlabel = random.choice(label_pool)
    ylabel = random.choice(label_pool)
    if random.random() < 0.5:
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
    
    # Build title: select 1 to 5 random words from corpus.
    num_title_words = random.randint(1, 5)
    title_words = random.sample(corpus_words, min(num_title_words, len(corpus_words)))
    title_text = " ".join(title_words)
    ax.set_title(f"{title_text}: {layout_type.capitalize()} Bar Chart", pad=12, fontweight='bold')
    
    if random.random() < 0.5:
        ax.grid(True, linestyle='--', alpha=0.3)
    
    plt.tight_layout()
    return fig

# -----------------------------------------------------
def generate_journal_pie_plot():
    """
    Generate an academic-style pie chart with the following features:
      1. The number of parts is randomly chosen from 1 to 10.
      2. Each part's value is a random integer between 1 and 1000.
      3. A random number (0 to 3) of parts are set to "explode" (offset from the center).
      4. Each part's label is randomly taken from the corpus.
      5. There is a 50% chance to annotate slices with their percentage (autopct).
      6. With a 5% chance, all slices use the same color; otherwise, different colors are used.
"""
    
    # 1. Determine number of parts (slices)
    n_parts = random.randint(2, 10)
    
    # 5. Generate values for each part: random integers in [1, 1000]
    values = [random.randint(1, 1000) for _ in range(n_parts)]
    
    # 2. Set up the explosion ("poking out") configuration.
    # Randomly decide how many slices (0 to 3) will be exploded.
    num_exploded = random.randint(0, min(3, n_parts))
    # Initialize all explodes to 0
    explode = [0] * n_parts
    if num_exploded > 0:
        # Randomly select indices to explode
        exploded_indices = random.sample(range(n_parts), num_exploded)
        # Set a uniform explosion value (e.g., 0.1 or 0.15)
        for idx in exploded_indices:
            explode[idx] = 0.1
    
    # 3. For each part, choose a label from the corpus.
    labels = [random.choice(label_pool) for _ in range(n_parts)]
    
    # 4. 50% chance to include autopct (percentage annotations) on the pie.
    autopct_value = '%1.1f%%' if random.random() < 0.5 else None
    
    # 6. Determine colors for the slices.
    # With 5% chance, use the same color for all slices.
    if random.random() < 0.05:
        color_choice = random.choice(RESEARCH_COLORS)
        colors = [color_choice] * n_parts
    else:
        # Otherwise, try to use distinct colors.
        if n_parts <= len(RESEARCH_COLORS):
            colors = random.sample(RESEARCH_COLORS, n_parts)
        else:
            # If more parts than available colors, use distinct colors as far as possible
            colors = random.sample(RESEARCH_COLORS, len(RESEARCH_COLORS))
            colors += random.choices(RESEARCH_COLORS, k=n_parts - len(RESEARCH_COLORS))
    
    # Create the pie chart figure.
    fig, ax = plt.subplots(figsize=(6, 6))
    if autopct_value:
        wedges, texts, autotexts = ax.pie(
        values,
        explode=explode,
        labels=labels,
        autopct=autopct_value,
        colors=colors,
        shadow=False,
        startangle=random.randint(0, 360)
    )
        plt.setp(autotexts, size=10, weight="bold")
    else:
        wedges, texts = ax.pie(
        values,
        explode=explode,
        labels=labels,
        colors=colors,
        shadow=False,
        startangle=random.randint(0, 360)
    )

    
    # Optionally, customize text properties (e.g., size).
    plt.setp(texts, size=10)
    if autopct_value:
        plt.setp(autotexts, size=10, weight="bold")
    
    # Build a title from 1 to 5 random words from corpus.
    num_title_words = random.randint(1, 5)
    title_words = random.sample(corpus_words, min(num_title_words, len(corpus_words)))
    title_text = " ".join(title_words)
    ax.set_title(f"{title_text}: Pie Chart", pad=12, fontweight='bold')
    
    plt.tight_layout()
    return fig

def generate_graphs(num_graphs, sizes):
    global graph_counter
    """Main graph generation function with proper resizing and mode conversion"""
    graph_functions = {
        #'scatter': generate_journal_scatter_plot,
        'line': generate_journal_line_plot,
        'bar': generate_journal_bar_plot,
        #'pie': generate_journal_pie_plot
    }
    
    os.makedirs("Generation/graph", exist_ok=True)
    image_paths = []
    
    for i in range(num_graphs):
        # Select graph type and generate
        gtype = random.choice(list(graph_functions.keys()))
        fig = graph_functions[gtype]()
        
        # Save high-quality version with white background
        temp_path = f"Generation/graph/temp_{graph_counter}.png"
        fig.savefig(temp_path, dpi=600, bbox_inches='tight', facecolor='white')
        plt.close(fig)
        
        # Resize and convert to RGB
        target_size = sizes[i % len(sizes)]
        img = Image.open(temp_path).convert('RGB')  # Convert to RGB mode
        img = img.resize(target_size, Image.LANCZOS)
        
        # Save final version
        final_path = f"Generation/graph/{gtype}_{graph_counter}.jpg"
        graph_counter+=1
        img.save(final_path, quality=95)
        image_paths.append(final_path)
        os.remove(temp_path)
    
    return image_paths