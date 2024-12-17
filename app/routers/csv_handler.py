
#csv_handler.py
from fastapi import APIRouter, HTTPException, File, UploadFile
from typing import List
import pandas as pd
import os

router = APIRouter()

READINGS_DIR = "static/readings"

if not os.path.exists(READINGS_DIR):
    os.makedirs(READINGS_DIR)

@router.get("/", response_model=List[str])
async def list_files():
    files = os.listdir(READINGS_DIR)
    return files

@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    file_path = os.path.join(READINGS_DIR, file.filename)
    with open(file_path, "wb") as f:
        f.write(await file.read())
    return {"filename": file.filename}

@router.get("/{filename}")
async def read_file(filename: str):
    file_path = os.path.join(READINGS_DIR, filename)
    if not os.path.isfile(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    df = pd.read_csv(file_path)
    return df.to_dict(orient="records")

