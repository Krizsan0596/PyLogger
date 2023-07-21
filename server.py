import importlib
import sys
import subprocess


def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])


try:
    importlib.import_module("pyngrok")
except ImportError:
    install("pyngrok")

try:
    importlib.import_module("Flask")
except ImportError:
    install("Flask")

from pyngrok import ngrok
import os
from flask import Flask, request

app = Flask(__name__)


@app.route('/upload', methods=['POST'])
def upload_file():
    # Create a folder based on the sender's IP address
    sender_ip = request.remote_addr
    folder_name = os.path.join(os.getcwd(), sender_ip)
    os.makedirs(folder_name, exist_ok=True)

    # Save the uploaded file to the created folder
    file = request.files['file']
    file_path = os.path.join(folder_name, file.filename)
    file.save(file_path)

    return 'File uploaded successfully!'


ngrok.connect(8181)
if __name__ == '__main__':
    app.run(port=8181)
