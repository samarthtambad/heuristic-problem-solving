
class Hospital:
    def __init__(self, hid, x, y, num_ambulance):
        self.id = hid 
        self.x = x
        self.y = y
        self.num_ambulance = num_ambulance
        self.size = 0
        self.persons = []

        # computed
        self.paths = []
    
    def add_person(self, person):
        self.persons.append(person)
        self.size += 1

    def find_paths(self):
        
        pass
    
    def __str__(self):
        return "Hospital: {0} ({1}, {2}) {3} {4}\n".format(self.id, self.x, self.y, self.num_ambulance, self.size)

    def __repr__(self):
        return "Hospital: {0} ({1}, {2}) {3} {4}\n".format(self.id, self.x, self.y, self.num_ambulance, self.size)