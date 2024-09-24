from flask import Flask, render_template, request, redirect, send_file
from PIL import Image
import os
import zipfile

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads/'
PROCESSED_FOLDER = 'processed/'

# Ensure the directories exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)

@app.route('/')
def upload_form():
    return render_template('upload.html')

@app.route('/upload', methods=['POST'])
def upload_image():
    files = request.files.getlist('files[]')
    if not files:
        return "No files uploaded", 400

    for file in files:
        filepath = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(filepath)
        print(f"Saved uploaded file: {filepath}")

        # Open the image and break into 256x256 tiles
        img = Image.open(filepath)
        width, height = img.size
        print(f"Original image size: {width}x{height}")
        
        for i in range(0, width, 256):
            for j in range(0, height, 256):
                box = (i, j, i+256, j+256)
                tile = img.crop(box)
                tile_name = f"{os.path.splitext(file.filename)[0]}_{i}_{j}.png"
                tile_path = os.path.join(PROCESSED_FOLDER, tile_name)
                tile.save(tile_path)
                print(f"Saved tile: {tile_path}")

    # Create a zip file of processed images
    zip_filename = "processed_images.zip"
    with zipfile.ZipFile(zip_filename, 'w') as zipf:
        for root, dirs, files in os.walk(PROCESSED_FOLDER):
            for file in files:
                zipf.write(os.path.join(root, file), file)
                print(f"Added {file} to zip file.")

    print(f"Final zip file size: {os.path.getsize(zip_filename)} bytes")

    return send_file(zip_filename, as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)
