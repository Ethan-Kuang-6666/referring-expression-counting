"""
Creates splits_with_converses.json for annotations_with_converses.json.

Inherits the image->split assignment from the original splits.json so that
images remain unique across train/val/test splits. All complement expressions
for a given image are assigned to the same split as that image.

Output: anno/splits_with_converses.json
"""

import json
from collections import defaultdict

ANNO_FILE = "anno/annotations_with_converses.json"
ORIG_SPLITS_FILE = "anno/splits.json"
OUTPUT_FILE = "anno/splits_with_converses.json"

with open(ANNO_FILE) as f:
    anno = json.load(f)

with open(ORIG_SPLITS_FILE) as f:
    orig_splits = json.load(f)

# Build image -> split mapping from original splits
img_to_split = {}
for split, entries in orig_splits.items():
    for img, expr in entries:
        img_to_split[img] = split

# Assign all expressions in new annotations to the same split as their image
new_splits = defaultdict(list)
for img, exprs in anno.items():
    split = img_to_split.get(img)
    if split is None:
        print(f"WARNING: {img} has no split assignment, skipping.")
        continue
    for expr in exprs:
        new_splits[split].append([img, expr])

with open(OUTPUT_FILE, "w") as f:
    json.dump(new_splits, f, indent=4)

print(f"Done. Output: {OUTPUT_FILE}")
for split in ("train", "val", "test"):
    entries = new_splits[split]
    imgs = set(e[0] for e in entries)
    print(f"  {split}: {len(entries)} Image-RE pairs, {len(imgs)} images")
