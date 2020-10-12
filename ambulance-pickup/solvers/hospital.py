
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
        self.clusters = []
        self.people_locations = []
    
    def get_info(self):
        return [self.id, self.x, self.y]

    def add_person(self, person):
        self.persons.append(person)
        self.size += 1
    
    def get_time_from(self, cur_x, cur_y):
        return abs(self.x - cur_x) + abs(self.y - cur_y)

    def generate_clusters(self):
        pass

    def find_paths(self):
        persons_sorted = sorted(self.persons, key=lambda x: x.rescue_time)
        print(persons_sorted)

        load_time_per_person = 1
        unload_time = 1
        result = []

        path = [[] for _ in range(self.num_ambulance)]
        cur_time = [0 for _ in range(self.num_ambulance)]
        cur_x = [self.x for _ in range(self.num_ambulance)]
        cur_y = [self.y for _ in range(self.num_ambulance)]

        for person in persons_sorted:
            
            is_ignored = True

            for ambulance_idx in range(self.num_ambulance):
                time_cur_to_hospital = self.get_time_from(cur_x[ambulance_idx], cur_y[ambulance_idx]) # current location to hospital location
            
                if len(path[ambulance_idx]) == 4:
                    cur_time[ambulance_idx] = cur_time[ambulance_idx] + time_cur_to_hospital + unload_time
                    cur_x[ambulance_idx], cur_y[ambulance_idx] = self.x, self.y
                    result.append(path[ambulance_idx])
                    path[ambulance_idx] = []
            
                time_to_person = person.get_time_from(cur_x[ambulance_idx], cur_y[ambulance_idx])  # current location to person's location
                time_to_hospital = person.time_from_hospital()       # person's location to hospital location
            
                estimated_time = cur_time[ambulance_idx] + time_to_person + load_time_per_person + time_to_hospital + unload_time
                is_valid = True
                for person_in_path in path[ambulance_idx]:
                    if estimated_time > person_in_path.rescue_time:
                        is_valid = False
                        break

                if is_valid and estimated_time <= person.rescue_time:
                    is_ignored = False
                    path[ambulance_idx].append(person)
                    cur_time[ambulance_idx] = cur_time[ambulance_idx] + time_to_person + load_time_per_person
                    cur_x[ambulance_idx], cur_y[ambulance_idx] = person.x, person.y
                    break
            
            if is_ignored:
                for ambulance_idx in range(self.num_ambulance):
                    time_cur_to_hospital = self.get_time_from(cur_x[ambulance_idx], cur_y[ambulance_idx]) # current location to hospital location
                    time_to_person = person.get_time_from(cur_x[ambulance_idx], cur_y[ambulance_idx])     # current location to person's location
                    time_to_hospital = person.time_from_hospital()          # person's location to hospital location
                    
                    cur_time[ambulance_idx] = cur_time[ambulance_idx] + time_cur_to_hospital + unload_time
                    cur_x[ambulance_idx], cur_y[ambulance_idx] = self.x, self.y
                    result.append(path[ambulance_idx])
                    path[ambulance_idx] = []
                    
                    if cur_time[ambulance_idx] + time_to_hospital + load_time_per_person + time_to_hospital + unload_time <= person.rescue_time:
                        path.append(person)
                        cur_time[ambulance_idx] = cur_time[ambulance_idx] + time_to_person + load_time_per_person
                        cur_x[ambulance_idx], cur_y[ambulance_idx] = person.x, person.y
        
        res = []
        for person_list in result:
            ans = []
            for person in person_list:
                ans.append(person.id)
            res.append(ans)

        return res
    
    def __str__(self):
        return "Hospital: {0} ({1}, {2}) {3} {4}\n".format(self.id, self.x, self.y, self.num_ambulance, self.size)

    def __repr__(self):
        return "Hospital: {0} ({1}, {2}) {3} {4}\n".format(self.id, self.x, self.y, self.num_ambulance, self.size)