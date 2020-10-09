
class Person:
    def __init__(self, pid, x, y, rescue_time):
        self.id = pid
        self.x = x
        self.y = y
        self.rescue_time = rescue_time
        
        self.hospital_idx = None
        self.hospital_x = None
        self.hospital_y = None
    
    def assign_hospital(self, hospital_id, x, y):
        self.hospital_id = hospital_id
        self.hospital_x = x
        self.hospital_y = y
    
    def time_from_hospital(self):
        return abs(self.x - self.hospital_x) + abs(self.y - self.hospital_y)

    def get_time_from(self, px, py):
        return abs(self.x - px) + abs(self.y - py)

    def __str__(self):
        return "Person: {0} ({1}, {2}) {3}s\n".format(self.id, self.x, self.y, self.rescue_time)

    def __repr__(self):
        return "Person: {0} ({1}, {2}) {3}s\n".format(self.id, self.x, self.y, self.rescue_time)