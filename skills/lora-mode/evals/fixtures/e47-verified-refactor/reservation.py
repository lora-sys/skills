class ReservationBook:
    def __init__(self, capacity):
        self.capacity = capacity
        self.records = {}

    def create(self, request_id, owner):
        if request_id in self.records:
            return False
        occupied = sum(status in ("held", "confirmed") for _, status in self.records.values())
        if occupied >= self.capacity:
            return False
        self.records[request_id] = (owner, "held")
        return True

    def confirm(self, request_id, owner):
        current = self.records.get(request_id)
        if current != (owner, "held"):
            return False
        self.records[request_id] = (owner, "confirmed")
        return True

    def cancel(self, request_id, owner):
        current = self.records.get(request_id)
        if current != (owner, "held"):
            return False
        del self.records[request_id]
        return True
