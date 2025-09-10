import os
from flask import Flask, request, render_template, send_file
from google.cloud import storage
from werkzeug.utils import secure_filename
import io

app = Flask(__name__)

# Replace with your actual bucket name
BUCKET_NAME = os.environ.get("GCS_BUCKET_NAME")

# Initialize a client for GCS
# The library will automatically use the credentials from the GOOGLE_APPLICATION_CREDENTIALS environment variable
storage_client = storage.Client()

def upload_to_gcs(file_stream, filename):
    """Uploads a file stream to a Google Cloud Storage bucket."""
    bucket = storage_client.bucket(BUCKET_NAME)
    blob = bucket.blob(filename)
    blob.upload_from_file(file_stream)

def download_from_gcs(filename):
    """Downloads a file from GCS into memory."""
    bucket = storage_client.bucket(BUCKET_NAME)
    blob = bucket.blob(filename)
    
    # Download the file content into an in-memory buffer
    file_buffer = io.BytesIO()
    blob.download_to_file(file_buffer)
    file_buffer.seek(0)
    return file_buffer

@app.route('/')
def index():
    """Renders the file upload form."""
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    """Handles the file upload and saves it to GCS."""
    if 'file' not in request.files:
        return 'No file part', 400
    
    file = request.files['file']
    if file.filename == '':
        return 'No selected file', 400

    if file:
        filename = secure_filename(file.filename)
        upload_to_gcs(file, filename)
        return f'File {filename} uploaded successfully to GCS!'

@app.route('/download/<filename>')
def download_file(filename):
    """Handles file download from GCS."""
    try:
        file_buffer = download_from_gcs(filename)
        return send_file(file_buffer, mimetype='application/octet-stream', as_attachment=True, download_name=filename)
    except Exception as e:
        return f'Error downloading file: {e}', 404

if __name__ == '__main__':
    # For local development, set the bucket name and creds in your environment
    if BUCKET_NAME is None:
        print("Warning: GCS_BUCKET_NAME environment variable is not set. GCS features will not work.")
    app.run(host="0.0.0.0", port=5000, debug=True)
