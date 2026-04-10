"""
Creates annotations_with_converses.json with complement expressions added.

For each expression that has same-class siblings in an image, 2 complement
expressions are added using randomly sampled natural language negation templates
(e.g. "pen except red", "non-red pen"). The template pool is restricted per
attribute type to ensure natural phrasing.

Points for complement expressions = union of all sibling points, with
cross-type near-duplicates (within 2px) merged to their average coordinate
to avoid double-counting the same physical object.

Original expressions and their points are preserved unchanged.

Output: anno/annotations_with_converses.json
Seed: 42 (reproducible)
"""

import json
import random
import numpy as np
from collections import defaultdict

INPUT_FILE = "anno/annotations.json"
OUTPUT_FILE = "anno/annotations_with_converses.json"
SEED = 42
DEDUP_THRESHOLD = 2.0  # pixels, cross-type only

# Template ID -> (expression name format, attribute format)
# {c} = class, {a} = attribute
TEMPLATES = {
    1: ("{c} except {a}",       "except {a}"),
    2: ("{c} not {a}",          "not {a}"),
    3: ("{c} other than {a}",   "other than {a}"),
    4: ("{c} excluding {a}",    "excluding {a}"),
    5: ("non-{a} {c}",          "non-{a}"),
    6: ("{c} that is not {a}",  "that is not {a}"),
    7: ("{c} without {a}",      "without {a}"),
}

# Per-type template pools (natural language constraints)
# non- (5): single-word adjective types only
# without (7): clothing/accessory only
# other than (3) / excluding (4): excluded from clothing/accessory (unnatural)
TYPE_POOL = {
    'color':       [1, 2, 3, 4, 5, 6],
    'location':    [1, 2, 3, 4, 6],
    'material':    [1, 2, 3, 4, 5, 6],
    'variety':     [1, 2, 3, 4, 6],
    'size':        [1, 2, 3, 4, 5, 6],
    'action':      [1, 2, 3, 4, 6],
    'orientation': [1, 2, 3, 4, 6],
    'clothing':    [1, 2, 6, 7],
    'accessory':   [1, 2, 6, 7],
    'age':         [1, 2, 3, 4, 5, 6],
    'gender':      [1, 2, 3, 4, 5, 6],
}


def dedup_union(sibling_data):
    """
    Union points from sibling expressions. Merge cross-type point pairs
    within DEDUP_THRESHOLD px to their coordinate average.

    sibling_data: list of {'points': [[x,y], ...], 'type': str}
    Returns: list of [x, y]
    """
    # Flatten to (x, y, type_tag)
    flat = []
    for d in sibling_data:
        for p in d['points']:
            flat.append([p[0], p[1], d['type']])

    if not flat:
        return []

    n = len(flat)
    coords = np.array([[p[0], p[1]] for p in flat], dtype=float)
    merged = [False] * n
    result = []

    for i in range(n):
        if merged[i]:
            continue
        group = [i]
        for j in range(i + 1, n):
            if merged[j]:
                continue
            if flat[i][2] == flat[j][2]:  # same type — different objects, skip
                continue
            dist = np.linalg.norm(coords[i] - coords[j])
            if dist <= DEDUP_THRESHOLD:
                group.append(j)
                merged[j] = True
        merged[i] = True
        avg = coords[group].mean(axis=0)
        result.append([round(float(avg[0]), 2), round(float(avg[1]), 2)])

    return result


def apply_template(tid, cls, attr):
    expr_fmt, attr_fmt = TEMPLATES[tid]
    return expr_fmt.format(c=cls, a=attr), attr_fmt.format(a=attr)


rng = random.Random(SEED)

with open(INPUT_FILE) as f:
    anno = json.load(f)

new_anno = {}
complement_count = 0
total_pts_before = 0
total_pts_after = 0

for img, exprs in anno.items():
    by_class = defaultdict(list)
    for expr_key, data in exprs.items():
        by_class[data['class']].append(expr_key)

    new_exprs = {}  # originals not included

    for expr_key, data in exprs.items():
        cls = data['class']
        attr = data['attribute']
        typ = data['type']
        siblings = [k for k in by_class[cls] if k != expr_key]

        pool = TYPE_POOL.get(typ, [1, 2, 6])
        tid = rng.choice(pool)
        new_key, new_attr = apply_template(tid, cls, attr)

        if not siblings:
            # No same-class siblings: complement is empty (all objects of this
            # class in the image already belong to this expression)
            new_exprs[new_key] = {
                'class': cls,
                'attribute': new_attr,
                'points': [],
                'type': typ,
            }
        else:
            sibling_data = [{'points': exprs[s]['points'], 'type': exprs[s]['type']}
                            for s in siblings]

            pts_before = sum(len(d['points']) for d in sibling_data)
            union_pts = dedup_union(sibling_data)
            total_pts_before += pts_before
            total_pts_after += len(union_pts)

            new_exprs[new_key] = {
                'class': cls,
                'attribute': new_attr,
                'points': union_pts,
                'type': typ,
            }

        complement_count += 1

    new_anno[img] = new_exprs

with open(OUTPUT_FILE, 'w') as f:
    json.dump(new_anno, f, indent=4)

print(f"Done. Output: {OUTPUT_FILE}")
print(f"  Complement expressions added:    {complement_count}")
print(f"  Points merged via cross-type dedup: {total_pts_before - total_pts_after}")
