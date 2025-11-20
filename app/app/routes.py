import os
import requests
import cv2
import time
from flask import Blueprint, render_template, jsonify, request
from flask_login import login_required

main_bp = Blueprint('main', __name__)

# GLOBAL PROGRESS VARIABLE
SCAN_PROGRESS = {"value": 0}

def relay_on(n):
    url = f"http://192.168.4.1/relay?r{n}=on"
    try:
        response = requests.get(url, timeout=2)
        print(f"Relay {n} ON at {time.strftime('%H:%M:%S')}")
    except Exception as e:
        print(f"Relay {n} ON error:", e)

def relay_off(n):
    url = f"http://192.168.4.1/relay?r{n}=off"
    try:
        response = requests.get(url, timeout=2)
        print(f"Relay {n} OFF at {time.strftime('%H:%M:%S')}")
    except Exception as e:
        print(f"Relay {n} OFF error:", e)

@main_bp.route('/')
def splash():
    return render_template('splash.html')

@main_bp.route('/home')
@login_required
def home():
    return render_template('home.html')

@main_bp.route('/video_feed')
@login_required
def video_feed():
    from .camera import frames
    return frames()

@main_bp.route('/scan', methods=['POST'])
@login_required
def scan():
    print("Scan Button Pressed")
    data = request.get_json(force=True)
    lot_no = (data.get('lot') or '').strip()
    prod_id = (data.get('id') or '').strip()

    desktop = os.path.join(os.path.expanduser("~"), "Desktop")
    parent_folder = os.path.join(desktop, "CapturedScans")
    os.makedirs(parent_folder, exist_ok=True)
    folder_name = f"{lot_no}_{prod_id}" if lot_no and prod_id else time.strftime("%Y-%m-%d_%H-%M-%S")
    scan_folder = os.path.join(parent_folder, folder_name)
    os.makedirs(scan_folder, exist_ok=True)

    cam = cv2.VideoCapture(1)
    cam.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    time.sleep(0.5)  # minimal camera warmup

    start = time.time()
    saved = []
    capture_num = 1

    # Progress percentages for each image
    percent_steps = [20, 40, 60, 80, 90, 100]
    SCAN_PROGRESS["value"] = 0  # Reset at scan start

    # Timeline for this scan session
    timeline = [
        (1,  'relay_on',  1),
        (2,  'capture',   None),
        (2,  'relay_off', 1),
        (4,  'relay_on',  2),
        (5,  'capture',   None),
        (5,  'relay_off', 2),
        (8,  'relay_on',  3),
        (9,  'capture',   None),
        (9,  'relay_off', 3),
        (13, 'relay_on',  4),
        (14, 'capture',   None),
        (14, 'relay_off', 4),
        (17, 'capture',   None),
        (19, 'capture',   None),
    ]
    print("Relay Command Started")
    for sec, action, relay in timeline:
        target_time = start + sec
        wait = target_time - time.time()
        if wait > 0:
            time.sleep(wait)
        if action == 'relay_on':
            relay_on(relay)
        elif action == 'relay_off':
            relay_off(relay)
        elif action == 'capture':
            ret, frame = cam.read()
            fname = os.path.join(scan_folder, f"scan_{capture_num}.jpg")
            if ret:
                cv2.imwrite(fname, frame)
                saved.append(fname)
                print(f"Captured image {capture_num} at {sec} sec ({time.strftime('%H:%M:%S')})")
            # Update progress after each capture
            if capture_num <= len(percent_steps):
                SCAN_PROGRESS["value"] = percent_steps[capture_num-1]
                print("Progress updated to", SCAN_PROGRESS["value"])
            capture_num += 1

    cam.release()
    print("Scan & relay sequence complete.")
    SCAN_PROGRESS["value"] = 100  # Ensure 100% on finish (even if extra captures)
    return jsonify({'result': 'ok', 'files': saved, 'msg': 'Saved successfully!'})

@main_bp.route('/scan_progress')
def scan_progress():
    return jsonify({"progress": SCAN_PROGRESS["value"]})

@main_bp.route('/autofocus', methods=['POST'])
@login_required
def autofocus():
    cam = cv2.VideoCapture(1)
    msg = ""
    try:
        ret = cam.set(cv2.CAP_PROP_AUTOFOCUS, 1)
        msg = "Autofocus set: " + str(ret)
        time.sleep(0.3)
    finally:
        cam.release()
    return jsonify({"message": msg})
