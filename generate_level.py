
import random

#random level generator - not garunteed solvable
#also generates metadata on each level in json to later tune the generator to more reliably produce solvable levels
#based purely on encoded form of the grid
class Generator:

	def __init__(self):
		#empty grid
		self.grid = [[".", ".", ".", ".",".","."],
		 [".", ".", ".", ".",".","."],
		 [".", ".", ".", ".",".","."],
		 [".", ".", ".", ".",".","."],
		 [".", ".", ".", ".",".","."],
		 [".", ".", ".", ".",".","."]]

		self.grid_data = {
			"grid":[],
			"num_blocks":0,
			"red_block_col":-1,
			"vert_short":0,
			"vert_long":0,
			"hori_short":0,
			"hori_long":0,
			"moves_to_solve":0,
			"solvable":False,
			"solution":[]
		}

		self.block_info = {
			"R":"red",
			"A":"hori_short",
			"a":"vert_short",
			"B":"hori_long",
			"b":"vert_long"
		}


	def reset(self):

		self.grid = [[".", ".", ".", ".",".","."],
		 [".", ".", ".", ".",".","."],
		 [".", ".", ".", ".",".","."],
		 [".", ".", ".", ".",".","."],
		 [".", ".", ".", ".",".","."],
		 [".", ".", ".", ".",".","."]]

		self.grid_data = {
			"grid":[],
			"num_blocks":0,
			"red_block_col":-1,
			"vert_short":0,
			"vert_long":0,
			"hori_short":0,
			"hori_long":0,
			"moves_to_solve":0,
			"solvable":False,
			"solution":[]
		}

		
	#handles block placement - returns true if block is placed successfully
	#some block placing rules for better solvability:
	# - no horizontal blocks on row 2
	def place_block(self,block, r, c):

		#print("Attempting to place "  + self.block_info[block] + " at ("+str(r)+","+str(c)+")") 
		grid = self.grid
		ret = False
		if r < 0 or c < 0 or r > 5 or c >5:
			return False


		match block:
			case "R":
				if not (r != 2 or c > 3):
					grid[r][c] = block
					grid[r][c+1] =  block
					ret = True
				#move straight to "A" code to avoid repition 
			case "A":
				if not (c == 5 or r == 2 or grid[r][c] != "." or grid[r][c+1] != "."):
					grid[r][c] = block
					grid[r][c+1] =  block
					ret = True
				
			case "a":
				if not (r == 5 or grid[r][c] != "." or grid[r+1][c] != "."):
					grid[r][c] = block
					grid[r+1][c] =  block
					ret = True
			case "B":
				if not (c > 3 or r == 2 or grid[r][c] != "." or grid[r][c+1] != "." or grid[r][c+2] != "."):
					grid[r][c] = block
					grid[r][c+1] =  block
					grid[r][c+2] =  block
					ret = True
			case "b":
				if not (r > 3 or grid[r][c] != "." or grid[r+1][c] != "." or grid[r+2][c] != "." ):
					grid[r][c] = block
					grid[r+1][c] =  block
					grid[r+2][c] =  block
					ret = True
		self.grid = grid
		return ret

	def print_state(self):
		#prints a game state for debugging purposes		
		for row in grid:
				line = "[ "
				for cell in row:
					line += cell + " "
				line += "]"

	#generates random level
	def generate_level(self):

		#reset
		self.reset()

		#place red block

		red_block_col = random.randint(0,3)
		self.place_block("R", 2, red_block_col)

		self.grid_data["red_block_col"] = red_block_col
		#choose number of brown blocks between 4 and 13
		#this number range is largely arbitrary based on a cursory examination of a few unblock me levels
		num_blocks = random.randint(4,13)

		for i in range(0, num_blocks+1):
			#pick block, currently weighted 50/50 short/long and vertical/horizantal, meaning a quarter chance for every block type
			#these may be altered in the future to more consistantly produce solvable levels based on statistics harvested from generated levels
			block_type_int = random.randint(0,3)

			block = ""
			match block_type_int:
				case 0:
					block = "A"
					
				case 1:
					block = "a"
					
				case 2:
					block = "B"
					
				case 3: 
					block = "b"
					

			#try to place block at random coordinates 1000 times, if block cannot be placed, move on
			#this is a very inefficient way to do this, oh well, if its significantly delaying the program I'll change it I guess
			for i in range(1000):
				#pick coordinates
				r = random.randint(0,5)
				c = random.randint(0,5)

				if self.place_block(block, r, c):
					#if block was succesfully placed add it to meta data
					self.grid_data["num_blocks"] += 1
					self.grid_data[self.block_info[block]] += 1
					break

		#add grid to metadata

		self.grid_data["grid"] = self.grid

		return self.grid_data
