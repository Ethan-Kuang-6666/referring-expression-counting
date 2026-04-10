"""
Visualizes point annotations from annotations_with_converses.json overlaid
on REC-8K images. Saves one output image per expression with points drawn
as red circles and the expression label in the title.

Output: visualizations/<image_stem>/<expression>.jpg
"""

import json
import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from PIL import Image

ANNO_FILE = "anno/annotations.json"
IMG_DIR = "data_root/rec-8k"
OUT_DIR = "visualizations"

COLORS = ['red', 'cyan', 'lime', 'yellow', 'magenta', 'orange', 'deepskyblue', 'white']

with open(ANNO_FILE) as f:
    anno = json.load(f)

img_files = [f for f in os.listdir(IMG_DIR) if f.endswith('.jpg')]
os.makedirs(OUT_DIR, exist_ok=True)

for img_name in sorted(img_files):
    if img_name not in anno:
        print(f"No annotations for {img_name}, skipping.")
        continue

    img = Image.open(os.path.join(IMG_DIR, img_name))
    exprs = anno[img_name]

    fig, ax = plt.subplots(figsize=(12, 9))
    ax.imshow(img)

    for i, (expr, data) in enumerate(exprs.items()):
        pts = data['points']
        color = COLORS[i % len(COLORS)]
        if pts:
            ax.scatter([p[0] for p in pts], [p[1] for p in pts],
                       s=40, c=color, edgecolors='black', linewidths=0.5,
                       zorder=5, label=f"{expr} ({len(pts)})")
        else:
            ax.scatter([], [], c=color, s=40, label=f"{expr} (0 — empty complement)")

    ax.legend(loc='upper right', fontsize=8, framealpha=0.7,
              markerscale=1.2, bbox_to_anchor=(1, 1))
    ax.axis('off')
    plt.tight_layout()

    out_path = os.path.join(OUT_DIR, img_name)
    plt.savefig(out_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"Saved → {out_path}")

print(f"\nDone. Output in: {OUT_DIR}/")
