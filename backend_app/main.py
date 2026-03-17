#from fastapi import FastAPI, UploadFile, File, BackgroundTasks
#from fastapi.responses import FileResponse
#import os
#import argparse
#import uuid
#from pipeline import run_pipeline
#
#app = FastAPI()
#
#UPLOAD_DIR = "uploads"
#OUTPUT_DIR = "outputs"
#
#@app.post("/upload/")
#async def upload_images(background_tasks: BackgroundTasks,
#                        files: list[UploadFile] = File(...)):
#
#    job_id = str(uuid.uuid4())
#    job_folder = os.path.join(UPLOAD_DIR, job_id)
#    os.makedirs(job_folder, exist_ok=True)
#
#    for file in files:
#        contents = await file.read()
#        with open(os.path.join(job_folder, file.filename), "wb") as f:
#            f.write(contents)
#
#    background_tasks.add_task(run_pipeline, job_id)
#
#    return {"job_id": job_id, "status": "processing"}
#
#
#@app.get("/status/{job_id}")
#def check_status(job_id: str):
#    model_path = f"{OUTPUT_DIR}/{job_id}/model"
#    if os.path.exists(model_path):
#        return {"status": "done"}
#    return {"status": "processing"}
#
#
#@app.get("/download/{job_id}")
#def download_model(job_id: str):
#    file_path = f"{OUTPUT_DIR}/{job_id}/model/point_cloud.ply"
#    return FileResponse(file_path)


from fastapi import FastAPI, UploadFile, File, BackgroundTasks, HTTPException
from fastapi.responses import FileResponse
from typing import List
from typing_extensions import Annotated
import os
import uuid

from pipeline import run_pipeline
from config import UPLOAD_DIR, OUTPUT_DIR

app = FastAPI(openapi_version="3.0.2")


# ==============================
# Root (optional but useful)
# ==============================
@app.get("/")
def root():
    return {"message": "3D Reconstruction API Running"}


# ==============================
# Upload Endpoint
# ==============================
@app.post("/upload/")
async def upload_images(
    background_tasks: BackgroundTasks,
    files: Annotated[List[UploadFile], File(...)]
):
    job_id = str(uuid.uuid4())
    job_folder = os.path.join(UPLOAD_DIR, job_id)

    os.makedirs(job_folder, exist_ok=True)

    for file in files:
        contents = await file.read()
        file_path = os.path.join(job_folder, file.filename)

        with open(file_path, "wb") as f:
            f.write(contents)

    background_tasks.add_task(run_pipeline, job_id)

    return {
        "job_id": job_id,
        "status": "processing"
    }


# ==============================
# Status Endpoint
# ==============================
@app.get("/status/{job_id}")
def check_status(job_id: str):

    model_path = os.path.join(OUTPUT_DIR, job_id, "model")

    if os.path.exists(model_path):
        return {"status": "done"}

    return {"status": "processing"}


# ==============================
# Download Endpoint
# ==============================
@app.get("/download/{job_id}")
def download_model(job_id: str):

    file_path = os.path.join(
        OUTPUT_DIR,
        job_id,
        "model",
        "point_cloud.ply"
    )

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Model not ready")

    return FileResponse(
        path=file_path,
        media_type="application/octet-stream",
        filename="point_cloud.ply"
    )
