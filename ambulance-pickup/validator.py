# !/usr/bin/env python

import fileinput
import re
import sys


# Exception classes
class ValidationError(ValueError):
    pass


class FormatSyntaxError(ValidationError):
    pass


class DataMismatchError(ValidationError):
    pass


class IllegalPlanError(ValidationError):
    pass


# travel time between two points a and b
def travel_time(a, b):
    return abs(a.x - b.x) + abs(a.y - b.y)


# Person object
PID = 0


class Person:

    def __init__(self, x, y, rescue_time):
        global PID
        PID += 1
        self.pid = PID
        self.x = x
        self.y = y
        self.rescue_time = rescue_time
        self.rescued = False
        return

    def __repr__(self):
        return f'{self.pid}: ({self.x}, {self.y}, {self.rescue_time})'


# Hospital object
HID = 0


class Hospital:

    def __init__(self, x, y, num_ambulances):
        global HID
        HID += 1
        self.hid = HID
        self.x = x
        self.y = y
        self.num_ambulances = num_ambulances
        # ambulance_time array represents the time each ambulance have already spent.
        # NOTE: this should be sorted in a decreasing order (larger value first).
        self.ambulance_time = [0] * num_ambulances
        return

    def __repr__(self):
        return f'{self.hid}: ({self.x},{self.y})'

    def decrement_number_of_ambulances(self, t):
        self.ambulance_time[t] -= 1
        if self.ambulance_time[t] == 0:
            del self.ambulance_time[t]
        return

    def increment_number_of_ambulances(self, t):
        if t not in self.ambulance_time:
            self.ambulance_time[t] = 0
        self.ambulance_time[t] += 1
        return

    def rescue(self, people_on_ambulance, hospitals):
        if 4 < len(people_on_ambulance):
            raise IllegalPlanError('Cannot rescue more than four people at once: %s' % people_on_ambulance)
        already_rescued = [p for p in people_on_ambulance if p.rescued]
        if already_rescued:
            raise IllegalPlanError('Person already rescued: %s' % already_rescued)
        # t: time to take
        # note: we don't have to go back to the starting hospital
        # so go to the closest from the last person
        t = 0
        curr_location = self
        for p in people_on_ambulance:
            t += travel_time(curr_location, p)  # add time for traveling to person
            t += 1  # add 1 minute for loading the person
            curr_location = p
        # look for closest hospital to return to
        closest_hospital = 0
        travel_time_to_closest_hospital = None
        for hosp in hospitals:
            temp_dist = travel_time(curr_location, hosp)
            if not travel_time_to_closest_hospital:
                travel_time_to_closest_hospital = temp_dist
                closest_hospital = hosp
            elif temp_dist < travel_time_to_closest_hospital:
                travel_time_to_closest_hospital = temp_dist
                closest_hospital = hosp
        t += travel_time_to_closest_hospital
        t += 1  # add time for unloading up to 4 people

        # check if there are any people on the ambulance that wont make it in time
        for (i, t0) in enumerate(self.ambulance_time):
            if not [p for p in people_on_ambulance if p.rescue_time < t0 + t]:
                break
        else:
            raise IllegalPlanError(f'Either of these people cannot make it: {people_on_ambulance}')
        # proceed the time.
        self.ambulance_time[i] += t
        # keep it sorted.
        self.ambulance_time.sort()
        self.ambulance_time.reverse()
        for p in people_on_ambulance:
            p.rescued = True
        print('Rescued:', ' and '.join(map(str, people_on_ambulance)), 'taking time:', t,
              ' with the ambulance ending at hospital', closest_hospital)
        return


def read_input_data(fname):
    print('Reading data:', fname, file=sys.stderr)
    people = []
    hospitals = []
    mode = 0  # 0: default, 1: people data, 2: hospital data
    with open(fname, 'r') as input_data:
        for line in input_data:
            line = line.strip().lower()
            if line.startswith("person") or line.startswith("people"):
                mode = 1
            elif line.startswith("hospital"):
                mode = 2
            elif line:
                if mode == 1:
                    (x, y, t) = list(map(int, line.split(",")))
                    people.append(Person(x, y, t))
                elif mode == 2:
                    (n,) = list(map(int, line.split(",")))
                    hospitals.append(Hospital(-1, -1, n))
    return people, hospitals


def read_results(people, hospitals):
    print('Reading results...', file=sys.stderr)
    p1 = re.compile(r'(\d+\s*:\s*\(\s*\d+\s*,\s*\d+(\s*,\s*\d+)?\s*\))')
    p2 = re.compile(r'(\d+)\s*:\s*\(\s*(\d+)\s*,\s*(\d+)\s*\)')
    p3 = re.compile(r'(\d+)\s*:\s*\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*\)')

    score = 0
    hospital_index = 0
    # reads from stdin by default, or from a result_file if specified in the command line args
    for line in fileinput.input():
        line = line.strip().lower()
        if not line:
            continue
        # check hospital coordinates
        if line.startswith('hospital'):
            # read in hospital coordinates and set on hospital object
            (x, y, num_ambulances) = list(map(int, line.replace('hospital:', '').split(',')))
            print(f"Hospital #{hospital_index + 1}: coordinates ({x},{y})")
            if not (x and y):
                raise ValidationError("Hospital coordinates not set: line".format(line))
            if num_ambulances != hospitals[hospital_index].num_ambulances:
                raise ValidationError(
                    f"Hospital's ambulance # does not match input "
                    f"(input={hospitals[hospital_index].num_ambulances}, "
                    f"results={num_ambulances})")
            hospitals[hospital_index].x = x
            hospitals[hospital_index].y = y
            hospital_index += 1
            continue

        # check ambulance movements
        if not line.startswith('ambulance'):
            print('!!! Ignored line: %r' % line, file=sys.stderr)
            continue
        try:
            hospital = None
            people_rescued = []
            for (i, (w, num_ambulances)) in enumerate(p1.findall(line)):
                hospital_match = p2.match(w)
                if hospital_match:
                    # Hospital hospital_id:(x,y)
                    if i != 0:
                        raise FormatSyntaxError('Specify a person now: %r' % line)
                    (hospital_id, x, y) = list(map(int, hospital_match.groups()))
                    if hospital_id <= 0 or hospital_id > len(hospitals):
                        raise FormatSyntaxError(f'Illegal hospital id: {hospital_id}')
                    hospital = hospitals[hospital_id - 1]
                    if hospital.x != x or hospital.y != y:
                        raise DataMismatchError(f'Hospital location mismatch: {hospital} != {hospital_id}: ({x},{y})')
                    continue
                person_match = p3.match(w)
                if person_match:
                    # Person n:(x,y,t)
                    if i == 0:
                        raise FormatSyntaxError('Specify a hospital first: %r' % line)
                    (person_id, x, y, rescue_time) = list(map(int, person_match.groups()))
                    if person_id <= 0 or person_id > len(people):
                        raise FormatSyntaxError(f'Illegal person id: {person_id}')
                    person = people[person_id - 1]
                    if person.x != x or person.y != y or person.rescue_time != rescue_time:
                        raise DataMismatchError(f'Person mismatch: {person} != {person_id}: ({x, y, rescue_time})')
                    people_rescued.append(person)
                    continue
                # error
                raise FormatSyntaxError('Expected "n:(x,y)" or "n:(x,y,t)": %r' % line)

            if not hospital or not people_rescued:
                print('!!! Insufficient data: %r' % line, file=sys.stderr)
                continue
            hospital.rescue(people_rescued, hospitals)
            score += len(people_rescued)
        except ValidationError as x:
            print('!!!', x, file=sys.stderr)
    print('Total score:', score)
    return


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print('usage: validator.py datafile resultfile') #resultfile is optional
        sys.exit(2)
    people_data, hospital_data = read_input_data(sys.argv[1])
    del sys.argv[1]
    read_results(people_data, hospital_data)
