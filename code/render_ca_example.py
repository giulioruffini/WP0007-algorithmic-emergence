"""Render the checked CA comparison used in the manuscript."""
from pathlib import Path
import argparse
import sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
import numpy as np
import ca_examples as ca

root = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--output-dir", type=Path,
                    default=root / ("entropy/figures" if (root / "entropy").is_dir() else "figures"))
parser.add_argument("--figcheck-dir", type=Path,
                    help="optional directory containing the figcheck overlap.py checker")
args = parser.parse_args()
target = args.output_dir
target.mkdir(parents=True, exist_ok=True)
initial = ca.initial_state(7)
micro = ca.evolve(initial, ca.BLOCK * ca.COARSE_STEPS, 146)
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10.5,
                     "axes.titlesize": 11, "axes.labelsize": 10.5,
                     "xtick.labelsize": 10.5, "ytick.labelsize": 10.5})
fig = plt.figure(figsize=(8.6, 5.1))
grid = fig.add_gridspec(2, 3, left=.07, right=.985, bottom=.12, top=.92,
                        wspace=.40, hspace=.54)
axes = [fig.add_subplot(grid[:, 0]), fig.add_subplot(grid[0, 1]),
        fig.add_subplot(grid[0, 2]), fig.add_subplot(grid[1, 1]), fig.add_subplot(grid[1, 2])]
and_rows, or_rows = ca.observations(initial, 128), ca.observations(initial, 254)
panels = [(micro, "(a) Rule 146", True), (and_rows, "(b) AND readout", False),
          (ca.evolve(and_rows[0], 40, 128), "(c) Rule 128", False),
          (or_rows, "(d) OR readout", False),
          (ca.evolve(or_rows[0], 40, 182), "(e) Rule 182", False)]
for ax, (rows, title, microscopic) in zip(axes, panels):
    values = np.array(rows)
    ax.imshow(values, cmap=ListedColormap(["white", "#202B34"]), vmin=0, vmax=1,
              interpolation="nearest", aspect="auto")
    ax.set_title(title, loc="left", pad=8)
    ax.set_xlabel("Cell" if microscopic else "Block")
    ax.set_ylabel("Microsteps" if microscopic else "Coarse steps")
    ax.set_xticks([0, values.shape[1] - 1])
    ax.set_yticks([0, (values.shape[0] - 1) // 2, values.shape[0] - 1])
    ax.tick_params(length=2, pad=3)
    for spine in ax.spines.values():
        spine.set_color("#AAB1B7")
        spine.set_linewidth(.5)
if args.figcheck_dir:
    sys.path.insert(0, str(args.figcheck_dir))
    import overlap
    issues = overlap.check(fig, placed_frac=.98, textwidth_in=5.3, min_pt=6,
                           name="ca-coarse-graining", check_clipping=True)
    if issues:
        raise RuntimeError("; ".join(issues))
fig.savefig(target / "ca_coarse_graining.pdf")
fig.savefig(target / "ca_coarse_graining.png", dpi=180)
plt.close(fig)
print(f"Rendered five panels in {target}.")
