import os
import pickle
from deepface import DeepFace

def train_model(progress_callback=None):
    """
    Trains the face recognition model using DeepFace:
    1. Loads images from dataset/
    2. Computes embeddings using VGG-Face
    3. Saves embeddings to encodings.pkl
    """
    dataset_dir = "dataset"
    if not os.path.exists(dataset_dir):
        print(f"Dataset directory '{dataset_dir}' not found.")
        return False

    print("Starting training with DeepFace... This may take a while depending on the number of images.")

    known_encodings = []
    known_names = []
    known_ids = []

    # Using VGG-Face (default) or Facenet for embeddings. VGG is fast and reliable.
    model_name = "VGG-Face"

    student_folders = [f for f in os.listdir(dataset_dir) if os.path.isdir(os.path.join(dataset_dir, f))]
    
    total_images = 0
    processed_images = 0

    for folder in student_folders:
        path = os.path.join(dataset_dir, folder)
        total_images += len([f for f in os.listdir(path) if f.endswith(('.jpg', '.jpeg', '.png'))])

    print(f"Found {len(student_folders)} students with {total_images} images.")
    
    if total_images == 0:
        return False

    for folder in student_folders:
        path = os.path.join(dataset_dir, folder)
        
        try:
            student_id, student_name = folder.split('_', 1)
        except ValueError:
            print(f"Skipping folder {folder}: Invalid format. Expected ID_Name.")
            continue

        print(f"Processing images for {student_name} ({student_id})...")

        for filename in os.listdir(path):
            if filename.endswith(('.jpg', '.jpeg', '.png')):
                img_path = os.path.join(path, filename)
                
                try:
                    # Generate embedding
                    # enforce_detection=False so it doesn't crash if a face isn't perfectly clear
                    embedding_objs = DeepFace.represent(img_path=img_path, model_name=model_name, enforce_detection=False)
                    
                    if len(embedding_objs) > 0:
                        # Take the first face found in the image
                        embedding = embedding_objs[0]["embedding"]
                        known_encodings.append(embedding)
                        known_names.append(student_name)
                        known_ids.append(student_id)
                        processed_images += 1
                        
                        # Update progress
                        if progress_callback:
                            progress_callback(processed_images, total_images, student_name)
                    else:
                        print(f"No face found in {filename}")
                        # still count as processed to advance the progress bar
                        processed_images += 1
                        if progress_callback:
                            progress_callback(processed_images, total_images, student_name)
                        
                except Exception as e:
                    print(f"Error processing {filename}: {e}")
                    processed_images += 1
                    if progress_callback:
                        progress_callback(processed_images, total_images, student_name)

    print(f"Training complete. Processed {processed_images}/{total_images} images.")

    if len(known_encodings) == 0:
        print("No faces were successfully encoded. Please check your dataset.")
        return False

    data = {
        "encodings": known_encodings,
        "names": known_names,
        "ids": known_ids,
        "model_name": model_name
    }

    try:
        with open("encodings.pkl", "wb") as f:
            pickle.dump(data, f)
        print("Encodings saved to 'encodings.pkl'.")
        return True
    except Exception as e:
        print(f"Error saving encodings: {e}")
        return False

if __name__ == "__main__":
    train_model()
