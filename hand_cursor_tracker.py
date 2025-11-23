import cv2
import mediapipe as mp
import numpy as np
import math
import config
from palm_tracker import PalmTracker

pt = PalmTracker()

class HandCursorTracker:
    def __init__(self):
        self.mp_hands = mp.solutions.hands.Hands(
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        self.mp_draw = mp.solutions.drawing_utils

        self.cap = cv2.VideoCapture(0)

        self.cursor_x = 0
        self.cursor_y = 0
        self.palm_cursor_x = 0
        self.palm_cursor_y = 0
        self.pinch_threshold = 0.06
        self.is_pinched = False

    def process_frame(self):
        ret, frame = self.cap.read()
        if not ret:
            return None, None

        frame = cv2.flip(frame, 1)
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.mp_hands.process(rgb)

        h, w, _ = frame.shape
        self.is_pinched = False

        if results.multi_hand_landmarks:
            lm = results.multi_hand_landmarks[0].landmark

            # INDEX TIP
            palm = lm[5]
            self.palm_cursor_x = int(palm.x * w)
            self.palm_cursor_y = int(palm.y * h)

            index = lm[8]
            self.cursor_x = int(index.x * w)
            self.cursor_y = int(index.y * h)

            # PINCH DETECTION
            thumb = lm[4]
            dx = thumb.x - index.x
            dy = thumb.y - index.y
            dist = math.sqrt(dx * dx + dy * dy)

            if dist < self.pinch_threshold:
                self.is_pinched = True

            # ---------- TEST MODE VISUALIZATION ----------
            if config.TEST_MODE:
                # Draw landmarks on camera
                self.mp_draw.draw_landmarks(
                    frame,
                    results.multi_hand_landmarks[0],
                    mp.solutions.hands.HAND_CONNECTIONS
                )

                # Draw the cursor point
                cv2.circle(frame, (self.cursor_x, self.cursor_y), 12,
                           (0, 255, 0), 2)

                # Draw pinch line
                ix = int(index.x * w)
                iy = int(index.y * h)
                tx = int(thumb.x * w)
                ty = int(thumb.y * h)

                cv2.line(frame, (tx, ty), (ix, iy),
                         (0, 255, 255) if self.is_pinched else (255, 0, 0),
                         2)

        # ---------- SHOW CAMERA WINDOW IF TEST MODE ----------
        if config.TEST_MODE:
            cv2.imshow("DEBUG CAMERA POV", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                pass

        return frame, (self.palm_cursor_x, self.palm_cursor_y, self.is_pinched)

    def release(self):
        self.cap.release()
        cv2.destroyAllWindows()
