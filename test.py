import requests
import time
import cv2

cam = cv2.VideoCapture(1)
cam.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
# time.sleep(0.2)

start_on = time.time()
try:
    r_on = requests.get("http://192.168.4.1/relay?r1=on", timeout=1.5)
    print("Relay 1 ON, response:", r_on.text)
except Exception as e:
    print("Relay 1 ON error:", e)
print("Relay ON command took:", round(time.time()-start_on, 2), "seconds")
# time.sleep(2)

start_off = time.time()
try:
    r_off = requests.get("http://192.168.4.1/relay?r1=off", timeout=1.5)
    print("Relay 1 OFF, response:", r_off.text)
except Exception as e:
    print("Relay 1 OFF error:", e)
print("Relay OFF command took:", round(time.time()-start_off, 2), "seconds")

cam.release()
print("Test complete.")
