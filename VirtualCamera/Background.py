import os, cv2, pyvirtualcam
import mediapipe as mp
import numpy as np

dirpath = os.path.dirname(os.path.realpath(__file__))

mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_face_mesh = mp.solutions.face_mesh
mp_selfie_segmentation = mp.solutions.selfie_segmentation

try: cap = cv2.VideoCapture(0)
except Exception: cap = cv2.VideoCapture(1)
fmt = pyvirtualcam.PixelFormat.BGR  

imgBg = cv2.imread(f"{dirpath}\\forest_img.jpg")
with pyvirtualcam.Camera(width=1280, height=720, fps=20, fmt=fmt) as cam:
  with mp_selfie_segmentation.SelfieSegmentation(model_selection=1) as selfie_segmentation:
    bg_image = None
    while cap.isOpened():
      success, image = cap.read()
      image = cv2.resize(image, (1280, 720), interpolation=cv2.BORDER_DEFAULT)
      imgBg = cv2.resize(imgBg, (1280, 720), interpolation=cv2.BORDER_DEFAULT)
      if not success:
        print("Ignoring empty camera frame.")
        continue
      image = cv2.cvtColor(cv2.flip(image, 1), cv2.COLOR_BGR2RGB)
      image.flags.writeable = False
      results = selfie_segmentation.process(image)

      image.flags.writeable = True
      image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
      condition = np.stack(
        (results.segmentation_mask,) * 3, axis=-1) > 0.1
      if bg_image is None:
        bg_image = np.zeros(image.shape, dtype=np.uint8)
        bg_image[:] = imgBg
      output_image = np.where(condition, image, bg_image)

      cam.send(output_image)
      cam.sleep_until_next_frame()
      if cv2.waitKey(5) & 0xFF == 27:
        break
cap.release()