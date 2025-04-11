import matplotlib.pyplot as plt
import numpy as np
import random
from scipy.interpolate import make_interp_spline


def generate_random_text(n_words):
    words = ["Temperature", "Time", "Growth", "Response", "Signal", "Amplitude", "Voltage", "Rate", "Concentration", "Distance"]
    return " ".join(random.choices(words, k=n_words))


def generate_xy(pattern, num_points):
    x_max = random.uniform(50, 1000)  # Increase x range
    x = np.linspace(0, x_max, num_points)

    if pattern == "linear":
        y = random.uniform(-50, 50) * x + random.uniform(-100, 100)

    elif pattern == "quadratic":
        y = random.uniform(-1, 1) * x**2 + random.uniform(-20, 20) * x + random.uniform(-100, 100)

    elif pattern == "polynomial":
        coeffs = [random.uniform(-1, 1) for _ in range(random.randint(3, 5))]
        y = np.polyval(coeffs, x)

    elif pattern == "sine":
        y = random.uniform(10, 100) * np.sin(random.uniform(0.01, 0.2) * x)

    elif pattern == "log":
        x = np.linspace(1, x_max, num_points)
        y = np.log(x) * random.uniform(10, 100)

    elif pattern == "exponential":
        y = np.exp(x * random.uniform(0.005, 0.01)) * random.uniform(0.1, 2)
        y = np.clip(y, 0, 1e5)

    elif pattern == "logistic":
        L = random.uniform(100, 300)
        k = random.uniform(0.05, 0.15)
        x0 = random.uniform(0.2 * x_max, 0.8 * x_max)
        y = L / (1 + np.exp(-k * (x - x0)))

    elif pattern == "step":
        y = np.floor(x / random.uniform(5, 15)) * random.uniform(10, 100)

    elif pattern == "piecewise":
        y = np.piecewise(
            x,
            [x < x_max/3, (x >= x_max/3) & (x < 2*x_max/3), x >= 2*x_max/3],
            [lambda x: x * random.uniform(0.5, 1.5), lambda x: -x + x_max, lambda x: x * 0.5]
        )

    elif pattern == "spikey":
        y = np.sin(x * 0.5) * 20 + np.random.normal(scale=10, size=num_points)

    elif pattern == "uniform":
        y = np.random.uniform(-100, 100, num_points)

    elif pattern == "normal":
        y = np.random.normal(loc=0, scale=50, size=num_points)

    elif pattern == "fourier":
        y = sum(np.sin((i+1) * x * 0.05) * random.uniform(10, 50) for i in range(3))

    elif pattern == "spline":
        control_x = np.linspace(0, x_max, 10)
        control_y = np.random.rand(10) * 200 - 100
        spline = make_interp_spline(control_x, control_y, k=3)
        y = spline(x)

    elif pattern == "gaussian_peaks":
        centers = np.random.uniform(10, x_max - 10, size=2)
        widths = np.random.uniform(2, 10, size=2)
        y = sum(np.exp(-((x - c)**2) / (2 * w**2)) * random.uniform(50, 100) for c, w in zip(centers, widths))

    elif pattern == "random_walk":
        y = np.cumsum(np.random.randn(num_points)) * random.uniform(5, 20)

    elif pattern == "noisy_piecewise":
        segment_len = num_points // 5
        y = []
        for _ in range(5):
            base = random.uniform(-50, 50)
            segment = [base + random.uniform(-10, 10) for _ in range(segment_len)]
            y.extend(segment)
        y = np.array(y[:num_points])
        if len(y) < num_points:
            y = np.pad(y, (0, num_points - len(y)), mode='edge')

    else:
        y = np.zeros_like(x)

    # Final crop to same length
    x = x[:len(y)]
    y = y[:len(x)]

    return x, y


def generate_diverse_line_plot():
    plt.figure(figsize=(7, 5))
    ax = plt.gca()
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    line_styles = ['-', '--', '-.', ':']
    marker_types = ['o', 's', '^', 'x', '*', 'P']
    research_colors = ['black', 'dimgray', 'darkblue', 'darkred', 'darkgreen', 'indigo', 'teal']

    num_lines = random.randint(1, 3)
    available_patterns = [
        "linear", "quadratic", "polynomial", "sine", "log", "exponential",
        "step", "logistic", "piecewise", "spikey", "uniform", "normal",
        "fourier", "spline", "gaussian_peaks", "random_walk", "noisy_piecewise"
    ]

    patterns = [random.choice(available_patterns)] if random.random() < 0.5 else random.sample(available_patterns, 2)

    marker = random.choice(marker_types)
    show_marker = random.random() < 0.5
    marker_size = random.uniform(3, 6) if show_marker else 0

    single_color = random.random() < 0.5
    chosen_color = random.choice(research_colors)

    for _ in range(num_lines):
        pattern = random.choice(patterns)
        num_points = random.randint(10, 100)
        x, y = generate_xy(pattern, num_points)

        color = chosen_color if single_color else random.choice(research_colors)
        line_style = random.choice(line_styles)

        plt.plot(
            x, y,
            linestyle=line_style,
            color=color,
            marker=marker if show_marker else '',
            markersize=marker_size,
            alpha=0.85,
            label=f"{pattern} pattern"
        )

    title = generate_random_text(random.randint(2, 4))
    xlabel = generate_random_text(random.randint(1, 3))
    ylabel = generate_random_text(random.randint(1, 3))

    plt.title(title, fontsize=14, fontweight='bold')
    plt.xlabel(xlabel, fontsize=12)
    plt.ylabel(ylabel, fontsize=12)
    plt.legend(fontsize=10, loc="best")

    if random.random() < 0.5:
        plt.grid(True, linestyle='--', alpha=0.5)

    return plt


# Run and save
if __name__ == "__main__":
    fig = generate_diverse_line_plot()
    fig.savefig("wider_range_plot.png")
    fig.show()
