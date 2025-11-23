# cursor_test.py — Standalone mouse testing of SmoothCursor

import pygame
from cursor import SmoothCursor  # your real cursor.py will be used

pygame.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.DOUBLEBUF)
pygame.display.set_caption("Cursor Appearance Test")

clock = pygame.time.Clock()

# Create your cursor with whatever values you're testing
cursor = SmoothCursor(
    outer_radius=50,
    inner_radius=40,
    speed=5,
    color=(153, 255, 51)  # green for pinch
)

running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # Simulate pinch using left mouse click
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # left click = pinch
                cursor.start_animation()

    # Cursor position follows mouse
    mx, my = pygame.mouse.get_pos()

    # Update cursor animation
    cursor.update()

    # Draw everything
    screen.fill((30, 30, 30))  # dark grey background
    cursor.draw(screen, (mx, my))

    pygame.display.flip()
    clock.tick(120)

pygame.quit()
