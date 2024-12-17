from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import os
import pandas as pd

app = FastAPI()

EVENTS_FOLDER = 'Events'
READINGS_FOLDER = "C:/Users/Arafat/Documents/Research - Wilo/Fast-API-Server2.0/readings"

# Mount static files directory
app.mount("/static", StaticFiles(directory="C:/Users/Arafat/Documents/Research - Wilo/Fast-API-Server2.0/static"), name="static")

@app.get("/")
async def read_index():
    return FileResponse('C:/Users/Arafat/Documents/Research - Wilo/Fast-API-Server2.0/static/index.html')

@app.get("/log")
async def read_log():
    return 'Hello World'

@app.post("/create_folder/")
async def create_folder(name: str = Form(...)):
    # Check if the Events folder exists
    if not os.path.exists(EVENTS_FOLDER):
        os.makedirs(EVENTS_FOLDER)
    
    # Create a subfolder with the provided name
    folder_path = os.path.join(EVENTS_FOLDER, name)

    if not name.strip():  # Check if the input is empty or consists of only whitespace
        return HTMLResponse(content=f"""
        <html>
            <script>
                console.log("Cannot leave the Event name blank.");
                window.location.href = "/";
            </script>
            <body>
                <p>Cannot leave the Event name blank.</p>
            </body>
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
    """List all CSV files in the data directory."""
    try:
        files = [f for f in os.listdir(READINGS_FOLDER) if f.endswith('.csv')]
        return {'files': files}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get('/readings/{file_name}')
async def read_csv(file_name: str):
    """Read the CSV file and return its content as JSON."""
    file_path = os.path.join(READINGS_FOLDER, file_name)

    if not os.path.isfile(file_path):
        raise HTTPException(status_code=404, detail='File not found')

    try:
        # Read the CSV file using pandas
        df = pd.read_csv(file_path)
        # Convert DataFrame to JSON format
        readings = df.to_dict(orient='records')
        return {'readings': readings}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=2121)
