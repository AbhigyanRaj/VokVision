
import os
import torch

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MAST3R_PATH = "../mast3r"
GAUSSIAN_PATH = "../gaussian-splatting"

UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
OUTPUT_DIR = os.path.join(BASE_DIR, "outputs")
TEMP_DIR = os.path.join(BASE_DIR, "temp")

DEVICE = "cuda"
IMAGE_SIZE = (1024, 768)
ITERATIONS = 7000
print(f"Using device: {DEVICE}")

