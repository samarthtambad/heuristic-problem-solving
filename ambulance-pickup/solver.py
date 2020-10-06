#!/usr/bin/python3

import sys

class AmbulancePickup:
    def __init__(self, file_path):
        self.x_loc = []
        self.y_loc = []
        self.rescue_time = []
        self.num_ambulance = []
        
        self.read_input(file_path)
        # self.print_input()

    def read_input(self, file_path):
        with open(file_path) as fp:
            state = 0
            for cnt, line in enumerate(fp):
                if len(line.strip()) == 0:
                    continue
                if state == 0:
                    # person(xloc,yloc,rescuetime)
                    state = 1
                elif state == 1:
                    ln = line.strip().split(",")
                    if line[0].isdigit():
                        # read person's position and save time
                        self.x_loc.append(int(ln[0]))
                        self.y_loc.append(int(ln[1]))
                        self.rescue_time.append(int(ln[2]))
                        # print("{0}".format(ln))
                    else:
                        # hospital(numambulance)
                        state = 2
                elif state == 2:
                    # read number of ambulances at each hospital
                    ln = line.strip()
                    self.num_ambulance.append(int(ln))
                    # print("{0}".format(ln))

    def print_input(self):
        n = len(self.x_loc)
        
        print("x_loc \t y_loc \t rescue_time")
        for i in range(n):
            print("{0} \t {1} \t {2}".format(self.x_loc[i], self.y_loc[i], self.rescue_time[i]))
        
        print("num_ambulance")
        for i in range(len(self.num_ambulance)):
            print(self.num_ambulance[i])

    def generate_output(self):
        pass


if __name__ == "__main__":
    input_file = sys.argv[1]
    print("input_file", input_file)

    game = AmbulancePickup(input_file)
