import threading
import unittest

from src.rsi_scheduler import Scheduler


class SchedulerConcurrencyTests(unittest.TestCase):
    def test_two_workers_cannot_claim_the_last_gpu_slot(self):
        scheduler = Scheduler(capacity=1)
        after_check = threading.Barrier(2)
        results = []

        def claim(trial_id, worker_id):
            results.append(scheduler.claim(trial_id, worker_id, after_check.wait))

        workers = [
            threading.Thread(target=claim, args=("trial-a", "worker-a")),
            threading.Thread(target=claim, args=("trial-b", "worker-b")),
        ]
        for worker in workers:
            worker.start()
        for worker in workers:
            worker.join(timeout=2)

        self.assertTrue(all(not worker.is_alive() for worker in workers))
        self.assertEqual(sum(result is not None for result in results), 1)
        self.assertLessEqual(len(scheduler.active), scheduler.capacity)

    def test_expired_worker_cannot_complete_reclaimed_trial(self):
        scheduler = Scheduler(capacity=1)
        old_lease = scheduler.claim("trial-a", "worker-a")
        self.assertTrue(scheduler.expire("trial-a"))
        new_lease = scheduler.claim("trial-a", "worker-b")
        self.assertNotEqual(old_lease, new_lease)
        self.assertFalse(scheduler.complete("trial-a", "worker-a", old_lease))
        self.assertTrue(scheduler.complete("trial-a", "worker-b", new_lease))

    def test_completed_trial_cannot_be_claimed_again(self):
        scheduler = Scheduler(capacity=1)
        lease = scheduler.claim("trial-a", "worker-a")
        self.assertTrue(scheduler.complete("trial-a", "worker-a", lease))
        self.assertIsNone(scheduler.claim("trial-a", "worker-b"))


if __name__ == "__main__":
    unittest.main()
