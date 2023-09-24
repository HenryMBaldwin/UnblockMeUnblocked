import json
import os
import time
import generate_level
import unblock
import multiprocessing as mp
from threading import Lock
class Level_Factory:

    def __init__(self):
        self.generator = generate_level.Generator()
        self.unblocker = unblock.Unblocker()
        self.unique_states_file = "levels/unique_game_states.txt"  # Set the file path to the levels folder
        self.unique_game_states = self.load_unique_game_states()  # Initialize the set by loading from the file
        self.gen_mutex = Lock() #mutex used in level generation
        self.gs_mutex = Lock()	#mutex used in game state reading and writing
        self.ld_mutex = Lock()	#mutex used in level data reading and writing

    def load_unique_game_states(self):
    	self.gs_mutex.acquire()
        unique_states = set()
        if os.path.exists(self.unique_states_file):
            with open(self.unique_states_file, "r") as file:
                for line in file:
                    unique_states.add(line.strip())
        self.gs_mutex.release()
        return unique_states
        

    def save_unique_game_states(self):
    	self.gs_mutex.acquire()
        with open(self.unique_states_file, "w") as states_file:
            for state_str in self.unique_game_states:
                states_file.write(state_str + "\n")
        self.gs_mutex.release()

    def parallel_handler(self, num, solvable = True, gen_mutex, gs_mutex, ld_mutex):
    	#ensuring mutexes are the same between parallel processes
    	#not exactly sure if this is necassary but it is a fairly simple precaution to implement
    	self.gen_mutex = gen_mutex
    	self.gs_mutex = gs_mutex
    	self.ld_mutex = ld_mutex
    	generate_levels(num, solvable)

    def generate_levels(self, num, solvable=True):
        for i in range(num):
            while True:
                grid_data = self.generator.generate_level()
                grid = grid_data["grid"]
                state_str = ''.join(''.join(row) for row in grid)
                
                self.gen_mutex.acquire()
                self.unique_game_states = load_unique_game_states()
              

                if state_str not in self.unique_game_states:
                	# Add to the set and save if unique
                	self.unique_game_states.add(state_str)
	                self.save_unique_game_states()
	                self.gen_mutex.release()

                    solution = self.unblocker.solve_board(board=grid, smooth=False)

                    grid_data["solution"] = solution
                    if len(solution) != 0 and solvable:
                        print("Level " + str(i))
                        for move in solution:
                            print(move)

                        grid_data["solvable"] = True
                        grid_data["moves_to_solve"] = len(solution)
                        self.save_level(grid_data)
	                    break

	                elif not solvable:
	                	grid_data["solvable"] = False
                        grid_data["moves_to_solve"] = -1
                        self.save_level(grid_data)
	                    break
	            else:
	            	#make sure to release mutex even if not unique
	            	self.gen_mutex.release()

                

    def save_level(self, level_data, filename="levels/level_data.json"):
    	self.ld_mutex.acquire()
        if os.path.exists(filename):
            with open(filename, "r") as file:
                existing_data = json.load(file)
        else:
            existing_data = []

        existing_data.append(level_data)

        with open(filename, "w") as file:
            json.dump(existing_data, file, indent=4)
        self.ld_mutex.release()

    def generate_levels_parallel(self, num_processes, num, solvable=True):
        gen_mutex = self.gen_mutex
        gs_mutex = self.gs_mutex
        ld_mutex = self.ld_mutex
        
        input_data = [(num, solvable, gen_mutex, gs_mutex, ld_mutex)] * num_processes

        with mp.Pool(processes=num_processes) as pool:
            pool.starmap(self.parallel_handler, input_data)

lfactory = Level_Factory()

st = time.time()
lfactory.generate_levels(1000, True)
et = time.time()

print(str(et - st))
