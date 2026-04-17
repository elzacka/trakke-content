#!/usr/bin/env python3
"""
Generate catalog.json from individual .md article files.

Run this after editing articles, before pushing to GitHub:
    python3 generate-catalog.py

The catalog includes checksums so the app only downloads changed articles.
"""

import json
import hashlib
import os
import re
from datetime import datetime, timezone

ARTICLES_DIR = "articles"
OUTPUT = "catalog.json"

CAT_MAP = {
    "Beredskap": "beredskap",
    "Dyr": "dyr",
    "Fjellvettreglene": "fjellvettreglene",
    "Førstehjelp": "forstehjelp",
    "Giftige arter": "giftigeArter",
    "Ly": "ly",
    "Mat": "mat",
    "Mentale strategier": "mentaleStrategier",
    "Nødprosedyrer": "nodprosedyrer",
    "Orientering": "orientering",
    "Rettigheter": "rettigheter",
    "Utstyr": "utstyr",
    "Vær": "vaer",
    "Vann": "vann",
    "Varme og kulde": "varme",
}

CAT_SORT = {v: k for k, v in CAT_MAP.items()}


def parse_article(filepath):
    with open(filepath, "r") as f:
        content = f.read()

    lines = content.strip().split("\n")
    if not lines:
        return None

    # Extract category from first line: "## Category Name"
    cat_display = lines[0].replace("## ", "").strip()
    category = CAT_MAP.get(cat_display, cat_display.lower())

    # Extract title from line 3: "### Title"
    title = lines[2].replace("### ", "").strip()

    # Checksum of the full file content
    checksum = hashlib.sha256(content.encode("utf-8")).hexdigest()[:16]

    # Relative path from repo root
    rel_path = os.path.relpath(filepath)

    return {
        "category": category,
        "title": title,
        "file": rel_path,
        "checksum": checksum,
    }


def main():
    articles = []

    for root, dirs, files in os.walk(ARTICLES_DIR):
        dirs.sort()
        for fname in sorted(files):
            if not fname.endswith(".md"):
                continue
            filepath = os.path.join(root, fname)
            article = parse_article(filepath)
            if article:
                articles.append(article)

    # Sort by category display name, then title
    articles.sort(key=lambda a: (CAT_SORT.get(a["category"], a["category"]), a["title"]))

    # Assign IDs and sort orders
    current_cat = None
    sort_order = 0
    for i, a in enumerate(articles):
        a["id"] = i + 1
        if a["category"] != current_cat:
            current_cat = a["category"]
            sort_order = 1
        else:
            sort_order += 1
        a["sortOrder"] = sort_order

    catalog = {
        "version": 1,
        "generated": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "articles": articles,
    }

    with open(OUTPUT, "w") as f:
        json.dump(catalog, f, ensure_ascii=False, indent=2)

    print(f"Generated {OUTPUT}: {len(articles)} articles in {len(set(a['category'] for a in articles))} categories")


if __name__ == "__main__":
    main()
