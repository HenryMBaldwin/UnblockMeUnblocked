import copy
#empty board array


#going to use a depth first search because it makes recording the path much easier, though a breadth first search would definitely be more effecient 
def solve_board(board):
	#stores hashed already visited game states
	hashes = []
	#stores current states to be explored 
	queue = []
	#stores current moves
	moves = []

	#hash initial state and add it to list of already explored states
	hash_string = ""
	for row in board:
		for cell in row:
			hash_string += cell
	hashes.append(hash(hash_string))

	def print_state(state):
		#prints a game state for debugging purposes		
		for row in state:
				line = "[ "
				for cell in row:
					line += cell + " "
				line += "]"
				print(line) 
		print("---------------")

	#breadth first search version for shortest solve
	def solve_shortest(b):
		nonlocal queue
		queue.append(b)
		i = 0
		while len(queue) != 0:
			i+=1
			curr = queue.pop(0)
			state = curr[0]
			#print("Checking State")
			print_state(state)
			move_list = copy.deepcopy(curr[1])
			if state[2][5] == "R" and state[2][4] == "R":
				print("After examining " + str(i) + " game states the game was solved in") 
				return move_list
			new_states = gen_states(state)
			for item in new_states:
				move_list.append(item[1])
				temp_move = copy.deepcopy(move_list)
				queue.append([item[0], temp_move])
				move_list.pop()
		return []



	#returns m, the list of moves or path to win state using depth search
	def solve(b, m, d):

		d += 1

		#check for win state
		if b[2][5] == "R" and b[2][4] == "R":
			#print("Game solved, returning moves")
			return m

		nexts = gen_states(b)
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

	#returns a list of possible next states and the corrisponding move like [state, move]
	#where state is a board array and move is a string
	# as a rule if it sees the top of a block try to move it up and if it sees the bottom try to move it down, same with left and right, just to simplify
	def gen_states(b):
		nonlocal hashes

		#gets the side of the block you're looking at
		# r = right, l = left, t = top, b = bottom, m = middle, n = not a block
		def get_gridside(r,c):
			nonlocal b

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
					side = get_gridside(r,c)
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
				if not hash(hash_string) in hashes:
					#print("new state found")
					#print_state(new_state)
					hashes.append(hash(hash_string))
					state_arr = []
					state_arr.append(new_state)
					state_arr.append(move)
					states.append(state_arr) 
		return states
	#return solve(board, moves, 0)

	#01234567890123	
	#(1,0) -> (2,0)
	#turns multistep moves of the same tile into a smooth move to cut down move list length
	def smooth_moves(m):
		i = 0
		while i < len(m):
			if i != 0:
				if m[i][1:4] == m[i-1][10:13]:
					new_move = m[i-1][0:10] + m[i][10:14]
					m.pop(i)
					i = i-1
					m[i] = new_movex
			i += 1 
		return m


	empty_move = []
	return smooth_moves(solve_shortest([board, empty_move]))						


board = [["A", "A", "A", "A","a","b"],
		 ["A", "A", "A", "A","a","b"],
		 ["R", "R", ".", ".",".","b"],
		 ["a", ".", ".", "a","A","A"],
		 ["a", "A", "A", "a","A","A"],
		 [".", ".", "A", "A","A","A"]]

empty = [[".", ".", ".", ".",".","."],
		 [".", ".", ".", ".",".","."],
		 [".", ".", ".", ".",".","."],
		 [".", ".", ".", ".",".","."],
		 [".", ".", ".", ".",".","."],
		 [".", ".", ".", ".",".","."]]

sol = solve_board(board)
print(str(len(sol))+" moves")
for move in sol:
	print(move)