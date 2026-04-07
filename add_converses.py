"""
Adds converse negations to attributes in annotations.json.

For each image, expressions sharing the same class get "not <sibling_attr>"
appended to their attribute. E.g., within an image that has both
"standing camel" (attr: "standing") and "sitting camel" (attr: "sitting"):
  "standing" -> "standing, not sitting"
  "sitting"  -> "sitting, not standing"

Skips:
  - Sibling attributes that already start with "not " (avoids double negation)
  - Negations already present in the current attribute (avoids duplicates)

Output: anno/annotations_with_converses.json
"""

import json
import re
from collections import defaultdict

INPUT_FILE = "anno/annotations.json"
OUTPUT_FILE = "anno/annotations_with_converses.json"

with open(INPUT_FILE) as f:
    anno = json.load(f)

modified_count = 0
skipped_double_neg = 0
skipped_duplicate = 0

new_anno = {}
for img, exprs in anno.items():
    # Group expression keys by class
    by_class = defaultdict(list)
    for expr_key, data in exprs.items():
        by_class[data["class"]].append(expr_key)

    new_exprs = {}
    for expr_key, data in exprs.items():
        siblings = [k for k in by_class[data["class"]] if k != expr_key]
        new_attr = data["attribute"]

        for sibling_key in siblings:
            sibling_attr = exprs[sibling_key]["attribute"]

            # Skip: sibling is already a negative attribute (would create double negation)
            if re.match(r"not\s", sibling_attr, re.IGNORECASE):
                skipped_double_neg += 1
                continue

            negation = f"not {sibling_attr}"

            # Skip: this negation is already present in the attribute
            if re.search(r"\b" + re.escape(negation) + r"\b", new_attr, re.IGNORECASE):
                skipped_duplicate += 1
                continue

            new_attr = f"{new_attr}, {negation}"
            modified_count += 1

        new_data = dict(data)
        new_data["attribute"] = new_attr
        new_exprs[expr_key] = new_data

    new_anno[img] = new_exprs

with open(OUTPUT_FILE, "w") as f:
    json.dump(new_anno, f, indent=4)

print(f"Done. Output: {OUTPUT_FILE}")
print(f"  Negations added:           {modified_count}")
print(f"  Skipped (double negation): {skipped_double_neg}")
print(f"  Skipped (already present): {skipped_duplicate}")
