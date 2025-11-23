import pygame
import math
import time

class SmoothCursor:
    def __init__(self, outer_radius=60, inner_radius=20, speed=5, color=(0, 255, 0)):
        self.outer_radius = outer_radius
        self.inner_radius = inner_radius
        self.speed = speed

        self.active_color = color      # green during pinch
        self.idle_color = (255, 255, 51, 200)  # yellow when not pinched

        # Animation state
        self.angle = 360    # full circle by default
        self.animating = False

        # Cached frames
        self._cached_idle = None
        self._cached_angle = None
        self._cached_overlay = None

        self.hold_time = 0.2       # seconds to keep green visible
        self.hold_until = 0   

        # Prebuild idle ring once
        self._build_idle_ring()

    # -------------------------------------------------

    def _build_idle_ring(self):
        glow_offset = 10  # how much bigger the glow ring is

        max_radius = self.outer_radius + glow_offset

        # Create a surface large enough to fit everything
        size = max_radius * 2
        surf = pygame.Surface((size, size), pygame.SRCALPHA)

        center = (max_radius, max_radius)

        glow_color = (255, 255, 150, 70)

        pygame.draw.circle(
            surf,
            glow_color,
            center,
            self.outer_radius + glow_offset,
            20
        )

        # Main yellow ring
        pygame.draw.circle(
            surf,
            self.idle_color,
            center,
            self.outer_radius,
            10
        )


        # Inner hole
        pygame.draw.circle(
            surf,
            (0, 0, 0, 0),
            center,
            2
        )

        self._cached_idle = surf


    # -------------------------------------------------

    def start_animation(self):
        if not self.animating:
            self.angle = 0
            self.animating = True
            self._cached_angle = None
            self.hold_until = 0        # reset hold timer

    
    def stop_animation(self):
        """Immediately stop green animation and return to idle."""
        if self.animating:
            self.animating = False
            self.angle = 360
            self._cached_angle = None
            self.hold_until = 0


    # -------------------------------------------------

    def _build_arc(self):
        """Build the green animated arc polygon."""
        number = 65
        self.outer_radius = number
        surf = pygame.Surface((self.outer_radius * 2, self.outer_radius * 2), pygame.SRCALPHA)

        start_angle = -90
        end_angle = start_angle + self.angle + 5

        points = [(self.outer_radius, self.outer_radius)]
        for a in range(start_angle, int(end_angle) + 1):
            rad = math.radians(a)
            x = self.outer_radius + math.cos(rad) * self.outer_radius
            y = self.outer_radius + math.sin(rad) * self.outer_radius
            points.append((x, y))

        if len(points) > 2:
            pygame.draw.polygon(surf, self.active_color, points)

        # Punch inner hole
        pygame.draw.circle(
            surf,
            (0, 0, 0, 0),
            (self.outer_radius, self.outer_radius),
            51
        )

        return surf

    # -------------------------------------------------
    def update(self):
        if self.animating:
            self.angle += self.speed
            if self.angle >= 360:
                self.angle = 360
                self.animating = False

                self.hold_until = time.time() + 0.4   # 1 second hold


    # -------------------------------------------------

    def draw(self, surface, pos):

        # Always draw idle ring
        surface.blit(self._cached_idle, self._cached_idle.get_rect(center=pos))

        # If animation finished, but we are in hold time → keep green ring visible
        if not self.animating and self.angle >= 360:
            if time.time() < self.hold_until:
                # Still within 1 second — draw last green arc
                if self._cached_overlay:
                    surface.blit(self._cached_overlay, self._cached_overlay.get_rect(center=pos))
            return

        # Build new arc frame if angle changed
        if self._cached_angle != self.angle:
            self._cached_overlay = self._build_arc()
            self._cached_angle = self.angle

        # Draw green arc
        surface.blit(self._cached_overlay, self._cached_overlay.get_rect(center=pos))

