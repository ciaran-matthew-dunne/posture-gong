import cv2
import numpy as np
import math, os, time

state = "OUT"

cap = cv2.VideoCapture(0)
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')
angle, last_played = 0, 0

while True:
  angle=0
  ret, frame = cap.read()
  gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
  faces = face_cascade.detectMultiScale(gray, 1.3, 5)
  # Draw rectangle around detected face
  for (x, y, w, h) in faces:
    cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
    # Crop the region of interest to the face area
    roi_gray = gray[y:y+h, x:x+w]
    roi_color = frame[y:y+h, x:x+w]
    # Detect eyes in the region of interest
    eyes = eye_cascade.detectMultiScale(roi_gray)
    # Draw a rectangle around each detected eye
    eye_boxes = []
    for (ex, ey, ew, eh) in eyes:
      eye_boxes.append((x+ex, y+ey, ew, eh))
      cv2.rectangle(roi_color, (ex, ey), (ex+ew, ey+eh), (255, 0, 0), 2)

    # Draw a line between the centers of the eye boxes
    if len(eye_boxes) == 2:
      eye_box1 = eye_boxes[0]
      eye_box2 = eye_boxes[1]
      (x1,y1) = (eye_box1[0] + eye_box1[2] // 2, eye_box1[1] + eye_box1[3] // 2)
      (x2,y2) = (eye_box2[0] + eye_box2[2] // 2, eye_box2[1] + eye_box2[3] // 2)
      cv2.line(frame, (x1,y1), (x2,y2), (0, 0, 255), 2)

      # Calculate the angle between the eyes
      delta_x = x2 - x1
      delta_y = y2 - y1
      angle = np.arctan2(delta_y, delta_x) * 180 / np.pi

      # Adjust the angle if it's less than -90 degrees
      if angle > 90:
        angle = angle - 180
  
  cv2.putText(frame, f"Angle: {angle:.2f}\nState: {state}", (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
  cv2.imshow('frame', frame) 


  if angle > -12 and angle < 12:
    if state == "OUT" and time.time() - last_played > 0.5:
      os.system('cvlc /usr/share/sounds/Yaru/stereo/power-plug.oga -q --play-and-exit')
      last_played = time.time()
      state = "IN"
  else:
    if state == "IN" and time.time() - last_played > 0.5:
      os.system('cvlc /usr/share/sounds/Yaru/stereo/power-unplug.oga -q --play-and-exit')
      last_played = time.time()
      state = "OUT"

  if cv2.waitKey(1) & 0xFF == ord('q'):
    break
    

# Release the video capture device and close all windows
cap.release()
cv2.destroyAllWindows()
