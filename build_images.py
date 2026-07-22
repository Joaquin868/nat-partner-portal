#!/usr/bin/env python3
"""Scan Images/ and write images.json (product galleries) and photos.json
(real photography, grouped by brand -> category). Counts and filenames come
from the actual files on disk, so you never report them by hand.

Photography layout:
  Images/Photography/<Brand>/<Category>/*.jpg   -> shown as a category block
  Images/Photography/<Brand>/*.jpg              -> loose files go under "General"
"""
import json, os, re

ROOT = os.path.dirname(os.path.abspath(__file__))
IMAGES_DIR = os.path.join(ROOT, "Images")
MAP_FILE = os.path.join(ROOT, "image-map.json")
OUT_FILE = os.path.join(ROOT, "images.json")
PHOTO_DIR = os.path.join(IMAGES_DIR, "Photography")
PHOTO_OUT = os.path.join(ROOT, "photos.json")
EXT = {".png", ".jpg", ".jpeg", ".webp", ".gif"}

def natural(s):
    return [int(t) if t.isdigit() else t.lower() for t in re.split(r"(\d+)", s)]

def images_in(dir_):
    out = []
    for root, _, fnames in os.walk(dir_):
        for fn in fnames:
            if os.path.splitext(fn)[1].lower() in EXT:
                rel = os.path.relpath(os.path.join(root, fn), ROOT).replace(os.sep, "/")
                out.append(rel)
    out.sort(key=natural)
    return out

# ---- product galleries (PN -> folder) ----
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
print(f"OK - {len(manifest)} products in images.json")
if missing: print("WARNING missing folders:", missing)
if empty:   print("WARNING empty folders:", empty)

# ---- photography (brand -> category) ----
photos = {}
if os.path.isdir(PHOTO_DIR):
    for brand in sorted(os.listdir(PHOTO_DIR)):
        bdir = os.path.join(PHOTO_DIR, brand)
        if not os.path.isdir(bdir):
            continue
        cats = {}
        # loose files directly in the brand folder -> "General"
        loose = sorted(
            [f for f in os.listdir(bdir)
             if os.path.isfile(os.path.join(bdir, f)) and os.path.splitext(f)[1].lower() in EXT],
            key=natural)
        if loose:
            cats["General"] = ["Images/Photography/" + brand + "/" + f for f in loose]
        # each subfolder -> its own category
        for sub in sorted(os.listdir(bdir)):
            sdir = os.path.join(bdir, sub)
            if not os.path.isdir(sdir):
                continue
            imgs = images_in(sdir)
            if imgs:
                cats[sub] = imgs
        if cats:
            photos[brand] = cats

with open(PHOTO_OUT, "w", encoding="utf-8") as f:
    json.dump(photos, f, ensure_ascii=False, indent=2)
tot = sum(len(v) for b in photos.values() for v in b.values())
print(f"OK - {tot} photos across {len(photos)} brands in photos.json")