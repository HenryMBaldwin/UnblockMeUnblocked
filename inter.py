from tensorflow.keras.models import load_model
import numpy as np
import data_factory
import unblock
# Load the model

class ML_Unblocker:

	def __init__(self, grid):
		self.model = load_model('models/unblock_me_solver')
		#need some functions from here
		self.data_f = data_factory.Level_Factory() 
		self.unblocker = unblock.Unblocker()
		self.moves = []
		self.grid = grid

	def solve_state(self, state):

		processed_state = self.data_factory.convert_to_one_hot(state)

		# Ensure that this new_state should be preprocessed (normalized/encoded) in the same way as training data.
		new_state = np.array([processed_new_state])  #

		new_state = new_state.reshape(-1, 6, 6, 6) 

		# Use the model to predict the best move for the given state.
		predicted_move = model.predict(new_state)

		#print(type(predicted_move))

		
		new_state, move = decode_move(predicted_move)  
		
		moves.append(move)

		if state[2][5] == "R" and state[2][4] == "R":
			#print("After examining " + str(i) + " game states the game was solved in") 
			return moves

		#visually update teh grid
		update_grid(new_state)
		

		#solve new state
		solve_state(new_state)

	def update_grid(self,state):
		if self.grid != None:
			self.grid.grid = state

	#takes in a move from the ml model and outputs a state
	def decode_move(self, move, state):

		new_state = None

		move = list(map(lambda x: int(x*5),move))

		r1,c1,r2,c2 = move
		gridside = self.unblocker.get_gridside(r1,c1,state)

		block = state[r1][c1]
		direction = ""
		#get move direction and check for move validity based on coordinates
		#using t for top/up and b for bottom/down to be consistant with gridside
		if r1 != r2 and c1 != c2:
			self.move_error("Can't move diagonally.", move)
		if abs(r1-r2) > 1 or abs(c1-c2) > 1:
			self.move_error("Can't move more than one position at a time.", move)
		if r1 > r2:
			direction = "t"
		elif r2 > r1:
			direction = "b"
		elif c1 > c2:
			direction = "l"
		elif c2 > c1:
			direction = "r"
		else:
			self.move_error("No move was made.", move)

		#check for move validity based on gridside of starting coordinate and begin state genera
		if gridside == "m":
			self.move_error("Can't perform move on middle of block.", move)
		if gridside == "n":
			self.move_error("Can't perform a move on an empty space.", move)
		if gridside == direction:
			#check move validy based on location
			match r1,c1, direction:
				case 5, _, "d":
					self.move_error("Cannot move downwards from row 5.", move)
				case 0, _, "u":
					self.move_error("Cannot move upward from row 0.", move)
				case _, 0, "l":
					self.move_error("Cannot move leftwards from col 0.", move)
				case _, 5, "r":
					self.move_error("Cannot move rightwards from col 5.", move)
				case _,_,_:
					new_state = self.state_from_move(gridside, block, state, r1, c1)
		else:
			self.move_error("Cant perform a move " + str(direction) + " on side " + str(gridside) + ".", move)

		return [new_state, pretty_print_move(move)]

	def state_from_move(self, side, block, state, r, c):
		#repurposed code from unblock.py
		new_state = state
		if block.isupper():
			#move right
			if side == "r" and c != 5 and b[r][c+1] == ".":
				new_state[r][c+1] = block
				if block == "B":
					new_state[r][c-2] = "."
				else:
					new_state[r][c-1] = "."
			#move left
			if side == "l" and c != 0 and b[r][c-1] == ".":
				new_state[r][c-1] = block
				if block == "B":
					new_state[r][c+2] = "."
				else:
					new_state[r][c+1] = "."
		else:
			#move down
			if side == "d" and r != 5 and b[r+1][c] == ".":
				new_state[r+1][c] = block
				if block == "b":
					new_state[r-2][c] = "."
				else:
					new_state[r-1][c] = '.'
			#move up
			if side == "u" and r != 0 and b[r-1][c] == ".":
				new_state[r-1][c] = block
				if block == "b":
					new_state[r+2][c] = "."
				else:
					new_state[r+1][c] = '.'
		return new_state

		

	def move_error(self, details, move):
		print("Error Invalid Move: " + details + "\n" + self.pretty_print_move(move))
		quit()

	def pretty_print_move(self,move):
		#pretty prints a move array 
		r1,c1,r2,c2 = move
		return "(" + str(r1) + "," +str(c1) + ") -> " + "(" + str(r2) + "," + str(c2) +")"

	def print_state(self,state):
		self.mutex.acquire()
		if self.grid != None:
			self.grid.grid = state
		
		#prints a game state for debugging purposes		
		for row in state:
				line = "[ "
				for cell in row:
					line += cell + " "
				line += "]"
		#		print(line) 
		#print("---------------")
		self.mutex.release()

#function to run solver on its own, without the GUI and threading nonsense. 







