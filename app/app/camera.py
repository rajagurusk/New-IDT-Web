import cv2
from flask import Response

def frames():
    cap = cv2.VideoCapture(1)  # use 0 for the first USB camera

    def generate():
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            ret, jpeg = cv2.imencode('.jpg', frame)
            if not ret:
                continue
            yield (
                b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n'
            )

    return Response(generate(), mimetype='multipart/x-mixed-replace; boundary=frame')
