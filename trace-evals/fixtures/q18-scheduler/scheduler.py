"""简易任务调度器：worker 认领并执行任务。"""
import time


class Task:
    def __init__(self, tid):
        self.tid = tid
        self.claimed_by = None
        self.claimed_at = None
        self.done = False


class Scheduler:
    LEASE_SECONDS = 30

    def __init__(self):
        self.tasks = {}

    def add(self, tid):
        self.tasks[tid] = Task(tid)

    def claim(self, tid, worker):
        task = self.tasks[tid]
        if task.done:
            return None
        if task.claimed_by is not None:
            # BUG: 不检查租约是否过期，崩溃的 worker 会永久占用任务
            return None
        task.claimed_by = worker
        task.claimed_at = time.time()
        return task

    def complete(self, tid, worker):
        task = self.tasks[tid]
        if task.claimed_by != worker:
            return False
        task.done = True
        task.claimed_by = None
        return True
