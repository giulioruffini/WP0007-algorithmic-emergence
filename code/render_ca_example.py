"""Render the checked CA comparison used in the manuscript (Figure 6).

Every cell is drawn as a vector rectangle with square geometry: the rule-146 run spans the
full width, and the four coarse panels sit below it in two rows (AND pair, OR pair).
``--variant diff`` additionally marks, in panel (e), the cells where the rule-182 run differs
from the OR record.
"""
from pathlib import Path
import argparse
import sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
from matplotlib import font_manager
import numpy as np
import ca_examples as ca

root = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--output-dir", type=Path,
                    default=root / ("entropy/figures" if (root / "entropy").is_dir() else "figures"))
parser.add_argument("--figcheck-dir", type=Path,
                    help="optional directory containing the figcheck overlap.py checker")
parser.add_argument("--variant", choices=["clean", "diff"], default="clean",
                    help="'diff' marks cells of the rule-182 run that differ from the OR record")
parser.add_argument("--name", default="ca_coarse_graining", help="output basename")
args = parser.parse_args()
target = args.output_dir
target.mkdir(parents=True, exist_ok=True)

available = {f.name for f in font_manager.fontManager.ttflist}
family = next((f for f in ["Helvetica Neue", "Helvetica", "Arial", "DejaVu Sans"] if f in available),
              "DejaVu Sans")
plt.rcParams.update({"font.family": family, "font.size": 11, "axes.titlesize": 11.5,
                     "axes.labelsize": 10.5, "xtick.labelsize": 10.5, "ytick.labelsize": 10.5,
                     "pdf.fonttype": 42})
INK, DIFF, FRAME, GREY = "#1F2A44", "#D7532F", "#9AA3AB", "#4A5561"


def rectangles(mask):
    """Merge horizontal runs of True cells into rectangles (data coordinates)."""
    verts = []
    for y, row in enumerate(mask):
        x, n = 0, len(row)
        while x < n:
            if row[x]:
                x0 = x
                while x < n and row[x]:
                    x += 1
                verts.append([(x0, y), (x, y), (x, y + 1), (x0, y + 1)])
            else:
                x += 1
    return verts


def raster(ax, values, diff=None):
    values = np.asarray(values, dtype=bool)
    h, w = values.shape
    ax.add_collection(PolyCollection(rectangles(values), facecolors=INK, edgecolors="none",
                                     antialiaseds=False))
    if diff is not None:
        ax.add_collection(PolyCollection(rectangles(np.asarray(diff, dtype=bool)), facecolors=DIFF,
                                         edgecolors="none", antialiaseds=False))
    ax.set_xlim(0, w)
    ax.set_ylim(h, 0)                      # time increases downward
    ax.set_xticks([0.5, w - 0.5])
    ax.set_xticklabels(["0", str(w - 1)])
    ax.set_yticks([0.5, h / 2, h - 0.5])
    ax.set_yticklabels(["0", str((h - 1) // 2), str(h - 1)])
    ax.tick_params(length=2, pad=2.5, color=FRAME)
    for spine in ax.spines.values():
        spine.set_color(FRAME)
        spine.set_linewidth(.6)


initial = ca.initial_state(7)
micro = ca.evolve(initial, ca.BLOCK * ca.COARSE_STEPS, 146)
and_rows, or_rows = ca.observations(initial, 128), ca.observations(initial, 254)
run128, run182 = ca.evolve(and_rows[0], 40, 128), ca.evolve(or_rows[0], 40, 182)
diff182 = (np.array(run182) != np.array(or_rows)) if args.variant == "diff" else None
mh, mw = np.array(micro).shape
ch, cw = np.array(and_rows).shape

# Geometry in inches: square cells throughout.
W, L, R, TOP = 8.6, 0.62, 0.12, 0.34
U = W - L - R
a_h = U * mh / mw
gap_x = 0.78
pw = (U - gap_x) / 2
ph = pw * ch / cw
head, xlab, row_gap = 0.54, 0.45, 0.34
H = TOP + a_h + xlab + 2 * (head + ph) + row_gap + xlab
fig = plt.figure(figsize=(W, H))


def axes_at(x, y_top, w, h):
    """Axes placed by inches from the top-left corner."""
    return fig.add_axes([x / W, (H - y_top - h) / H, w / W, h / H])


y = TOP
ax_a = axes_at(L, y, U, a_h)
raster(ax_a, micro)
ax_a.set_title("(a) Rule 146", loc="left", pad=6)
ax_a.set_xlabel("cell", labelpad=1)
ax_a.set_ylabel("microstep")
y += a_h + xlab
rows = [("AND projection: 1 only for 111",
         [("(b) AND readout", and_rows, None), ("(c) Rule 128", run128, None)]),
        ("OR projection: 1 for any nonzero triple",
         [("(d) OR readout", or_rows, None), ("(e) Rule 182", run182, diff182)])]
for r, (header, panels) in enumerate(rows):
    y += head
    fig.text(L / W, (H - (y - 0.40)) / H, header, ha="left", va="bottom", fontsize=10.5, color=GREY)
    for j, (title, data, diff) in enumerate(panels):
        ax = axes_at(L + j * (pw + gap_x), y, pw, ph)
        raster(ax, data, diff)
        ax.set_title(title, loc="left", pad=5)
        if j == 0:
            ax.set_ylabel("coarse step")
        if r == 1:
            ax.set_xlabel("block", labelpad=1)
    y += ph + (row_gap if r == 0 else xlab)

if args.figcheck_dir:
    sys.path.insert(0, str(args.figcheck_dir))
    import overlap
    issues = overlap.check(fig, placed_frac=.98, textwidth_in=5.3, min_pt=6,
                           name="ca-coarse-graining", check_clipping=True)
    if issues:
        raise RuntimeError("; ".join(issues))
fig.savefig(target / f"{args.name}.pdf")
fig.savefig(target / f"{args.name}.png", dpi=180)
plt.close(fig)
print(f"Rendered five panels ({args.variant}, font {family}, {W:.1f} x {H:.2f} in) in {target}.")
