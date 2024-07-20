import cv2
import mediapipe as mp
import time

class HandProcessor:
    def __init__(self):
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(static_image_mode=False,
                                         max_num_hands=3,
                                         min_detection_confidence=0.6,
                                         min_tracking_confidence=0.5)
        self.mpDraw = mp.solutions.drawing_utils

    def process_frame(self, img):
        start_time = time.time()
        h, w = img.shape[0], img.shape[1]
        img = cv2.flip(img, 1)
        img_RGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        results = self.hands.process(img_RGB)

        if results.multi_hand_landmarks:
            handness_str = ''
            index_finger_tip_str = ''
            for hand_idx in range(len(results.multi_hand_landmarks)):
                hand_21 = results.multi_hand_landmarks[hand_idx]
                self.mpDraw.draw_landmarks(img, hand_21, self.mp_hands.HAND_CONNECTIONS)
                temp_handness = results.multi_handedness[hand_idx].classification[0].label
                handness_str += '{}:{} '.format(hand_idx, temp_handness)
                hand_coordinates = {
                    "hand_index": hand_idx,
                    "handness": temp_handness,
                    "landmarks": []
                }
                cz0 = hand_21.landmark[0].z
                min_x, min_y = w, h
                max_x, max_y = 0, 0
                for i in range(21):
                    cx = int(hand_21.landmark[i].x * w)
                    cy = int(hand_21.landmark[i].y * h)
                    cz = hand_21.landmark[i].z
                    depth_z = cz0 - cz
                    hand_coordinates["landmarks"].append({
                        "index": i,
                        "x": cx,
                        "y": cy,
                        "z": hand_21.landmark[i].z
                    })
                    min_x = min(min_x, cx)
                    min_y = min(min_y, cy)
                    max_x = max(max_x, cx)
                    max_y = max(max_y, cy)
                    radius = 5
                    if i == 0:
                        img = cv2.circle(img, (cx, cy), radius, (0, 0, 255), -1)
                    if i == 8:
                        img = cv2.circle(img, (cx, cy), radius, (193, 182, 255), -1)
                        index_finger_tip_str += '{}:{:.2f} '.format(hand_idx, depth_z)
                    if i in [1, 5, 9, 13, 17]:
                        img = cv2.circle(img, (cx, cy), radius, (16, 144, 247), -1)
                    if i in [2, 6, 10, 14, 18]:
                        img = cv2.circle(img, (cx, cy), radius, (1, 240, 255), -1)
                    if i in [3, 7, 11, 15, 19]:
                        img = cv2.circle(img, (cx, cy), radius, (140, 47, 240), -1)
                    if i in [4, 12, 16, 20]:
                        img = cv2.circle(img, (cx, cy), radius, (223, 155, 60), -1)
            width = max_x - min_x
            height = max_y - min_y
            min_x = max(0, int(min_x - 0.25 * width))
            min_y = max(0, int(min_y - 0.25 * height))
            max_x = min(w, int(max_x + 0.25 * width))
            max_y = min(h, int(max_y + 0.25 * height))
            color = (0, 255, 0) if temp_handness == 'Right' else (255, 0, 0)
            img = cv2.rectangle(img, (min_x, min_y), (max_x, max_y), color, 2)
            scaler = 1
            img = cv2.putText(img, handness_str, (25 * scaler, 100 * scaler), cv2.FONT_HERSHEY_SIMPLEX, 1 * scaler,
                              (255, 0, 255), 2 * scaler)
            img = cv2.putText(img, index_finger_tip_str, (25 * scaler, 150 * scaler), cv2.FONT_HERSHEY_SIMPLEX,
                              1 * scaler, (255, 0, 255), 2 * scaler)
            end_time = time.time()
            FPS = 1 / (end_time - start_time)
            img = cv2.putText(img, 'FPS  ' + str(int(FPS)), (25 * scaler, 50 * scaler), cv2.FONT_HERSHEY_SIMPLEX,
                              1 * scaler, (255, 0, 255), 2 * scaler)
        return img
