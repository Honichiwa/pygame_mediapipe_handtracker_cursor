# main.py — Final version with:
# OpenCV Threaded Hand Tracking
# Pinch Detection
# SmoothCursor (idle/active)
# Adaptive Smoothing (smooth.py)
import time
import pygame
import threading
import queue
import config

from hand_cursor_tracker import HandCursorTracker
from cursor import SmoothCursor
from smooth import CursorSmoother



# --------------------------------------------
# INITIALIZE PYGAME
# --------------------------------------------
pygame.init()

screen = pygame.display.set_mode(
    (config.DISPLAY_WIDTH, config.DISPLAY_HEIGHT),
    pygame.DOUBLEBUF
)

pygame.display.set_caption("Hand Cursor Game")
clock = pygame.time.Clock()
pygame.mouse.set_visible(False)



# --------------------------------------------
# QUEUE FOR CURSOR DATA FROM THREAD
# --------------------------------------------
cursor_queue = queue.Queue(maxsize=1)


# --------------------------------------------
# THREAD: HAND TRACKING (OpenCV)
# --------------------------------------------
def tracking_loop():
    tracker = HandCursorTracker()
    cam_width = tracker.cap.get(3)
    cam_height = tracker.cap.get(4)

    while True:
        frame, (cx, cy, pinched) = tracker.process_frame()
        if frame is None:
            continue

        # Always keep the newest cursor data only
        try:
            cursor_queue.get_nowait()
        except queue.Empty:
            pass

        cursor_queue.put((cx, cy, pinched, cam_width, cam_height))

# Start thread
tracking_thread = threading.Thread(target=tracking_loop, daemon=True)
tracking_thread.start()

# --------------------------------------------
# CREATE CURSOR + SMOOTHER
# --------------------------------------------
cursor = SmoothCursor(
    outer_radius=50,
    inner_radius=40,
    speed=3,
    color=(153, 255, 51)  # green for pinch
)

smoother = CursorSmoother(dead_zone=12)


target_x = config.DISPLAY_WIDTH // 2
target_y = config.DISPLAY_HEIGHT // 2

pinch_start_time = 0
pinch_required_ms = 0.15


pinch_count = 0
last_pinch_time = 0
PINCH_ACTIVATION_FRAMES = 3     # how many frames in a row needed
PINCH_HANG_TIME = 0.08


# --------------------------------------------
# MAIN LOOP
# --------------------------------------------
running = True

while running:

    # ---------------------------
    # Handle events
    # ---------------------------
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # ---------------------------
    # Get latest cursor data
    # ---------------------------
    try:
        cx, cy, pinched, cam_w, cam_h = cursor_queue.get_nowait()
        # Convert camera coords → Pygame coords
        scale_x = config.DISPLAY_WIDTH / cam_w
        scale_y = config.DISPLAY_HEIGHT / cam_h

        target_x = cx * scale_x
        target_y = cy * scale_y

    except queue.Empty:
        pinched = False
        # Keep using previous target_x/target_y
        # They will remain unchanged if no new hand data



    # ---------------------------
    # Apply ADAPTIVE smoothing
    # ---------------------------
    sx, sy = smoother.update(target_x, target_y)


    # ---------------------------
    # PINCH ANIMATION LOGIC
    # ---------------------------

    current_time = time.time()

    if pinched:  # raw pinch from camera
        pinch_count += 1
        last_pinch_time = current_time

        # Activate pinch only when enough frames detected
        if pinch_count >= PINCH_ACTIVATION_FRAMES:
            cursor.start_animation()

    else:
        # If no new pinch frames arrived for 0.10 seconds → stop animation
        if current_time - last_pinch_time > PINCH_HANG_TIME:
            pinch_count = 0
            cursor.stop_animation()


    # Update animation progression
    cursor.update()

    # ---------------------------
    # DRAW FRAME
    # ---------------------------
    screen.fill((0, 0, 0))
    cursor.draw(screen, (int(sx), int(sy)))

    pygame.display.flip()
    clock.tick(120)



# Quit cleanly
pygame.quit()