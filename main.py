from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
import os
import subprocess

app = FastAPI(version="1.0.0")

curr_dir = os.path.dirname(os.path.abspath(__file__))

def sanitize_filename(name: str) -> str:
    return name.lower().replace(" ", "_")

def generate_video_sync(title: str, description: str):
    # Synchronous wrapper around subprocess call
    try:
        subprocess.run([
            "python", "generate_video.py",
            "--model", "gemini/gemini-2.0-flash-001",
            "--helper_model", "gemini/gemini-2.0-flash-001",
            "--output_dir", "output/final",
            "--topic", title,
            "--context", description
        ], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error during video generation: {e}")

@app.get("/")
async def get_video(title: str, description: str, background_tasks: BackgroundTasks):
    sanitized_title = sanitize_filename(title)
    file_path = os.path.join(curr_dir, f"output/final/{sanitized_title}/{sanitized_title}_combined.mp4")

    if os.path.exists(file_path):
        return FileResponse(file_path, media_type="video/mp4", filename=f"{sanitized_title}.mp4")

    try:
        generate_video_sync(title, description)
        if os.path.exists(file_path):
            return FileResponse(file_path, media_type="video/mp4", filename=f"{sanitized_title}.mp4")
    except Exception as e:
        generate_video_sync(title, description)
        if os.path.exists(file_path):
            return FileResponse(file_path, media_type="video/mp4", filename=f"{sanitized_title}.mp4")
    return {"error": f"{sanitized_title} is not a valid"}
