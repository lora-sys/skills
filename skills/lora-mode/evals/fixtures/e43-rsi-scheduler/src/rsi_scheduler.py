"""Small reproduction of a shared GPU trial scheduler with expiring leases."""

class Scheduler:
    def __init__(self, capacity: int) -> None:
        self.capacity = capacity
        self.active = {}
        self.completed = set()
        self.next_lease = 0

    def claim(self, trial_id, worker_id, after_capacity_check=None):
        if trial_id in self.completed or trial_id in self.active or len(self.active) >= self.capacity:
            return None
        if after_capacity_check is not None:
            after_capacity_check()
        self.next_lease += 1
        lease = self.next_lease
        self.active[trial_id] = (worker_id, lease)
        return lease

    def expire(self, trial_id):
        return self.active.pop(trial_id, None) is not None

    def complete(self, trial_id, worker_id, lease):
        if self.active.get(trial_id) != (worker_id, lease):
            return False
        del self.active[trial_id]
        self.completed.add(trial_id)
        return True
