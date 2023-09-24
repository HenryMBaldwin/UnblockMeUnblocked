import json
import os
import time
import generate_level
import unblock

class Level_Factory:

    def __init__(self):
        self.generator = generate_level.Generator()
        self.unblocker = unblock.Unblocker()
        self.unique_states_file = "levels/unique_game_states.txt"  # Set the file path to the levels folder
        self.unique_game_states = self.load_unique_game_states()  # Initialize the set by loading from the file

    def load_unique_game_states(self):
        unique_states = set()
        if os.path.exists(self.unique_states_file):
            with open(self.unique_states_file, "r") as file:
                for line in file:
                    unique_states.add(line.strip())
        return unique_states

    def save_unique_game_states(self):
        with open(self.unique_states_file, "w") as states_file:
            for state_str in self.unique_game_states:
                states_file.write(state_str + "\n")

    def generate_levels(self, num, solvable=True):
        for i in range(num):
            while True:
                grid_data = self.generator.generate_level()
                grid = grid_data["grid"]
                state_str = ''.join(''.join(row) for row in grid)

                if state_str not in self.unique_game_states:
                    solution = self.unblocker.solve_board(board=grid, smooth=False)

                    grid_data["solution"] = solution
                    if len(solution) != 0 and solvable:
                        print("Level " + str(i))
                        for move in solution:
                            print(move)

                        grid_data["solvable"] = True
                        grid_data["moves_to_solve"] = len(solution)
                        self.save_level(grid_data)

                    # Add to the set and save if unique
                    self.unique_game_states.add(state_str)
                    self.save_unique_game_states()
                    break
                elif not solvable:
                    break

    def save_level(self, level_data, filename="levels/level_data.json"):
        if os.path.exists(filename):
            with open(filename, "r") as file:
                existing_data = json.load(file)
        else:
            existing_data = []

        existing_data.append(level_data)

        with open(filename, "w") as file:
            json.dump(existing_data, file, indent=4)

lfactory = Level_Factory()

st = time.time()
lfactory.generate_levels(1000, True)
et = time.time()

print(str(et - st))
