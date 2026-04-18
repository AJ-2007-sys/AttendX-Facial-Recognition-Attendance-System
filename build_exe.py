from PyInstaller.__main__ import run
import os
import sys

def build_executable():
    """
    Builds a standalone executable for the Face Recognition application using PyInstaller.
    """
    print("Starting PyInstaller build process...")
    print("WARNING: Building an executable with OpenCV, TensorFlow, and DeepFace will take significant time and result in a large file (~1-2GB).")
    
    # We need to collect some hidden imports for DeepFace and OpenCV
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
        'tkinter'
    ]
    
    # Format hidden imports for PyInstaller arguments
    hidden_import_args = []
    for imp in hidden_imports:
        hidden_import_args.extend(['--hidden-import', imp])
        
    # Build arguments
    args = [
        'main.py',                    # Main entry point
        '--name=FaceRecognitionApp',  # Name of the executable
        '--onedir',                   # Create a directory containing the executable and libraries (faster startup than --onefile)
        '--windowed',                 # Don't show the console window (since it's a GUI app)
        '--icon=NONE',                # Optional: Add path to an .ico file here if you have one
        '--clean'                     # Clean PyInstaller cache
    ] + hidden_import_args

    print(f"Running PyInstaller with arguments: {args}")
    run(args)
    
    print("\nBuild Complete!")
    print("Your packaged application is located in the 'dist/FaceRecognitionApp' folder.")
    print("You can zip this entire folder and share it with others.")
    print("Note: They will not need Python installed to run 'FaceRecognitionApp.exe' inside that folder.")

if __name__ == '__main__':
    build_executable()
