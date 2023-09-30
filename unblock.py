import copy
from threading import Lock
#empty board array

class Unblocker:

	def print_sol(self, sol):
		print(str(len(sol))+" moves")
		for move in sol:
			print(move)

	#Entry point into Unblocker
	#lots of default perameters due to the fact that this module is used all over the place in a lot of different ways
	#mutex to prevent parallel printing
	#grid to tap into grid UI and show solving live
	#smooth to slightly optimize moves by combining them for human readability
	#training to return [state,move] pairs for generating training data

	def solve_board(self, board, mutex = None, grid = None, smooth = True, training = False):
		#mutex
		if mutex == None:
			self.mutex = Lock()
		else:
			self.mutex = mutex
		#used to pass current state back and forth
		self.grid = grid
		#stores hashed already visited game states
		self.hashes = []
		#stores current states to be explored 
		self.queue = []
		#stores current moves
		self.moves = []

		#hash initial state and add it to list of already explored states
		hash_string = ""
		for row in board:
			for cell in row:
				hash_string += cell
		self.hashes.append(hash(hash_string))
		empty_move = []

		if training:
			return self.solve_shortest([board,empty_move])
		else:
			if smooth:
				return self.smooth_moves(self.solve_shortest([board, empty_move])[1])
			else:
				return self.solve_shortest([board,empty_move])[1]

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
		
	#breadth first search version for shortest solve
	def solve_shortest(self, b):
		#print("Solve Shortest")
		self.queue.append(b)
		i = 0
		while len(self.queue) != 0:
			i+=1
			curr = self.queue.pop(0)
			state = curr[0]
			#print("Checking State")
			self.print_state(state)
			#store both state and move in move list for training data
			#recall, this is the state and the move that **led** to that state, not the state and the best move from that state.
			move_m = copy.deepcopy(curr[1])
			move_s = copy.deepcopy(curr[0])
			move_list = [move_s, move_m]
			#check for win condition
			if state[2][5] == "R" and state[2][4] == "R":
				#print("After examining " + str(i) + " game states the game was solved in") 
				return move_list
			new_states = self.gen_states(state)
			for item in new_states:
				move_list.append([item[0],item[1]])
				temp_move = copy.deepcopy(move_list)
				#wow already doing this in the queue, not sure why I didn't do this in the move list to begin with
				self.queue.append([item[0], temp_move])
				move_list.pop()
		return []



	#returns m, the list of moves or path to win state using depth first search
	def solve(self, b, m, d):

		d += 1

		#check for win state
		if b[2][5] == "R" and b[2][4] == "R":
			#print("Game solved, returning moves")
			return m

		nexts = self.gen_states(b)
		for nextt in nexts:
			#print state
			#print("exploring state, depth: " + str(d))
			st = nextt[0]
			#print_state(st)
			m.append(nextt[1])
			solution = solve(st,m,d)
			if len(solution) != 0:
				return solution
			m.pop
		return []


	#gets the side of the block you're looking at
	# r = right, l = left, t = top, b = bottom, m = middle, n = not a block
	def get_gridside(self,r,c,b):

			curr = b[r][c]

			if curr.isupper():
				#horizontal
				if c == 0:
					return "l"
				if c == 5:
					return "r"	
				if curr == "A":
					if b[r][c-1] == "A":
						if c == 1:
							return "r"
						if b[r][c-2] == "A":
							if b[r][c+1] == "A":
								return "l"
						return "r"
					if b[r][c+1] == "A":
						if c ==	4:
							return "l"
						if b[r][c+2] == "A":
							if b[r][c-1] == "A":
								return "r"
						return "l"
				elif curr == "B":
					#never going to have two right next to each other
					if b[r][c-1] == "B":
						if b[r][c+1] == "B":
							return "m"
						return "r"
					return "l"
				elif curr == "R":
					if b[r][c-1] == "R":
						return "r"
					return "l"
			else:
				if r == 0:
					return "u"
				if r == 5:
					return "d"
				if curr == "a":
					if b[r-1][c] == "a":
						if r ==	1:
							return "d"
						if b[r-2][c] == "a":
							if b[r+1][c] == "a":
								return "u"
						return "d"
					if b[r+1][c] == "a":
						if r == 4:
							return "u"
						if b[r+2][c] == "a":
							if b[r-1][c] == "a":
								return "d"
						return "u"
				elif curr == "b":
					if b[r-1][c] == "b":
						if b[r+1][c] == "b":
							return "m"
						return "d"
					return "u"
			print("error non a valid side")
			return "n"

	#returns a list of possible next states and the corrisponding move like [state, move]
	#where state is a board array and move is a string
	# as a rule if it sees the top of a block try to move it up and if it sees the bottom try to move it down, same with left and right, just to simplify
	def gen_states(self, b):

		states = []

		i = 0
		for r in range(6):
			for c in range(6):
				i += 1
				#print("current board: " + str(i))
				#print_state(b)
				move = ""
				new_state = copy.deepcopy(b)
				curr = copy.deepcopy(b[r][c])
				#check if not empty
				if curr != ".":
					side = self.get_gridside(r,c,b)
					move = "(" + str(r) + "," + str(c) + ") -> ("
					if curr.isupper():
						#move right
						if side == "r" and c != 5 and b[r][c+1] == ".":
							move += str(r) + "," + str(c+1) + ")"
							new_state[r][c+1] = curr
							if curr == "B":
								new_state[r][c-2] = "."
							else:
								new_state[r][c-1] = "."
						#move left
						if side == "l" and c != 0 and b[r][c-1] == ".":
							move += str(r) + "," + str(c-1) + ")"
							new_state[r][c-1] = curr
							if curr == "B":
								new_state[r][c+2] = "."
							else:
								new_state[r][c+1] = "."
					else:
						#move down
						if side == "d" and r != 5 and b[r+1][c] == ".":
							move += str(r+1) + "," + str(c) + ")"
							new_state[r+1][c] = curr
							if curr == "b":
								new_state[r-2][c] = "."
							else:
								new_state[r-1][c] = '.'
						#move up
						if side == "u" and r != 0 and b[r-1][c] == ".":
							move += str(r-1) + "," + str(c) + ")"
							new_state[r-1][c] = curr
							if curr == "b":
								new_state[r+2][c] = "."
							else:
								new_state[r+1][c] = '.'
							
				#turn new state into a string to hash it
				hash_string = ""
				for row in new_state:
					for cell in row:
						hash_string += cell
				if not hash(hash_string) in self.hashes:
					#print("new state found")
					#print_state(new_state)
					self.hashes.append(hash(hash_string))
					state_arr = []
					state_arr.append(new_state)
					state_arr.append(move)
					states.append(state_arr) 
		return states
	#return solve(board, moves, 0)

	#01234567890123	
	#(1,0) -> (2,0)
	#turns multistep moves of the same tile into a smooth move to cut down move list length
	def smooth_moves(self, m):
		i = 0
		while i < len(m):
			if i != 0:
				if m[i][1:4] == m[i-1][10:13]:
					new_move = m[i-1][0:10] + m[i][10:14]
					m.pop(i)
					i = i-1
					m[i] = new_move
			i += 1 
		return m



#sol = solve_board(board)
#print(str(len(sol))+" moves")
#for move in sol:
#	print(move)