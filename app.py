from flask import Flask, render_template, request, send_file, send_from_directory, redirect
import os
import pyqrcode
from io import BytesIO
import datetime
import random

app = Flask(__name__)

# Directory for uploaded files
UPLOAD_FOLDER = "uploads"
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# List of dummy device names for demonstration
device_names = ["Laptop", "Smartphone", "Tablet", "Desktop", "Smart TV"]

# Dictionary to store connected devices
connected_devices = {}

# Track connected devices by their IP address and assign a random name
@app.before_request
def track_connected_devices():
    client_ip = request.remote_addr
    if client_ip not in connected_devices:
        device_name = random.choice(device_names)
        connected_devices[client_ip] = {
            'name': device_name,
            'first_connected': datetime.datetime.now(),
            'last_connected': datetime.datetime.now()
        }
    else:
        connected_devices[client_ip]['last_connected'] = datetime.datetime.now()

# Home page route
@app.route("/")
def home():
    return render_template("home.html")

# Route for generating QR code pointing to the home page
@app.route("/qr", methods=["GET"])
def generate_qr_code():
    app_url = request.url_root.rstrip("/")
    qr = pyqrcode.create(app_url)
    qr_img = BytesIO()
    qr.png(qr_img, scale=8)
    qr_img.seek(0)
    return send_file(qr_img, mimetype="image/png")

# Route to list available files
@app.route("/files", methods=["GET", "POST"])
def list_files():
    if request.method == "POST":
        selected_files = request.form.getlist("selected_files")
        for filename in selected_files:
            file_path = os.path.join(UPLOAD_FOLDER, filename)
            if os.path.exists(file_path):
                os.remove(file_path)
        return redirect("/files")

    files = os.listdir(UPLOAD_FOLDER)
    file_links = [
        {
            "name": file,
            "size": os.path.getsize(os.path.join(UPLOAD_FOLDER, file))
        }
        for file in files
    ]
    return render_template("file_list.html", file_links=file_links)

# Route for file upload (on a separate page)
@app.route("/upload", methods=["GET", "POST"])
def upload_file():
    if request.method == "POST":
        if "file" not in request.files:
            return "No file part", 400
        file = request.files["file"]
        if file.filename == "":
            return "No selected file", 400
        file.save(os.path.join(UPLOAD_FOLDER, file.filename))
        return redirect("/files")
    return render_template("upload.html")

# Route to download a specific file
@app.route("/download/<filename>", methods=["GET"])
def download_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

# Route for file preview (for demonstration purposes, assuming simple formats like images or PDFs)
@app.route("/preview/<filename>", methods=["GET"])
def preview_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

# Route to delete a specific file
@app.route("/delete/<filename>", methods=["GET"])
def delete_file(filename):
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    if os.path.exists(file_path):
        os.remove(file_path)
        return redirect("/files")
    else:
        return "File not found", 404

# Route to list connected devices
@app.route("/connected_devices", methods=["GET"])
def list_connected_devices():
    devices_info = [
        {
            "name": info["name"],
            "first_connected": info["first_connected"],
            "last_connected": info["last_connected"]
        }
        for _, info in connected_devices.items()
    ]
    return render_template("connected_devices.html", devices=devices_info)

# Start the Flask app
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
