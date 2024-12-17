from fastapi import FastAPI, Form, File, UploadFile, HTTPException
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import os
import pandas as pd
import time
from io import StringIO
import zipfile
import shutil

app = FastAPI()

EVENTS_FOLDER = 'Events'
READINGS_FOLDER = "C:/Users/Arafat/Documents/Research - Wilo/Fast-API-Server2.0/readings"
uploaded_file_count = 0

# Mount static files directory
app.mount("/static", StaticFiles(directory="C:/Users/Arafat/Documents/Research - Wilo/Fast-API-Server2.0/static"), name="static")


@app.get("/")
async def read_index():
    """Serve the index.html file."""
    return FileResponse('C:/Users/Arafat/Documents/Research - Wilo/Fast-API-Server2.0/static/index.html')


@app.get("/log")
async def read_log():
    """Sample log endpoint."""
    return 'HARMS'


@app.post("/create_folder/")
async def create_folder(name: str = Form(...)):
    """Create a folder under the EVENTS_FOLDER directory."""
    if not os.path.exists(EVENTS_FOLDER):
        os.makedirs(EVENTS_FOLDER)
    
    folder_path = os.path.join(EVENTS_FOLDER, name)

    if not name.strip():
        return HTMLResponse(content=f"""
        <html>
            <script>
                alert("Cannot leave the Event name blank.");
                window.location.href = "/";
            </script>
        </html>
        """)
    elif not os.path.exists(folder_path):
        os.makedirs(folder_path)
        return HTMLResponse(content=f"""
        <html>
            <script>
                alert("Folder '{name}' created successfully in '{EVENTS_FOLDER}'.");
                window.location.href = "/";
            </script>
        </html>
        """)
    else:
        return HTMLResponse(content=f"""
        <html>
            <script>
                alert("Folder '{name}' already exists in '{EVENTS_FOLDER}'.");
                window.location.href = "/";
            </script>
        </html>
        """)


@app.get('/files')
async def list_files():
    """List all CSV files in the READINGS_FOLDER directory."""
    try:
        files = [f for f in os.listdir(READINGS_FOLDER) if f.endswith('.csv')]
        return {'files': files}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get('/readings/{file_name}')
async def read_csv(file_name: str):
    """Read a specific CSV file and return its content as JSON."""
    file_path = os.path.join(READINGS_FOLDER, file_name)

    if not os.path.isfile(file_path):
        raise HTTPException(status_code=404, detail='File not found')

    try:
        df = pd.read_csv(file_path)
        readings = df.to_dict(orient='records')
        return {'readings': readings}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/upload", status_code=201)
async def upload_csv(file: UploadFile = File(...)):
    """
    Upload a CSV file, save it in the READINGS_FOLDER, and update the count.
    """
    global uploaded_file_count
    try:
        # Read the uploaded file content
        content = await file.read()

        # Decode and parse content with pandas
        df = pd.read_csv(StringIO(content.decode('utf-8')))

        # Ensure the target folder exists
        os.makedirs(READINGS_FOLDER, exist_ok=True)

        # Generate a timestamped filename
        timestamp_str = time.strftime("%Y-%m-%d_%H-%M-%S")
        file_path = os.path.join(READINGS_FOLDER, f"{timestamp_str}.csv")

        # Save the DataFrame to a CSV file
        df.to_csv(file_path, index=False)

        # Increment the file count
        uploaded_file_count += 1

        # Return success response with the saved file path
        return JSONResponse(content={"message": f"CSV file saved to {file_path}"}, status_code=201)

    except pd.errors.EmptyDataError:
        raise HTTPException(status_code=422, detail="The uploaded CSV file is empty.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")


@app.get("/file_count")
async def get_file_count():
    """
    Return the current number of uploaded files.
    """
    return {"file_count": uploaded_file_count}

@app.post("/upload-zip", status_code=201)
async def upload_zip(file: UploadFile = File(...)):
    """
    Upload a ZIP file, extract its contents into the EVENTS_FOLDER, and return a success message.
    """
    try:
        # Ensure the EVENTS_FOLDER exists
        if not os.path.exists(EVENTS_FOLDER):
            os.makedirs(EVENTS_FOLDER)

        # Save the uploaded ZIP file temporarily
        zip_path = os.path.join(EVENTS_FOLDER, file.filename)
        with open(zip_path, 'wb') as f:
            content = await file.read()
            f.write(content)

        # Extract the contents of the ZIP file
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            # Extract all the contents into the EVENTS_FOLDER
            zip_ref.extractall(EVENTS_FOLDER)

        # Optionally, remove the ZIP file after extraction
        os.remove(zip_path)

        # Return a success message
        return {"message": f"ZIP file '{file.filename}' extracted successfully to '{EVENTS_FOLDER}'."}
    
    except zipfile.BadZipFile:
        raise HTTPException(status_code=422, detail="The uploaded file is not a valid ZIP file.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")
    
@app.get("/latest-event")
def get_latest_event():
    try:
        # Get all subfolders in the event directory sorted by modification time
        folders = sorted(
            [f for f in os.listdir(EVENTS_FOLDER) if os.path.isdir(os.path.join(EVENTS_FOLDER, f))],
            key=lambda f: os.path.getmtime(os.path.join(EVENTS_FOLDER, f)),
            reverse=True
        )
        if folders:
            latest_folder = folders[0]
            return {"latest_event": latest_folder}
        return {"latest_event": "No events found"}
    except Exception as e:
        return {"error": str(e)}

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=2121)

