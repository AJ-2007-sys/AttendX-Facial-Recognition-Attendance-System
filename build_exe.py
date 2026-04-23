from PyInstaller.__main__ import run
import os
import sys

def build_executable():
    """
    Builds a standalone executable for the AttendX web application using PyInstaller.
    """
    print("Starting PyInstaller build process...")
    print("WARNING: Building an executable with OpenCV, TensorFlow, and DeepFace will take significant time and result in a large file (~1-2GB).")
    
    # Hidden imports needed by the AI/ML stack
    hidden_imports = [
        'deepface',
        'cv2',
        'numpy',
        'pandas',
        'tensorflow',
        'keras',
        'scipy',
        'sqlite3',
        'PIL',
        'fastapi',
        'uvicorn',
        'jinja2',
        'mediapipe',
        'ultralytics',
    ]
    
    # Format hidden imports for PyInstaller arguments
    hidden_import_args = []
    for imp in hidden_imports:
        hidden_import_args.extend(['--hidden-import', imp])
    
    # Data files to bundle
    data_args = [
        '--add-data', 'templates;templates',
        '--add-data', 'static;static',
        '--add-data', 'face_landmarker.task;.',
    ]
        
    # Build arguments
    args = [
        'app.py',                     # Main entry point (FastAPI server)
        '--name=AttendX',             # Name of the executable
        '--onedir',                   # Create a directory containing the executable and libraries
        '--console',                  # Show console (needed for Uvicorn server output)
        '--icon=NONE',                # Optional: Add path to an .ico file here if you have one
        '--clean'                     # Clean PyInstaller cache
    ] + hidden_import_args + data_args

    print(f"Running PyInstaller with arguments: {args}")
    run(args)
    
    print("\nBuild Complete!")
    print("Your packaged application is located in the 'dist/AttendX' folder.")
    print("You can zip this entire folder and share it with others.")
    print("Note: They will not need Python installed to run 'AttendX.exe' inside that folder.")

if __name__ == '__main__':
    build_executable()
