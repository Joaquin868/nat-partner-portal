#!/usr/bin/env python3
"""Scan Images/ and write images.json for the portal.
Reads image-map.json (PN -> folder under Images/). Counts and filenames
come from the actual files on disk, so you never report them by hand."""
import json, os, re

ROOT = os.path.dirname(os.path.abspath(__file__))
IMAGES_DIR = os.path.join(ROOT, "Images")
MAP_FILE = os.path.join(ROOT, "image-map.json")
OUT_FILE = os.path.join(ROOT, "images.json")
EXT = {".png", ".jpg", ".jpeg", ".webp", ".gif"}

def natural(s):
    return [int(t) if t.isdigit() else t.lower() for t in re.split(r"(\d+)", s)]

with open(MAP_FILE, encoding="utf-8") as f:
    mapping = json.load(f)

manifest, missing, empty = {}, [], []
for pn, folder in mapping.items():
    folder = folder.strip().strip("/")
    d = os.path.join(IMAGES_DIR, *folder.split("/"))
    if not os.path.isdir(d):
        missing.append((pn, folder)); continue
    files = sorted([x for x in os.listdir(d) if os.path.splitext(x)[1].lower() in EXT], key=natural)
    if not files:
        empty.append((pn, folder)); continue
    manifest[pn] = {"folder": "Images/" + folder,
                    "images": ["Images/" + folder + "/" + x for x in files]}

with open(OUT_FILE, "w", encoding="utf-8") as f:
    json.dump(manifest, f, ensure_ascii=False, indent=2)

print(f"OK - {len(manifest)} products written to images.json")
if missing: print("WARNING missing folders:", missing)
if empty:   print("WARNING empty folders:", empty)
