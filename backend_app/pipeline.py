#import os
#import subprocess
#from config import MAST3R_PATH, GAUSSIAN_PATH
#
#def run_pipeline(job_id):
#    input_folder = f"uploads/{job_id}"
#    output_folder = f"outputs/{job_id}"
#    os.makedirs(output_folder, exist_ok=True)
#
#    # Step 1 — Run MASt3R
#    subprocess.run([
#        "python",
#        f"{MAST3R_PATH}/run_mast3r.py",
#        "--input_dir", input_folder,
#        "--output_dir", f"{output_folder}/mast3r",
#        "--mode", "sfm"
#    ])
#
#    # Step 2 — Convert output to 3DGS format
#    subprocess.run([
#        "python",
#        "convert_to_3dgs.py",
#        "--input", f"{output_folder}/mast3r",
#        "--output", f"{output_folder}/dataset"
#    ])
#
#    # Step 3 — Train Gaussian Splatting
#    subprocess.run([
#        "python",
#        f"{GAUSSIAN_PATH}/train.py",
#        "-s", f"{output_folder}/dataset",
#        "--model_path", f"{output_folder}/model",
#        "--iterations", "5000"
#    ])
import os
import subprocess
import shutil
import sys

from config import MAST3R_PATH, GAUSSIAN_PATH


def run_command(command, stage_name):
    """
    Runs a subprocess command safely and stops if it fails.
    """
    print(f"\n===== Running {stage_name} =====\n")
    print("Command:", " ".join(command))

    result = subprocess.run(command)

    if result.returncode != 0:
        print(f"\n❌ {stage_name} failed.")
        sys.exit(1)

    print(f"\n✅ {stage_name} completed successfully.\n")


def run_pipeline(job_id):

    # ==============================
    # Setup Paths
    # ==============================

    input_folder = os.path.join("uploads", job_id)
    output_folder = os.path.join("outputs", job_id)

    mast3r_output = os.path.join(output_folder, "mast3r")
    dataset_output = os.path.join(output_folder, "dataset")
    model_output = os.path.join(output_folder, "model")

    if not os.path.exists(input_folder):
        raise ValueError(f"Input folder does not exist: {input_folder}")

    os.makedirs(output_folder, exist_ok=True)

    print(f"\n🚀 Starting 3D Reconstruction Pipeline for: {job_id}")
    print(f"Input folder: {input_folder}")
    print(f"Output folder: {output_folder}")

    # ==============================
    # STEP 1 — Run MASt3R
    # ==============================

    mast3r_command = [
        "python",
        os.path.join(MAST3R_PATH, "kapture_mast3r_mapping.py"),
        "--input_dir", input_folder,
        "--output_dir", mast3r_output,
        "--mode", "sfm"
    ]

    run_command(mast3r_command, "MASt3R Pose Estimation")

    # Check if output exists
    if not os.path.exists(mast3r_output):
        raise RuntimeError("MASt3R output folder not created.")

    # ==============================
    # STEP 2 — Convert to 3DGS format
    # ==============================

    convert_command = [
        "python",
        "convert_to_3dgs.py",
        "--input", mast3r_output,
        "--output", dataset_output
    ]

    run_command(convert_command, "Convert to 3DGS Dataset")

    if not os.path.exists(dataset_output):
        raise RuntimeError("Dataset conversion failed.")

    # ==============================
    # STEP 3 — Automated Segmentation (Innovation)
    # ==============================
    segment_command = [
        "python",
        "segmentation.py",
        job_id,
        dataset_output
    ]

    run_command(segment_command, "SAM 2 Automated Object Isolation")

    # ==============================
    # STEP 4 — Train Gaussian Splatting
    # ==============================

    gaussian_command = [
        "python",
        os.path.join(GAUSSIAN_PATH, "train.py"),
        "-s", dataset_output,
        "--model_path", model_output,
        "--iterations", "5000"
    ]

    run_command(gaussian_command, "Gaussian Splatting Training")

    if not os.path.exists(model_output):
        raise RuntimeError("Gaussian model training failed.")

    print("\n🎉 FULL PIPELINE COMPLETED SUCCESSFULLY!\n")
