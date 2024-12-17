
#logging_handler.py
from fastapi import APIRouter, HTTPException
import os

router = APIRouter()

LOGS_DIR = "static/logs"

if not os.path.exists(LOGS_DIR):
    os.makedirs(LOGS_DIR)

# Example logging route
@router.get("/")
async def list_logs():
    logs = os.listdir(LOGS_DIR)
    return logs

@router.get("/{log_name}")
async def get_log(log_name: str):
    log_path = os.path.join(LOGS_DIR, log_name)
    if not os.path.isfile(log_path):
        raise HTTPException(status_code=404, detail="Log file not found")
    with open(log_path, "r") as file:
        content = file.read()
    return {"log_name": log_name, "content": content}


