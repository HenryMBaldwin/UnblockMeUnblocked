import pygame
import math
import copy
import unblock
import generate_level
from pygame.locals import *
from threading import Thread, Lock
import json
import inter
#Mutex
mutex = Lock()

# Initialize Pygame
pygame.init()

# Define colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GRAY = (128, 128, 128)
BROWN = (235, 177, 52)

# Set window dimensions
WINDOW_WIDTH = 1100
WINDOW_HEIGHT = 600
GRID_SIZE = 6
BLOCK_SIZE = WINDOW_HEIGHT // GRID_SIZE


#Define block types
BLOCK_TYPES = {
	"RED":[(2, 1), RED, "RED"], 
	"BROWN":[(2, 1), BROWN, "BROWN"],  # 2 long block
	"LONG_BROWN":[(3, 1), BROWN, "LONG_BROWN"]  # 3 long block
	  # 2 long red block
}
#center of each grid square for snapping and placement
GRID_POSITIONS = [
	(50,50), (150,50), (250,50),(350,50),(450,50),(550,50),
	(50,150), (150,150), (250,150),(350,150),(450,150),(550,150),
	(50,250), (150,250), (250,250),(350,250),(450,250),(550,250),
	(50,350), (150,350), (250,350),(350,350),(450,350),(550,350),
	(50,450), (150,450), (250,450),(350,450),(450,450),(550,450),
	(50,550), (150,550), (250,550),(350,550),(450,550),(550,550),
	]



#Class keeps track of grid
class Grid:
	def __init__(self,manager, button_manager, mutex):
		#empty grid
		self.grid = [[".", ".", ".", ".",".","."],
		 [".", ".", ".", ".",".","."],
		 [".", ".", ".", ".",".","."],
		 [".", ".", ".", ".",".","."],
		 [".", ".", ".", ".",".","."],
		 [".", ".", ".", ".",".","."]]
		
		#other classes
		self.generator = generate_level.Generator()
		self.unblocker = unblock.Unblocker()
		self.ml_unblocker = inter.ML_Unblocker(self)

		self.solver = "ML"
		
		self.manager = manager
		self.button_manager = button_manager
		self.mutex = mutex
		#keeps track of whether red block is placed
		self.red = False
		self.solving = False
		self.sol = None

		self.debug = False

	def solve(self):
		#print("solve")
		if self.solver == "DFS":
			self.sol = Thread(target = self.unblocker.solve_board, args = (self.grid, self.mutex, self))
			self.solving = True
			self.sol.start()
		if self.solver == "ML":
			print("Solving with ML.")
			#self.sol = Thread(target = self.ml_unblocker.solve_state)
			self.sol = Thread(target = self.ml_unblocker.solve_state, args = (self.grid,))
			self.solving = True
			self.sol.start()
			
		#print(str(len(sol))+" moves")
		#for move in sol:
		#	print(move)

	def check_solve(self):
		#print("Checking solver")
		if not self.sol.is_alive():
			self.solving = False

	#checks if red block is present
	def check_red(self):
		for y in self.grid:
			for x in y:
				if x == "R":
					self.red = True

	#decodes grid and places it on gameboard
	def decode(self):
		#self.print_state()
		#self.mutex.acquire()
		#print("decoding")
		encodings = {
		"R":"RED",
		"A":"BROWN",
		"B":"LONG_BROWN"}

		#need button manager for block
		buttons = self.button_manager
		#clear visual grid
		self.remove_all_visual()

		#print("in decode")
		#self.print_state()
		for y in range(len(self.grid)):
			for x in range(len(self.grid[y])):
				curr = self.get_grid_pos(x,y)
				if curr != ".":
					#current block
					selected_block = None

					#get side from unblocker
					side = self.unblocker.get_gridside(y,x,self.grid)
					#print(side)
					#print("test side: " + self.unblocker.get_gridside(5,3,self.grid))
					#only place blocks from top or left
					if side == "u" or side == "l":
						#print("placing block at (" +str(x) + "," +str(y) +")")
						coords = self.reverse_resolve(x,y)
						#print(str(coords))
						for block in buttons.block_arr:
							if block.block_type[2] == encodings[curr.upper()]:
								selected_block = block.clone(self.manager)


						if not curr.isupper():
							selected_block.rotate()
						selected_block.set_pos(coords[0],coords[1])
						selected_block.set_grid_pos(x,y)
						self.place(selected_block, (x,y))
						#print("placed")

		#self.mutex.release()


	#sets internal grid
	#dangerous: desyncs visual grid from internal
	def set_grid(self,grid):
		self.grid = grid
		
	#Updates a grid position
	#This function exists because the urge to reference grid like grid[grid_x][grid_y] is too powerful and I keep making mistakes because of it
	def update_grid_pos(self, x, y, val):
		if 0 > x or 5 < y:
			print("Invalid value for x: "+ str(x))
		if 0 > y or 5 < y:
			print("Invalid value for y: "+ str(y))
		#print(str(x) + "," + str(y))
		self.grid[y][x] = val
		
		

	#Same reason as above but getter
	def get_grid_pos(self, x, y):
		return self.grid[y][x]	

	def print_state(self):
		#prints a game state for debugging purposes		
		for row in self.grid:
				line = "[ "
				for cell in row:
					line += cell + " "
				line += "]"
				print(line) 
		print("---------------")

	#resolves grid position [0][0] to [5][5] from coordinate
	def resolve_pos(self,x,y):
		if x >= 600 or x < 0 or y >= 600 or y < 0:
			return None
		return (int(x/100),int(y/100))


	#resolves real coords from grid coords
	def reverse_resolve(self, x, y):
		return(x*100, y*100)

	#checks if closest position is free for specific block	 
	def check_pos(self, block, pos):
		x = pos[0]
		y = pos[1]

		grid_pos = self.resolve_pos(x,y)

		if grid_pos == None:
			return False

		grid_x = grid_pos[0]
		grid_y = grid_pos[1]

		for i in range(3 if block.block_type[2] == "LONG_BROWN" else 2):
			#print(i)
			if (i + (grid_y if block.vertical else grid_x))> 5:
				return False
			if block.vertical:
				if self.get_grid_pos(grid_x, grid_y+i) != ".":
					return False
			else:
				if self.get_grid_pos(grid_x + i, grid_y) != ".":
					return False
		return True
		
	#function to handle grid snapping
	def snap(self, block,pos):
		x = pos[0]
		y = pos[1]

		if block.vertical:
			ret = (x-50,y-25)
			new_pos = (x-50,y-25)
		else:
			ret = (x-25,y-50)
			new_pos = (x-25,y-50)

		#dont snap if mouse isnt over grid
		if x >= 600:
			#set grid positions to none
			block.set_grid_pos(None,None)
			return ret
		min_dist = 600
		#calculate closest point
		for point in GRID_POSITIONS:
			#pythag
			distance = math.sqrt((abs(x - point[0])**2) + (abs(y-point[1])**2))
			if distance < min_dist:
				#check for red block
				if block.block_type[2] != "RED" or point[1] == 250:
					min_dist = distance
					new_pos = (point[0]-50,point[1]-50)
		#set grid position
		if self.check_pos(block,new_pos):
			ret = new_pos
			grid_pos = self.resolve_pos(new_pos[0],new_pos[1])
			block.set_grid_pos(grid_pos[0], grid_pos[1])
		else:
			block.set_grid_pos(None,None)
			
		block.set_pos(ret[0],ret[1])

	def place(self,block,grid_pos):

		grid_x = grid_pos[0]
		grid_y = grid_pos[1]

		if block.block_type[2] == "LONG_BROWN":
			code_char = "B"
		elif block.block_type[2] == "BROWN":
			code_char = "A"
		else:
			code_char = "R"

		if block.vertical:
			code_char = code_char.lower()

		#print(code_char)
		for i in range(3 if block.block_type[2] == "LONG_BROWN" else 2):
			#print(str(i))
			if block.vertical:
				self.update_grid_pos(grid_x, grid_y+i, code_char) 
			else:
				self.update_grid_pos(grid_x+i, grid_y, code_char) 

		self.check_red()

	def remove(self,block):
		grid_x = block.grid_x
		grid_y = block.grid_y

		for i in range(3 if block.block_type[2] == "LONG_BROWN" else 2):
			if block.vertical:
				self.update_grid_pos(grid_x, grid_y + i, ".")
			else:
				self.update_grid_pos(grid_x + i, grid_y, ".")

		block.manager.remove(block)

		self.check_red()

	#cleans board both in visual and internal grid
	def remove_all(self):
		for i in reversed(range(len(self.manager.block_arr))):
			self.remove(self.manager.block_arr[i])
		

	#remove all block objects but does not clean board.
	#Dangerous, desyncs board from internal grid
	def remove_all_visual(self):
		for i in reversed(range(len(self.manager.block_arr))):
			self.manager.block_arr[i].remove()

	def save_to_json(self):
		with open("grid.json", 'w') as json_file:
			json.dump(self.grid, json_file)		

	def load_from_json(self):
		with open("grid.json", 'r') as json_file:
			temp = json.load(json_file)
			if temp != None:
				self.grid = temp
				self.decode()

	def generate_level(self):
		level = self.generator.generate_level()
		self.grid = level["grid"]
		#print("decoding grid")
		#self.print_state()
		self.decode()

	def set_solver(self, option):
		self.solver = option

	def set_debug(self):
		self.debug = not self.debug


#Block class to allow for easier collision detection
class Block:

	def __init__(self, x, y, block_type, manager):
		self.x = x
		self.y = y
		self.width = BLOCK_SIZE * block_type[0][0]
		self.height = BLOCK_SIZE * block_type[0][1]
		self.block_type = block_type
		self.rect = pygame.draw.rect(window, self.block_type[1], (x, y, self.width, self.height), 10, 10)

		#grid position
		self.grid_x = None
		self.grid_y = None
		self.vertical = False

		#block manager
		self.manager = manager
		self.manager.add(self)

	def rotate(self):
		#Don't rotate if block is red
		if self.block_type[2] == "RED":
			return
		self.vertical = not self.vertical
		temp = self.width
		self.width = self.height
		self.height = temp



	def set_grid_pos(self, x, y):
		self.grid_x = x
		self.grid_y = y

	def set_pos(self,x,y): 
		self.x = x
		self.y = y
			
	def draw(self):
		self.rect = pygame.draw.rect(window, self.block_type[1], (self.x, self.y, self.width, self.height))
		#draw border
		for i in range(4):
			pygame.draw.rect(window, (0, 0, 0), (self.x,self.y,self.width,self.height), 1)

	def remove(self):
		self.manager.remove(self)

	#used for duplicating a block from the block buttons
	def clone(self, manager):
		return Block(self.x, self.y, self.block_type, manager)

	
	#for custom buttons
	#def write(self, manager)

#Keep track of blocks to draw them every frame
class Block_Manager:
	def __init__(self):
		#internal array
		self.block_arr = []

	def draw(self):
		for block in self.block_arr:
			block.draw()

	def add(self, block):
		self.block_arr.append(block)
		#print(len(self.block_arr))

	def remove(self, block):
		self.block_arr.remove(block)
		del block

	def remove_all(self):
		for block in self.block_arr:
			self.remove(block)

	#function to check all blocks for clicks
	def detect_click(self, mouse_pos):
		for block in self.block_arr:
			if block.rect.collidepoint(mouse_pos):
				return block
		return None

class Menu_Manager(Block_Manager):
	def detect_click(self, mouse_pos):
		for block in self.block_arr:
			if block.rect.collidepoint(mouse_pos):
				block.click()
	
class Menu_Button:
	def __init__(self,x,y, text, text_x, manager, func, args = None):
		self.x = x
		self.y = y

		self.manager = manager
		self.manager.add(self)

		self.text_v = text
		self.func = func
		self.args = args
		self.width = 60
		self.height = 20
		self.primary_color = (255, 255, 255)
		self.press_color = (174, 180, 245)
		self.font_color = (0,0,0)
		self.font = pygame.font.SysFont('Corbel',22)
		self.text = self.font.render(text, True, self.font_color)
		self.text_box = self.text.get_rect()
		self.rect = pygame.draw.rect(window, self.primary_color, (self.x, self.y, self.width, self.height))

	def draw(self):
		self.rect = pygame.draw.rect(window, self.primary_color, (self.x, self.y, self.width, self.height))
		window.blit(self.text, (self.x+((self.width - self.text_box.width)/2), self.y))
		#draw border
		for i in range(4):
			pygame.draw.rect(window, (0, 0, 0), (self.x,self.y,self.width,self.height), 1)

	def click(self, args = None):
		if self.args != None:
			self.func(self.args)
		else:
			self.func()

#Main button for drop down menu
class DropDown_Menu(Menu_Button):

	def __init__(self, x, y, options, text_x, manager, func):
		assert options, "Options list should not be empty"
		super().__init__(x, y, options[0], text_x, manager, func)
		
		self.options = options  # List of options to be displayed in the dropdown
		self.active_option = options[0]  # Currently selected option
		self.expanded = False  # Flag to check if the dropdown is expanded
		self.option_height = self.height  # Height of each option in the dropdown
		self.dropdown_buttons = []  # List to store dynamically created dropdown buttons

	def expand(self):
		# Dynamically create dropdown buttons and register them with the menu manager
		for i, option in enumerate(self.options):
			btn = DropDown_Menu_Button(self.x, self.y + (i+1)*self.option_height, option, 10, self.manager, self.func, self)
			self.dropdown_buttons.append(btn)
		self.expanded = True

	def collapse(self):
		# Unregister and delete the dynamically created dropdown buttons
		for btn in self.dropdown_buttons:
			btn.manager.remove(btn)
			del btn
		self.dropdown_buttons.clear()
		self.expanded = False

	def select_option(self, option):
		# Handle option selection here
		self.text = self.font.render(option, True, self.font_color)
		self.collapse()
		self.func(option) 

	def click(self, args=None):
		if self.expanded:
			# If the dropdown is expanded, delegate the click handling to the parent
			# This will detect clicks on the dynamically created dropdown buttons
			self.collapse()
		else:
			# If the dropdown is not expanded, expand it
			self.expand()

#sub buttons for dropdown menu
class DropDown_Menu_Button(Menu_Button):

	def __init__(self, x, y, option, text_x, manager, func, dropdown_menu):
		super().__init__(x,y, option, text_x, manager, func)
		self.option = option
		self.dropdown = dropdown_menu

	def click(self):
		self.dropdown.select_option(self.option)






#Create Block Manager
block_manager = Block_Manager()

#Create Button Manager
button_manager = Block_Manager()

#Create Grid encoding
grid = Grid(block_manager,button_manager, mutex)

# Set selection area dimensions
SELECTION_WIDTH = WINDOW_WIDTH - WINDOW_HEIGHT
SELECTION_HEIGHT = WINDOW_HEIGHT

# Create the window
window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Unblock Me Unblocked Level Input")

clock = pygame.time.Clock()

#
# Init Buttons
#



#Add buttons
Block(700, 50, BLOCK_TYPES["RED"], button_manager)
Block(700, 250, BLOCK_TYPES["BROWN"], button_manager)
Block(700, 450, BLOCK_TYPES["LONG_BROWN"], button_manager)
#Block()

#
# Menu Manager
#

#Create Menu Manager
menu_manager = Menu_Manager()

#menu buttons
menu_button_x = WINDOW_WIDTH - 80
menu_button_y = 50

#solve button
Menu_Button(menu_button_x,menu_button_y, "Solve", 10, menu_manager, grid.solve)
menu_button_y = menu_button_y+25
Menu_Button(menu_button_x, menu_button_y, "Clear",10,menu_manager, grid.remove_all)
menu_button_y = menu_button_y+25
Menu_Button(menu_button_x, menu_button_y, "Save",10,menu_manager, grid.save_to_json)
menu_button_y = menu_button_y+25
Menu_Button(menu_button_x, menu_button_y, "Load",10,menu_manager, grid.load_from_json)
menu_button_y = menu_button_y+25
Menu_Button(menu_button_x, menu_button_y, "Rand",10, menu_manager, grid.generate_level)
menu_button_y = menu_button_y+25
Menu_Button(menu_button_x, menu_button_y, "Print",10, menu_manager, grid.print_state)
menu_button_y = menu_button_y+25
Menu_Button(menu_button_x, menu_button_y, "Debug",10, menu_manager, grid.set_debug)

#dropdown menu
options = ["ML", "DFS", "BFS "]
menu_button_y = menu_button_y+25
DropDown_Menu(menu_button_x, menu_button_y, options, 10, menu_manager, grid.set_solver)
#toggle buttons
# Track the currently selected block
selected_block = None



# Main game loop
running = True
while running:
	mutex.acquire()
	if grid.solving:
		grid.decode()
		grid.check_solve()
   
	#grid.print_state()
	# Process events
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			running = False
		elif event.type == pygame.MOUSEBUTTONDOWN:
			# Check if the left mouse button is pressed
			if event.button == 1:
				#check if a button has been clicked
				button = button_manager.detect_click(pygame.mouse.get_pos())
				#check if block has been clicked
				block = block_manager.detect_click(pygame.mouse.get_pos())
				#check if menubutton has been clicked. If so its function will instantly be called
				menu_manager.detect_click(pygame.mouse.get_pos())
				if not button == None:
					#delete previous selected block
					if not selected_block == None:
						selected_block.remove()
					#clone clicked button and add it to block_manager
					selected_block = button.clone(block_manager)
			   
				# place down currently selected block on grid
				if not selected_block == None:
					#check if on grid
						if selected_block.grid_x != None:
								#deselect block
								grid.place(selected_block,(selected_block.grid_x,selected_block.grid_y))
								selected_block = None
								
				#delete currently placed block
				elif not block == None:
					grid.remove(block)

		elif event.type == pygame.KEYDOWN:#rotate block
			if event.key == pygame.K_r:
				if not selected_block == None:
					selected_block.rotate()
			 #put away selected block
			if event.key == pygame.K_ESCAPE:
				if not selected_block == None:
					selected_block.remove()
					selected_block = None

	#handle snapping
	if selected_block is not None:
				grid.snap(selected_block, pygame.mouse.get_pos())
	mutex.release()
	# Clear the window
	window.fill(WHITE)

	#print grid
	#grid.print_state()
	# Draw the grid
	for x in range(0, WINDOW_HEIGHT, BLOCK_SIZE):
		pygame.draw.line(window, GRAY, (0, x), (WINDOW_HEIGHT, x))
		pygame.draw.line(window, GRAY, (x, 0), (x, WINDOW_HEIGHT))
		

	# Draw the block selection area
	pygame.draw.rect(window, GRAY, (WINDOW_HEIGHT, 0, SELECTION_WIDTH, SELECTION_HEIGHT))

	# Draw the block buttons in the selection area
	button_manager.draw()

	# Draw the other blocks
	block_manager.draw()

	#draw debug numbers
	for x in range(0, WINDOW_HEIGHT, BLOCK_SIZE):
		if grid.debug:
			# Draw number pairs in each box
			number_font = pygame.font.Font(None, 30)
			for i in range(0, WINDOW_HEIGHT, BLOCK_SIZE):
				for j in range(0, WINDOW_HEIGHT, BLOCK_SIZE):
					number_text = number_font.render(f"({i // BLOCK_SIZE},{j // BLOCK_SIZE})", True, (128, 128, 128, 128))
					window.blit(number_text, (i + 5, j + 5))
	#draw Menu Buttons
	menu_manager.draw()

	# Update the display
	pygame.display.update()
	clock.tick(60)
	#clock.tick(60)

# Quit the game
pygame.quit()
