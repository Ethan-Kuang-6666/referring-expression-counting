"""
Visualizes point annotations from annotations_with_converses.json overlaid
on REC-8K images. Saves one output image per expression with points drawn
as red circles and the expression label in the title.

Output: visualizations_converses/<image_stem>/<expression>.jpg
"""

import json
import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from PIL import Image

ANNO_FILE = "anno/annotations_with_converses.json"
IMG_DIR = "data_root/rec-8k"
OUT_DIR = "visualizations_converses"

with open(ANNO_FILE) as f:
    anno = json.load(f)

img_files = [f for f in os.listdir(IMG_DIR) if f.endswith('.jpg')]

for img_name in sorted(img_files):
    if img_name not in anno:
        print(f"No annotations for {img_name}, skipping.")
        continue

    img = Image.open(os.path.join(IMG_DIR, img_name))
    exprs = anno[img_name]
    out_subdir = os.path.join(OUT_DIR, os.path.splitext(img_name)[0])
    os.makedirs(out_subdir, exist_ok=True)

    for expr, data in exprs.items():
        pts = data['points']
        fig, ax = plt.subplots(figsize=(10, 8))
        ax.imshow(img)

        if pts:
            ax.scatter([p[0] for p in pts], [p[1] for p in pts],
                       s=40, c='red', edgecolors='white', linewidths=0.8, zorder=5)
            ax.set_title(f"{expr}  ({len(pts)} objects)", fontsize=11, pad=8)
        else:
            ax.set_title(f"{expr}  (0 objects — empty complement)",
                         fontsize=11, pad=8, color='gray')

        ax.axis('off')
        plt.tight_layout()

        safe_name = expr.replace('/', '_').replace(' ', '_')[:80]
        plt.savefig(os.path.join(out_subdir, f"{safe_name}.jpg"), dpi=150, bbox_inches='tight')
        plt.close()

    print(f"Saved {len(exprs)} visualizations → {out_subdir}/")

print(f"\nDone. Output in: {OUT_DIR}/")
