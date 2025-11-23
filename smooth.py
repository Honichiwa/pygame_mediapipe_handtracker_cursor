# smooth.py — Adaptive smoothing + dead-zone filtering for cursor stabilization

class CursorSmoother:
    def __init__(self, dead_zone=12):
        self.dead_zone = dead_zone

        # internal state
        self.last_x = None
        self.last_y = None
        self.smooth_x = None
        self.smooth_y = None

    # ---------------------------------------------------------

    def update(self, tx, ty):
        """Update smoothing based on new target position (tx, ty). Returns (sx, sy)."""

        # Initialize on first call
        if self.last_x is None:
            self.last_x = tx
            self.last_y = ty
            self.smooth_x = tx
            self.smooth_y = ty
            return tx, ty

        # -----------------------------
        # DEAD ZONE (ignore tiny motion)
        # -----------------------------
        dx = tx - self.last_x
        dy = ty - self.last_y

        if abs(dx) < self.dead_zone:
            tx = self.last_x

        if abs(dy) < self.dead_zone:
            ty = self.last_y

        # -----------------------------
        # ADAPTIVE SMOOTHING
        # -----------------------------

        # movement speed
        vel = abs(tx - self.last_x) + abs(ty - self.last_y)
        vel_clamped = max(1, min(vel, 80))

        # adaptive interpolation
        # slow movement → more smoothing
        # fast movement → more responsive
        adaptive_alpha = 0.25 - (0.20 * (1 - (vel_clamped / 80)))

        # apply interpolation
        self.last_x += (tx - self.last_x) * adaptive_alpha
        self.last_y += (ty - self.last_y) * adaptive_alpha

        # -----------------------------
        # MICRO-SMOOTHING
        # -----------------------------
        micro_alpha = 0.10 if vel_clamped > 25 else 0.05

        self.smooth_x += (self.last_x - self.smooth_x) * micro_alpha
        self.smooth_y += (self.last_y - self.smooth_y) * micro_alpha

        return self.smooth_x, self.smooth_y
