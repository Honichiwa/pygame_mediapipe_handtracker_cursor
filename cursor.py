import pygame
import math
import time


class SmoothCursor:
    def __init__(self, outer_radius=60, inner_radius=20, speed=5, color=(0, 255, 0)):
        self.outer_radius = outer_radius
        self.inner_radius = inner_radius
        self.speed = speed

        # Colors
        self.active_color = color
        self.idle_color = (255, 255, 51, 200)
        self.error_color = (255, 0, 0)

        # Animation state
        self.angle = 360
        self.animating = False

        # Cached surfaces
        self._cached_idle = None
        self._cached_angle = None
        self._cached_overlay = None

        # Green animation timers
        self.hold_until = 0
        self.cooldown_green = False
        self.cooldown_until = 0

        # Red ring fade
        self.error_mode = False
        self.error_until = 0
        self.error_fade_duration = 2.0
        self.error_max_alpha = 180

        # Red screen-shadow fade
        self.screen_error_mode = False
        self.screen_error_until = 0
        self.screen_error_fade_duration = 2.0
        self.screen_error_max_alpha = 20  # gentle, easy on eyes

        # Green screen fade (correct)
        self.screen_correct_mode = False
        self.screen_correct_until = 0
        self.screen_correct_fade_duration = 2.0
        self.screen_correct_max_alpha = 20    # soft, same strength as red


        # Build idle circle
        self._build_idle_ring()

    @property
    def red_fade_time_left(self):
        if not self.screen_error_mode:
            return 0.0
        return max(0.0, self.screen_error_until - time.time())
    
    @property
    def finished(self):
        return (not self.animating) and self.angle >= 360


    # -------------------------------------------------
    # BUILD IDLE YELLOW RING
    # -------------------------------------------------
    def _build_idle_ring(self):
        glow_offset = 10
        max_radius = self.outer_radius + glow_offset
        size = max_radius * 2

        surf = pygame.Surface((size, size), pygame.SRCALPHA)
        center = (max_radius, max_radius)

        glow_color = (255, 255, 150, 70)
        pygame.draw.circle(surf, glow_color, center, self.outer_radius + glow_offset, 20)
        pygame.draw.circle(surf, self.idle_color, center, self.outer_radius, 10)
        pygame.draw.circle(surf, (0, 0, 0, 0), center, 2)

        self._cached_idle = surf

    # -------------------------------------------------
    # PUBLIC CONTROLS
    # -------------------------------------------------
    def start_animation(self):
        if self.error_mode or self.screen_error_mode:
            return
        if not self.animating and not self.cooldown_green:
            self.angle = 0
            self.animating = True
            self._cached_angle = None
            self.hold_until = 0

    def stop_animation(self):
        self.animating = False
        self.angle = 360
        self._cached_angle = None
        self.hold_until = 0

    def trigger_correct(self):
        # Stop any animation immediately
        self.animating = False
        self.angle = 360
        self._cached_angle = None

        # Start green fade
        self.screen_correct_mode = True
        self.screen_correct_until = time.time() + self.screen_correct_fade_duration

    def trigger_wrong(self):
        # Cursor ring fade
        self.error_mode = True
        self.error_until = time.time() + self.error_fade_duration

        # Stop any green animation
        self.animating = False
        self.angle = 360
        self._cached_angle = None

        # Screen shadow fade
        self.screen_error_mode = True
        self.screen_error_until = time.time() + self.screen_error_fade_duration

    # -------------------------------------------------
    # BUILD GREEN ARC
    # -------------------------------------------------
    def _build_arc(self):
        radius = 65
        surf = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)

        start_angle = -90
        end_angle = start_angle + self.angle + 5

        points = [(radius, radius)]
        for a in range(start_angle, int(end_angle) + 1):
            rad = math.radians(a)
            x = radius + math.cos(rad) * radius
            y = radius + math.sin(rad) * radius
            points.append((x, y))

        pygame.draw.polygon(surf, self.active_color, points)
        pygame.draw.circle(surf, (0, 0, 0, 0), (radius, radius), 51)

        return surf

    # -------------------------------------------------
    # UPDATE
    # -------------------------------------------------
    def update(self):
        now = time.time()

        # Handle red ring fade
        if self.error_mode:
            if now >= self.error_until:
                self.error_mode = False
            return  # freeze animation while red ring is active

        # Handle green cooldown
        if self.cooldown_green and now > self.cooldown_until:
            self.cooldown_green = False

        # Progress green animation
        if self.animating:
            self.angle += self.speed

            if self.angle >= 360:
                self.angle = 360
                self.animating = False

                self.cooldown_green = True
                self.cooldown_until = now + 1
                self.hold_until = now + 0.4

    # -------------------------------------------------
    # DRAW
    # -------------------------------------------------
    def draw(self, surface, pos):
        now = time.time()

        # --- Screen red shadow fade ---
# --- Fullscreen soft red fade ---
        if self.screen_error_mode:
            time_left = self.screen_error_until - now

            if time_left <= 0:
                self.screen_error_mode = False
            else:
                alpha = int((time_left / self.screen_error_fade_duration) * self.screen_error_max_alpha)

                width, height = surface.get_size()

                # Make full-screen red overlay (very faint)
                fullscreen_red = pygame.Surface((width, height), pygame.SRCALPHA)
                fullscreen_red.fill((255, 0, 0, alpha))

                # Blit the red overlay
                surface.blit(fullscreen_red, (0, 0))

        # --- Fullscreen soft GREEN fade ---
        if self.screen_correct_mode:
            time_left = self.screen_correct_until - now

            if time_left <= 0:
                self.screen_correct_mode = False
            else:
                alpha = int((time_left / self.screen_correct_fade_duration) * self.screen_correct_max_alpha)

                width, height = surface.get_size()

                fullscreen_green = pygame.Surface((width, height), pygame.SRCALPHA)
                fullscreen_green.fill((0, 255, 0, alpha))

                surface.blit(fullscreen_green, (0, 0))



        # Draw idle ring
        surface.blit(self._cached_idle, self._cached_idle.get_rect(center=pos))

        # --- Cursor red ring fade ---
        if self.error_mode:
            time_left = self.error_until - now
            if time_left > 0:
                alpha = int((time_left / self.error_fade_duration) * self.error_max_alpha)
                red_overlay = pygame.Surface(self._cached_idle.get_size(), pygame.SRCALPHA)

                pygame.draw.circle(
                    red_overlay,
                    (255, 0, 0, alpha),
                    (red_overlay.get_width() // 2, red_overlay.get_height() // 2),
                    self.outer_radius + 5,
                    15
                )
                surface.blit(red_overlay, red_overlay.get_rect(center=pos))

            return

        # --- Hold finished green arc ---
        if not self.animating and self.angle >= 360:
            if now < self.hold_until and self._cached_overlay:
                surface.blit(self._cached_overlay, self._cached_overlay.get_rect(center=pos))
            return

        # --- Build new arc if needed ---
        if self._cached_angle != self.angle:
            self._cached_overlay = self._build_arc()
            self._cached_angle = self.angle

        # Draw green arc
        surface.blit(self._cached_overlay, self._cached_overlay.get_rect(center=pos))
