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
        self.ambulances = [Ambulance(self) for a in range(num_ambulances)]
        return

    def __repr__(self):
        return f'{self.hid}: ({self.x},{self.y})'

    def remove_ambulance(self, a):
        self.ambulances.remove(a)
        self.num_ambulances -= 1
        return

    def add_ambulance(self, a):
        self.ambulances.append(a)
        self.num_ambulances += 1
        return

    def choose_ambulance(self):
        return min(self.ambulances, key=lambda a: a.time)

    def rescue(self, people_on_ambulance, hospitals, end_hospital):
        ambulance = self.choose_ambulance()
        self.remove_ambulance(ambulance)
        if 4 < len(people_on_ambulance):
            raise IllegalPlanError('Cannot rescue more than four people at once: %s' % people_on_ambulance)
        already_rescued = [p for p in people_on_ambulance if p.rescued]
        if already_rescued:
            raise IllegalPlanError('Person already rescued: %s' % already_rescued)
        # t: time to take
        # note: we don't have to go back to the starting hospital
        time_for_this_trip = 0
        curr_location = self
        for p in people_on_ambulance:
            time_for_this_trip += travel_time(curr_location, p)  # add time for traveling to person
            time_for_this_trip += 1  # add 1 minute for loading the person
            curr_location = p
        time_for_this_trip += travel_time(curr_location, end_hospital)
        time_for_this_trip += 1  # add time for unloading up to 4 people
        ambulance.add_time(time_for_this_trip)  # proceed the time for this ambulance
        if [p for p in people_on_ambulance if p.rescue_time < ambulance.time]:
            raise IllegalPlanError(f'Either of these people cannot make it: {people_on_ambulance}, ambulance would '
                                   f'arrive at time: {ambulance.time} which is too late')
        for p in people_on_ambulance:
            p.rescued = True
        end_hospital.add_ambulance(ambulance)
        print('Rescued:', ' and '.join(map(str, people_on_ambulance)), 'taking time:', time_for_this_trip,
              ' with the ambulance ending at hospital', end_hospital)
        return


# Ambulance object
AID = 0


class Ambulance:

    def __init__(self, initial_hospital):
        global AID
        AID += 1
        self.aid = AID
        self.time = 0

    def add_time(self, time_to_add):
        self.time += time_to_add


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
            start_hospital, end_hospital = None, None
            people_to_rescue = []
            for (i, (w, num_ambulances)) in enumerate(p1.findall(line)):
                hospital_match = p2.match(w)
                if hospital_match:
                    # Hospital hospital_id:(x,y)
                    (hospital_id, x, y) = list(map(int, hospital_match.groups()))
                    if hospital_id <= 0 or hospital_id > len(hospitals):
                        raise FormatSyntaxError(f'Illegal hospital id: {hospital_id}')
                    if i == 0:
                        start_hospital = hospitals[hospital_id - 1]
                        if start_hospital.x != x or start_hospital.y != y:
                            raise DataMismatchError(
                                f'Start Hospital location mismatch: {start_hospital} != {hospital_id}: ({x},{y})')
                        if start_hospital.num_ambulances == 0:
                            raise FormatSyntaxError(f'Start hospital ({start_hospital}) has no ambulances')
                    else:
                        end_hospital = hospitals[hospital_id - 1]
                        if end_hospital.x != x or end_hospital.y != y:
                            raise DataMismatchError(
                                f'End Hospital location mismatch: {end_hospital} != {hospital_id}: ({x},{y})')

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
                    people_to_rescue.append(person)
                    continue
                # error
                raise FormatSyntaxError('Expected "n:(x,y)" or "n:(x,y,t)": %r' % line)

            if not start_hospital or not people_to_rescue or not end_hospital:
                print('!!! Insufficient data: %r' % line, file=sys.stderr)
                continue
            start_hospital.rescue(people_to_rescue, hospitals, end_hospital)
            # start_hospital.num_ambulances -= 1
            # end_hospital.num_ambulances += 1
            score += len(people_to_rescue)
        except ValidationError as x:
            print('!!!', x, file=sys.stderr)
    print('Total score:', score)
    return


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print('usage: validator.py datafile resultfile')
        sys.exit(2)
    people_data, hospital_data = read_input_data(sys.argv[1])
    del sys.argv[1]
    read_results(people_data, hospital_data)
