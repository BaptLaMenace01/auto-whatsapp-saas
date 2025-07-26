from flask import Flask, render_template, request, redirect, send_file
import os
import csv
import subprocess
from datetime import datetime

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
import os
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_PATH = os.path.join(BASE_DIR, "template.csv")

CSV_PATH = os.path.join(UPLOAD_FOLDER, "uploaded.csv")
MESSAGE_PATH = os.path.join(os.getcwd(), "message.txt")
IMAGE_PATH = os.path.join(os.getcwd(), "image.jpg")

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/download-template")
def download_template():
    return send_file(TEMPLATE_PATH, as_attachment=True)

@app.route("/upload", methods=["POST"])
def upload():
    file = request.files["csv_file"]
    message = request.form["message"]
    send_image = request.form.get("send_image") == "on"

    file.save(CSV_PATH)

    with open(MESSAGE_PATH, "w", encoding="utf-8") as f:
        f.write(message)

    # Lance le script JS avec les bons arguments
      # Lance le script Python avec les bons arguments
    args = ["python3", "script.py"]
    if send_image:
        args.append("--image")


    subprocess.Popen(args)
    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)

