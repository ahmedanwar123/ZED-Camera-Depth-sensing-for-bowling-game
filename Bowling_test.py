import mediapipe as mp
import cv2
import numpy as np
import pyautogui
import time

mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose


def calculate_angle(a, b, c):
    a = np.array(a)  # First
    b = np.array(b)  # Mid
    c = np.array(c)  # End

    radians = np.arctan2(c[1] - b[1], c[0] - b[0]) - np.arctan2(a[1] - b[1], a[0] - b[0])
    angle = np.abs(radians * 180.0 / np.pi)

    if angle > 180.0:
        angle = 360 - angle

    return angle


def calculate_tilt(a, b):
    a = np.array(a)
    b = np.array(b)

    radians = np.arctan((b[0] - a[0]) / [a[1] - b[1]])
    angle = np.abs(radians * 180.0 / np.pi)
    if (b[0] - a[0]) > 0:
        angle = -1 * angle

    if angle > 180.0:
        angle = 360 - angle

    return angle


cap = cv2.VideoCapture(1)  # Change to 1 for the other camera

with mp_pose.Pose(static_image_mode=True, min_detection_confidence=0.5) as pose:
    while cap.isOpened():
        Ball = False
        ret, frame = cap.read()

        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image.flags.writeable = False

        result = pose.process(image)

        try:
            landmarks = result.pose_landmarks.landmark
            shoulder = [landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].x,
                        landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].y]
            elbow = [landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value].x,
                     landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value].y]
            wrist = [landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].x,
                     landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].y]

            image.flags.writeable = True
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

            mp_drawing.draw_landmarks(image, result.pose_landmarks, mp_pose.POSE_CONNECTIONS)
            image = cv2.flip(image, 1)

            cv2.imshow("pose estimation", image)

            angle_of_release = calculate_angle(shoulder, elbow, wrist)
            if angle_of_release < 90:
                Ball = True
                # break

            position = (landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value].x + landmarks[
                mp_pose.PoseLandmark.LEFT_HIP.value].x) / 2 - 0.5
            position += 0.2
            position *= 1000
            # pyautogui.moveTo(720, 750)
            pyautogui.moveTo(970 - position, 830)

            tilt = calculate_tilt(shoulder, elbow)

            if Ball:
                pyautogui.dragTo(970, 200, 0.2, button='left')
                time.sleep(5)
                pyautogui.moveTo(970, 830)

        except:
            pass

        if cv2.waitKey(10) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
