"""Scalar animation track used by the combat preview."""


class AnimationTrack:
    def __init__(self, start_value, end_value, duration):
        self.start_value = start_value
        self.end_value = end_value
        self.duration = duration

    def sample(self, elapsed):
        progress = min(max(elapsed / self.duration, 0.0), 1.0)
        return self.start_value + (self.end_value - self.start_value) * progress
