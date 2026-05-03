VokVision - Knowledge Transfer (KT)
=================================


Quick Summary
-------------
- The app is a Flutter mobile client that captures photos and uploads them to a Node.js API.
- The Node API stores project metadata in MongoDB, writes images to disk, and queues a BullMQ job.
- A background worker (also in Node) consumes the queue, processes reconstruction jobs, and sends an FCM push.
- The Python pipeline in backend_app/ runs MASt3R and Gaussian Splatting for 3D reconstruction.

System Architecture
-------------------
1) Mobile (Flutter)
    - Entry: lib/main.dart, lib/src/app.dart
    - Routing: lib/src/routing/app_router.dart (GoRouter)
    - Features:
      - Onboarding and auth screens
      - Capture flow (camera + sensors + upload)
      - Project creation UI

2) API + Worker (Node/Express + BullMQ)
    - Entry: backend/src/server.ts -> backend/src/app.ts
    - Auth: SMS OTP via Twilio
    - Projects: MongoDB model, upload endpoint, queue enqueue
    - Worker: BullMQ processor that updates project status and fires FCM

3) Reconstruction Pipeline (Python)
    - FastAPI service: backend_app/main.py
    - Pipeline: backend_app/pipeline.py
    - Uses MASt3R and Gaussian Splatting from the repo directories

Runtime Flow (Actual Code Path)
-------------------------------
1) User signs in with OTP
    - Flutter: lib/src/features/authentication/data/auth_repository.dart
    - Node: backend/src/modules/auth/auth.controller.ts, backend/src/modules/auth/twilio.service.ts

2) User creates a project + captures images
    - Flutter: lib/src/features/capture/presentation/capture_screen.dart
    - API: POST /api/v1/projects (create) and POST /api/v1/projects/:id/upload
    - Storage: images saved under uploads/<projectId>/

3) Processing job is queued
    - Queue: backend/src/shared/utils/queue.ts
    - Worker: backend/src/modules/jobs/processor.worker.ts
    - Worker updates project status and sends FCM notification

4) Mobile receives FCM
    - Flutter: Firebase Messaging set up in lib/main.dart and capture_screen
    - FCM payload includes downloadUrl for model retrieval

Python Pipeline Flow
--------------------
backend_app/ provides a FastAPI service that can accept image uploads and run:
1) MASt3R pose estimation
2) Convert to 3DGS dataset
3) Train Gaussian Splatting model

Key Implementations
-------------------
Mobile (Flutter)
- Auth: OTP request/verify via Dio
  - lib/src/features/authentication/data/auth_repository.dart
  - lib/src/features/authentication/presentation/auth_screen.dart
- Capture:
  - Camera + accelerometer stability check
  - Auto-capture threshold and target photo count
  - Upload via Dio multipart
  - lib/src/features/capture/presentation/capture_screen.dart

Backend (Node/Express)
- API routes:
  - POST /api/v1/auth/otp/request
  - POST /api/v1/auth/otp/verify
  - POST /api/v1/projects
  - GET /api/v1/projects
  - GET /api/v1/projects/:id
  - POST /api/v1/projects/:id/upload
- Storage: multer writes to uploads/<projectId>/
- Queue: BullMQ 'reconstruction-processing'
- Worker: marks project completed, sets modelUrl, sends FCM

Backend (Python)
- FastAPI endpoints:
  - POST /upload/
  - GET /status/{job_id}
  - GET /download/{job_id}
- Pipeline: MASt3R -> Convert -> Gaussian Splatting

Local Setup (Minimal)
---------------------
1) Flutter app
        - Configure base URLs in:
      - lib/src/features/authentication/data/auth_repository.dart
      - lib/src/features/reconstruction/data/project_repository.dart

2) Node API + Worker
    - backend/package.json scripts:
      - npm run dev
    - Needs:
      - MongoDB
      - Redis (BullMQ)
      - Twilio credentials
      - Firebase Admin service account JSON

3) Python pipeline (optional)
    - backend_app/main.py runs FastAPI
    - backend_app/pipeline.py expects MASt3R and gaussian-splatting directories

Configuration and Secrets
-------------------------
Node backend reads from .env (not in repo):
- PORT, NODE_ENV
- MONGODB_URI
- TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_VERIFY_SERVICE_SID
- JWT_SECRET, JWT_EXPIRES_IN
- REDIS_URL
- LOCAL_IP

The backend expects firebase-service-account.json at repo root.

Data and Artifacts
------------------
- uploads/ (Node): images uploaded by clients (per project)
- backend_app/uploads/ and backend_app/outputs/ (Python): pipeline IO
- outputs/ is not tracked; create locally before running pipeline

Pipeline Deep Dive (CV Concepts)
--------------------------------
This section explains the end-to-end pipeline as it is intended to work, including the computer vision concepts behind each stage. The current codebase has a split between the Node worker and the Python pipeline; both are described here.

Stage 0: Capture and Upload (Mobile)
- The app captures a multi-view image set of the object/scene.
- For reliable reconstruction, images should have high overlap, varied viewpoints, and minimal motion blur. This increases feature matchability and triangulation quality.
- Images are uploaded as multipart form data to the Node API and stored on disk under uploads/<projectId>/.

Stage 1: Camera Pose Estimation (MASt3R)
- The pipeline uses MASt3R to estimate camera poses and sparse scene structure.
- CV concept: multi-view geometry and structure-from-motion (SfM).
- MASt3R finds correspondences across images and solves for camera extrinsics and a sparse 3D point cloud.
- Output: camera parameters and a sparse reconstruction that anchors all views in a shared coordinate frame.

Stage 2: Dataset Conversion (SfM -> 3DGS format)
- The MASt3R output is converted into the input format required by Gaussian Splatting.
- CV concept: consistent camera intrinsics/extrinsics and view metadata aligned to the 3D coordinate system.
- Output: a dataset folder with images, camera poses, and metadata for neural rendering optimization.

Stage 3: Gaussian Splatting Optimization
- The Gaussian Splatting training step fits a collection of 3D Gaussians (position, scale, opacity, color) to explain the input views.
- CV concept: differentiable rendering and photometric loss minimization.
- The optimizer renders novel views from the Gaussian scene and minimizes the error vs. ground-truth images.
- Output: a dense, view-dependent scene representation, typically exported as .splat, .ply, or .glb.

Stage 4: Notification and Delivery
- The Node worker updates the project status and sends an FCM push.
- The payload includes a downloadUrl for model retrieval.

Stage 5: Editing / AI Transform
- The editing layer supports high-level transformations like resize/reshape, material changes, and object-level edits.
- In CV terms, this maps to:
    - Geometry editing: mesh/point cloud deformation, scaling, smoothing, or topology changes.
    - Appearance editing: texture or color changes, relighting, or material edits.
    - Semantic editing: object-level segmentation followed by targeted edits to a subset of points/gaussians.

