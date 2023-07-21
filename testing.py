import io
import os
import zipfile


def zip_files_to_device_name(device_name, file_paths):
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w") as zip_file:
        for file_path in file_paths:
            if os.path.exists(file_path):
                zip_file.write(file_path)

    return zip_buffer.getvalue()
