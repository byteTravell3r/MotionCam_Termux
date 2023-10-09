#!/data/data/com.termux/files/usr/bin/python3

### === A Very Simple Security Camera with Motion Detection implemented with Python3, Termux:API, OpenCV and rsync ===

# Default settings and rsync destination path (Modify these!)
flashLight = True; autoSync = False; captureInterval = 0.5; motionDet = True;  saveCount = 10, threshold = 0.05;
pathRemoteSync = "byte@192.168.1.2:/home/byte/"

import os, sys, subprocess, signal, time, argparse
pathSave = "/data/data/com.termux/files/home/pics"
pathTermuxAPI = "/data/data/com.termux/files/usr/libexec/termux-api"
width = 0; height = 0; photoCount = 0; saveFrame = []; saveFrameStamp = [];

parser = argparse.ArgumentParser()
parser.add_argument("-l", "--light", default=True, required=False, action="store_true", help="Enable Camera LED Flash Light.")
parser.add_argument("-r", "--rsync", default=True, required=False, action="store_true", help="Enable Incremental Sync (rsync).")
parser.add_argument("-m", "--motion", default=True, required=False, action="store_true", help="Enable Motion Detection. (OpenCV Required)")
parser.add_argument("-c", "--count", required=False, help="Auto Sync Frequency (Upload Per (x) Valid Shots)")

def execCmd(command):
  proc = subprocess.Popen("exec " + command, shell=True, preexec_fn=lambda:os.nice(-19))

def signal_handler(sig, frame):
  if sig == signal.SIGINT:
    setLight(False)
    saveImage()
    execCmd(f"rm -rf {pathSave}/captured/")
    if autoSync:
      print("Syncing...")
      execCmd(f"rsync -a --exclude 'captured/' {pathSave} {pathRemoteSync}")
    execCmd("termux-wake-unlock")
    print("=== Shutdown Gracefully ===")
    sys.exit(0)

def setLight(bool):
  if flashLight:
    execCmd(f"{pathTermuxAPI} Torch --ez enabled {bool}")

def capturePic(path, filename):
  procCapture = subprocess.Popen(f"exec {pathTermuxAPI} CameraPhoto --es camera 0 --es file {path}/{filename}.jpg", shell=True, preexec_fn=lambda:os.nice(-19))
  while not os.path.isfile(f"{path}/{filename}.jpg"): time.sleep(0.1)
  procCapture.kill()
  print(f"Captured: {filename}.jpg")

def saveImage():
  for i in range(len(saveFrame)):
    execCmd(f"cp {pathSave}/captured/{saveFrame[i]}.jpg {pathSave}/{saveFrameStamp[i]}.jpg")
    print(f"{saveFrameStamp[i]}.jpg")

# Initialize
print("=== SecurityCamera Script w/ Motion Detection ===")
args = parser.parse_args()
if args.light:
  print("Use Camera LED Flash Light.")
  flashLight = True
if args.rsync:
  print("Auto Incremental Sync Enabled.")
  autoSync = True
if args.motion:
  print("Motion Detection Enabled.")
  import cv2
  motionDet = True
if args.count:
  saveCount = int(args.count)

signal.signal(signal.SIGINT, signal_handler); os.setpriority(0, 0, -19); execCmd("termux-wake-lock");

if not os.path.isdir(pathSave):
  os.mkdir(pathSave)
  print("Creating Directory for Picture.")
if not os.path.isdir(pathSave + "/captured/"):
  os.mkdir(pathSave + "/captured/")

capturePic(f"{pathSave}/captured", photoCount)
img0 = cv2.imread(f"{pathSave}/captured/0.jpg")
width = img0.shape[0]; height = img0.shape[1];
print(f"Save Once per {saveCount} Shot(s).")
print("Init Complete.")

while 1:
  setLight(True)
  time.sleep(0.1)
  photoCount += 1
  stamp = time.strftime("%y%m%d-%H%M%S")
  capturePic(f"{pathSave}/captured", photoCount)
  setLight(False)
  if motionDet:
    # curr_frame - prev_frame, then calculate the area of contour
    prev_frame = cv2.imread(f"{pathSave}/captured/{photoCount - 1}.jpg")
    prev_frame = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)
    ret, prev_frame = cv2.threshold(prev_frame, 100, 255, cv2.THRESH_BINARY)
    curr_frame = cv2.imread(f"{pathSave}/captured/{photoCount}.jpg")
    curr_frame = cv2.cvtColor(curr_frame, cv2.COLOR_BGR2GRAY)
    ret, curr_frame = cv2.threshold(curr_frame, 100, 255, cv2.THRESH_BINARY)
    diff_frame = cv2.subtract(curr_frame, prev_frame)
    contours, hirearchy = cv2.findContours(diff_frame, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    contArea = 0
    for contour in contours: contArea += cv2.contourArea(contour);
    changeRate =  contArea / (width * height)
    print(f"Difference: {changeRate}%")
    if changeRate > threshold:
      saveFrame.append(photoCount)
      saveFrameStamp.append(stamp)
      print("=== Moved! ===")
  else:
    saveFrame.append(photoCount)
    saveFrameStamp.append(stamp)
  
  if len(saveFrame) >= saveCount:
    if autoSync:
      execCmd(f"rm {pathSave}/*.jpg")
      while os.listdir(f"{pathSave}/") != ['captured']: time.sleep(0.1)
    print("Flushing...")
    saveImage()
    # Move the last frame out of the temp(captured) directory temporarily
    # Using a lot of "while not" for a fixed exec order
    execCmd(f"mv {pathSave}/captured/{photoCount}.jpg {pathSave}/0.jpg")
    while not os.path.isfile(f"{pathSave}/0.jpg"): time.sleep(0.1)
    execCmd(f"rm {pathSave}/captured/*")
    while os.listdir(f"{pathSave}/captured/") != []: time.sleep(0.1)
    execCmd(f"mv {pathSave}/0.jpg {pathSave}/captured/0.jpg")
    while not os.path.isfile(f"{pathSave}/captured/0.jpg"): time.sleep(0.1)

    photoCount = 0
    saveFrame = []; saveFrameStamp = [];
    if autoSync:
      print("Syncing...")
      execCmd(f"rsync -a  --exclude 'captured/' {pathSave} {pathRemoteSync}")

  time.sleep(captureInterval)
