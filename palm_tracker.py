import cv2
import mediapipe as mp


class PalmTracker:
    def __init__(self):
        self.cap = cv2.VideoCapture(0)

        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose()

        # last known coords (for stability)
        self.x = 0
        self.y = 0

    def process_frame(self):
        """Returns: (frame, (x, y)) — coordinates of LEFT_FOOT_INDEX"""

        ret, frame = self.cap.read()
        if not ret:
            return None, (self.x, self.y)

        frame = cv2.flip(frame, 1)
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.pose.process(rgb)

        h, w, _ = frame.shape

        if results.pose_landmarks:
            foot = results.pose_landmarks.landmark[
                self.mp_pose.PoseLandmark.LEFT_WRIST_INDEX
            ]

            self.x = int(foot.x * w)
            self.y = int(foot.y * h)

        # return coords (no drawings)
        return frame, (self.x, self.y)

    def release(self):
        self.cap.release()
