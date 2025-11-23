# cursor_gaussian.py
import pygame
import math

class SmoothCursor:
    """
    Soft gaussian-like glow using 3 fast layered rings.
    Idle: full yellow ring + soft halo.
    Pinch: green arc grows over idle.
    """
    def __init__(self, outer_radius=60, inner_radius=20, speed=5, color=(0, 255, 0)):
        self.outer_radius = outer_radius
        self.inner_radius = inner_radius
        self.speed = speed

        self.active_color = color
        self.idle_color = (255, 255, 51, 200)   # yellow ring
        self.glow_color = (255, 255, 120, 40)   # soft yellow glow

        self.angle = 360
        self.animating = False

        self._cached_idle = None
        self._cached_angle = None
        self._cached_overlay = None

        self._build_idle_ring()

    def _build_idle_ring(self):
        glow_offset = 12
        max_radius = self.outer_radius + glow_offset
        size = max_radius * 2
        surf = pygame.Surface((size, size), pygame.SRCALPHA)
        center = (max_radius, max_radius)

        # Fast fake-gaussian glow: 3 soft rings outward
        layers = [
            (self.outer_radius + 6,  18, 30),
            (self.outer_radius + 10, 14, 22),
            (self.outer_radius + 14, 10, 16),
        ]
        for r, w, a in layers:
            c = (self.glow_color[0], self.glow_color[1], self.glow_color[2], a)
            pygame.draw.circle(surf, c, center, r, w)

        # Main idle ring
        pygame.draw.circle(surf, self.idle_color, center, self.outer_radius, 10)

        # Tiny inner hole
        pygame.draw.circle(surf, (0, 0, 0, 0), center, 2)

        self._cached_idle = surf

    def start_animation(self):
        self.angle = 0
        self.animating = True
        self._cached_angle = None

    def set_idle(self):
        self.angle = 360
        self.animating = False
        self._cached_angle = None

    def _build_arc(self):
        max_r = self.outer_radius + 12
        size = max_r * 2
        surf = pygame.Surface((size, size), pygame.SRCALPHA)
        center = (max_r, max_r)

        # Arc polygon
        start_angle = -90
        end_angle = start_angle + self.angle
        points = [center]

        for a in range(start_angle, int(end_angle) + 1):
            rad = math.radians(a)
            x = center[0] + math.cos(rad) * self.outer_radius
            y = center[1] + math.sin(rad) * self.outer_radius
            points.append((x, y))

        if len(points) > 2:
            pygame.draw.polygon(surf, self.active_color, points)

        # Punch hole
        pygame.draw.circle(surf, (0, 0, 0, 0), center, self.inner_radius)

        return surf

    def update(self):
        if self.animating:
            self.angle += self.speed
            if self.angle >= 360:
                self.angle = 360
                self.animating = False

    def draw(self, surface, pos):
        surface.blit(self._cached_idle, self._cached_idle.get_rect(center=pos))

        if self.angle >= 360 and not self.animating:
            return

        if self._cached_angle != self.angle:
            self._cached_overlay = self._build_arc()
            self._cached_angle = self.angle

        surface.blit(self._cached_overlay, self._cached_overlay.get_rect(center=pos))
