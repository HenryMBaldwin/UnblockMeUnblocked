import json
import os
import time
import generate_level
import unblock
import multiprocessing as mp
import numpy as np
import re
from multiprocessing import Lock

class Level_Factory:

    def __init__(self):
        self.generator = generate_level.Generator()
        self.unblocker = unblock.Unblocker()
        self.gen_mutex = Lock() #mutex used in level generation
        self.gs_mutex = Lock()	#mutex used in game state reading and writing
        self.ld_mutex = Lock()	#mutex used in level data reading and writing
        self.unique_states_file = "levels/unique_game_states.txt"  # Set the file path to the levels folder
        self.unique_game_states = self.load_unique_game_states()  # Initialize the set by loading from the file

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

    def parallel_handler(self, gen_mutex, gs_mutex, ld_mutex, num, solvable = True):
    	#ensuring mutexes are the same between parallel processes
    	#not exactly sure if this is necassary but it is a fairly simple precaution to implement
    	self.gen_mutex = gen_mutex
    	self.gs_mutex = gs_mutex
    	self.ld_mutex = ld_mutex
    	print(gs_mutex)
    	self.generate_levels(num, solvable)

    def generate_levels(self, num, solvable=True):
        for i in range(num):
            while True:
                grid_data = self.generator.generate_level()
                grid = grid_data["grid"]
                state_str = ''.join(''.join(row) for row in grid)
                
                self.gen_mutex.acquire()
                self.unique_game_states = self.load_unique_game_states()
              

                if state_str not in self.unique_game_states:
                    # Add to the set and save if unique
                    self.unique_game_states.add(state_str)
                    self.save_unique_game_states()
                    self.gen_mutex.release()

                    solution = self.unblocker.solve_board(board=grid, smooth=False, training = True)


                    grid_data["solution"] = solution
                    if len(solution) != 0 and solvable:
                        print("Level " + str(i))
                        for move in solution:
                            print(move[1])

                        grid_data["solvable"] = True
                        grid_data["moves_to_solve"] = len(solution)
                        self.save_level(grid_data)

                        last_state = None
                        for sol_set in solution:
                            state = sol_set[0]
                            move = sol_set[1]
                            if last_state != None:
                                #convert the last state to a one hot
                                one_hot_state = self.convert_to_one_hot(last_state)
                                norm_move = self.convert_to_normalized(move)
                                #save current move and last state, as each [state, move] pair is the current state and the move
                                #that **led** to the current state
                                self.save_training_data(one_hot_state.flatten(), norm_move)
                            last_state = state
                        break

                    elif not solvable:
                        grid_data["solvable"] = False
                        grid_data["moves_to_solve"] = -1
                        self.save_level(grid_data)
                        break
                else:
                    #make sure to release mutex even if not unique
                    self.gen_mutex.release()

    import numpy as np

    #normalize moves
    def convert_to_normalized(self,move):
         # Define a regular expression pattern to extract coordinates
        pattern = re.compile(r"\((\d+),(\d+)\) -> \((\d+),(\d+)\)")
        
        # Search the string for matches
        match = pattern.search(move)
        
        # Validate the input string
        if match is None:
            raise ValueError("Input string format is invalid. Expected format: (x1,y1) -> (x2,y2)")
            
        # Extract coordinates and convert them to integers
        x1, y1, x2, y2 = map(int, match.groups())
        
        # Create a NumPy array from the coordinates
        coord_array = np.array([x1/5, y1/5, x2/5, y2/5])
        
        return coord_array

    def convert_to_one_hot(self, state):

        #self.unblocker.print_state(state)
        # Define a mapping from character to one-hot encoding
        char_to_one_hot = {
            ".": [1, 0, 0, 0, 0, 0],
            "A": [0, 1, 0, 0, 0, 0],
            "B": [0, 0, 1, 0, 0, 0],
            "R": [0, 0, 0, 1, 0, 0],
            "a": [0, 0, 0, 0, 1, 0],
            "b": [0, 0, 0, 0, 0, 1],
        }
        
        # Validate the input state
        if not (isinstance(state, list) and all(isinstance(row, list) and len(row) == 6 for row in state) and len(state) == 6):
            raise ValueError("Input state must be a 6x6 array.")
        
        # Initialize a 6x6x6 numpy array filled with zeros
        one_hot_array = np.zeros((6, 6, 6), dtype=int)

        # Fill the numpy array with one-hot encodings
        for i in range(6):
            for j in range(6):
                char = state[i][j]
                if char not in char_to_one_hot:
                    raise ValueError(f"Invalid character {char} in state at position {i}, {j}")
                one_hot_encoding = char_to_one_hot[char]
                one_hot_array[i, j] = one_hot_encoding
                
        return one_hot_array
            

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

    def save_training_data(self, state, move, filename="levels/training_data.json"):
        if isinstance(state, np.ndarray):
            state = state.tolist()
        if isinstance(move, np.ndarray):
            move = move.tolist()
            
        try:
            with open(filename, 'r') as f:
                data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            data = []
            
        data.append({
            "state": state,
            "move": move
        })
            
        with open(filename, 'w') as f:
            json.dump(data, f, indent = 4)


    def generate_levels_parallel(self, num_processes, num, solvable=True):
        num = num//num_processes
        gen_mutex = self.gen_mutex
        gs_mutex = self.gs_mutex
        ld_mutex = self.ld_mutex

        input_data = [(num, solvable)] * num_processes

        with mp.Pool(processes=num_processes) as pool:
            pool.starmap(self.parallel_handler, input_data)
def run():
    lfactory = Level_Factory()

    st = time.time()
    lfactory.generate_levels(2000, True)
    et = time.time()

    print(str(et - st))
