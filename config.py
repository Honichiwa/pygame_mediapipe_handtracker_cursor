# config.py
import os

# ----- Paths -----
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
IMAGES_DIR = os.path.join(ASSETS_DIR, "images")
SOUNDS_DIR = os.path.join(ASSETS_DIR, "sounds")
FONTS_DIR = os.path.join(ASSETS_DIR, "fonts")
DATA_DIR = os.path.join(BASE_DIR, "data")
LEVEL_DATA_PATH = os.path.join(DATA_DIR, "level_data.json")

# ----- Display -----
DISPLAY_WIDTH = 1920
DISPLAY_HEIGHT = 1080
FULLSCREEN = False
TARGET_FPS = 144

# ----- Camera / Tracking -----
CAMERA_WIDTH = 640
CAMERA_HEIGHT = 480
PROCESS_EVERY_N_FRAMES = 2  # process every Nth frame

# ----- MediaPipe Hands -----
MP_MODEL_COMPLEXITY = 0
MP_MIN_DET_CONF = 0.7
MP_MIN_TRK_CONF = 0.5
MP_MAX_HANDS = 1

# ----- Gesture thresholds -----
PINCH_DISTANCE_THRESHOLD = 0.05  # normalized coords
PINCH_DEBOUNCE_SECONDS = 0.3

# ----- Gameplay -----
OBJECTS_PER_LEVEL = (5, 8)
LEVEL_COMPLETE_DELAY = 2.0

# ----- Colors -----
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (80, 220, 120)
RED = (220, 80, 80)
YELLOW = (255, 220, 80)
UI_BG = (20, 20, 20)

USE_MOUSE = False   # or False for hand-tracking mode

TEST_MODE = True


CORRECT_HOLD_TIME = 0.8   # green display time
WRONG_COOLDOWN = 1.0      # red display time

CURSOR_COLOR_GREEN = (0, 255, 0)
CURSOR_COLOR_RED = (255, 50, 50)
CURSOR_COLOR_YELLOW = (255, 255, 51, 200)

CAMERA_MARGIN_X = 0.20   # 20% margin on left/right
CAMERA_MARGIN_Y = 0.20   # 20% margin on top/bottom
