import os
import numpy as np
import trimesh
import cv2
import torch
from PIL import Image
from sam2.build_sam import build_sam2
from sam2.sam2_image_predictor import SAM2ImagePredictor

def project_points(points, T, intrinsics):
    """
    Projects 3D points to 2D using extrinsic matrix T and intrinsic matrix.
    """
    # World to Camera
    R = T[:3, :3]
    t = T[:3, 3]
    
    pts_cam = (R @ points.T).T + t
    
    # Camera to Pixel
    fx, fy, cx, cy = intrinsics
    x = pts_cam[:, 0] / pts_cam[:, 2]
    y = pts_cam[:, 1] / pts_cam[:, 2]
    
    u = fx * x + cx
    v = fy * y + cy
    
    return np.stack([u, v], axis=1), pts_cam[:, 2]

def run_segmentation(job_id, dataset_path, model_cfg="sam2_hiera_l.yaml", sam2_checkpoint="checkpoints/sam2_hiera_large.pt"):
    input_dir = f"uploads/{job_id}"
    output_dir = os.path.join(dataset_path, "masks")
    os.makedirs(output_dir, exist_ok=True)

    # 1. Load MASt3R output
    scene_path = f"outputs/{job_id}/mast3r/reconstruction.glb" # Adjust path as needed
    if not os.path.exists(scene_path):
        print(f"MASt3R output not found at {scene_path}")
        return

    scene = trimesh.load(scene_path)
    
    # 2. Extract Points
    all_points = []
    for geom in scene.geometry.values():
        if hasattr(geom, "vertices"):
            all_points.append(np.asarray(geom.vertices))
    points_3d = np.concatenate(all_points)

    # 3. Extract Cameras
    cameras = []
    for node in scene.graph.nodes:
        transform, _ = scene.graph[node]
        if isinstance(transform, np.ndarray) and transform.shape == (4, 4):
            cameras.append(transform)

    # 4. Initialize SAM 2
    device = "cuda" if torch.cuda.is_available() else "cpu"
    predictor = SAM2ImagePredictor(build_sam2(model_cfg, sam2_checkpoint, device=device))

    # 5. Process each image
    image_files = sorted([f for f in os.listdir(input_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg'))])
    
    # Standard Pinhole assumption if not provided
    # (Matches current mast3r_to_colmap.py defaults)
    width, height = 512, 384
    fx, fy, cx, cy = 500, 500, 256, 192
    intrinsics = (fx, fy, cx, cy)

    for i, img_name in enumerate(image_files):
        if i >= len(cameras): break
        
        img_path = os.path.join(input_dir, img_name)
        image = cv2.imread(img_path)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # Project points to this camera
        pts_2d, depths = project_points(points_3d, cameras[i], intrinsics)
        
        # Filter points: 
        # Only keep points that land inside the image and are in front of the camera
        valid = (pts_2d[:, 0] >= 0) & (pts_2d[:, 0] < image.shape[1]) & \
                (pts_2d[:, 1] >= 0) & (pts_2d[:, 1] < image.shape[0]) & \
                (depths > 0)
        
        input_points = pts_2d[valid]
        
        # Heuristic: Sort by depth and take middle-range points to avoid outliers/background
        # Or just take top N points for performance
        if len(input_points) > 50:
            idx = np.random.choice(len(input_points), 50, replace=False)
            input_points = input_points[idx]

        input_labels = np.ones(len(input_points)) # All are positive prompts

        # Predict Mask
        predictor.set_image(image)
        masks, scores, _ = predictor.predict(
            point_coords=input_points,
            point_labels=input_labels,
            multimask_output=False
        )
        
        # Save Mask
        mask = (masks[0] * 255).astype(np.uint8)
        mask_path = os.path.join(output_dir, img_name.replace(".", "_") + ".png")
        cv2.imwrite(mask_path, mask)
        print(f"Generated mask for {img_name}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 2:
        run_segmentation(sys.argv[1], sys.argv[2])
    else:
        print("Usage: python segmentation.py <job_id> <dataset_path>")
