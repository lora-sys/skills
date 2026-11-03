import unittest

from animation import AnimationTrack


class AnimationTrackTests(unittest.TestCase):
    def test_track_keeps_endpoints_and_duration(self):
        track = AnimationTrack(0.0, 1.0, 0.5)
        self.assertEqual(track.sample(0.0), 0.0)
        self.assertEqual(track.sample(0.5), 1.0)
        self.assertEqual(track.duration, 0.5)


if __name__ == "__main__":
    unittest.main()
