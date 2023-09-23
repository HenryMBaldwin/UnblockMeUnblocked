import json
import os
import generate_level
import unblock

#Produces solvable levels with metadata including solution
class Level_Factory:

	def __init__(self):
		self.generator = generate_level.Generator()
		self.unblocker = unblock.Unblocker()

	#generates and stores num levels, by default these are the number of solvable levels to generate
	#if !solvable then this will log both solvable
	def generate_levels(self, num, solvable = True):

		for i in range(num):
			while(True):
				grid_data = self.generator.generate_level()
				grid = grid_data["grid"]
				#this line represents a failure in so  many ways at a very high level. TBF I wrote the initial solver years before I decide to write the rest of this.
				#I could refactor this pretty easily, but I wont.
				#Don't smooth moves for clean data
				solution = self.unblocker.solve_board(board = grid, smooth = False)

				if len(solution) != 0 and solvable:
					print("Level " + str(i))
					for move in solution:
						print(move)
					break
				elif not solvable:
					break
	
	#saves a level to level_data.json
	def save_level(level_data, filename="levels/level_data.json"):
	    # Check if the JSON file already exists
	    if os.path.exists(filename):
	        # Load existing data from the file
	        with open(filename, "r") as file:
	            existing_data = json.load(file)
	    else:
	        # Create a new data structure if the file doesn't exist
	        existing_data = []

	    # Append the new level data to the existing data
	    existing_data.append(level_data)

	    # Write the updated data back to the JSON file
	    with open(filename, "w") as file:
	        json.dump(existing_data, file, indent=4)

lfactory = Level_Factory()

lfactory.generate_levels(100,True)