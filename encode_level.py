import pygame
import math
import copy
import unblock
from pygame.locals import *

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
	def __init__(self):
		#empty grid
		self.grid = [[".", ".", ".", ".",".","."],
		 [".", ".", ".", ".",".","."],
		 [".", ".", ".", ".",".","."],
		 [".", ".", ".", ".",".","."],
		 [".", ".", ".", ".",".","."],
		 [".", ".", ".", ".",".","."]]
		
		self.unblocker = unblock.Unblocker()


	#Updates a grid position
	#This function exists because the urge to reference grid like grid[grid_x][grid_y] is too powerful and I keep making mistakes because of it
	def update_grid_pos(self, x, y, val):
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

		for i in range(3 if block.block_type == ["LONG_BROWN"] else 2):
			
			if block.vertical:
				self.update_grid_pos(grid_x, grid_y+i, code_char) 
			else:
				self.update_grid_pos(grid_x+i, grid_y, code_char) 

	def remove(self,block):
		grid_x = block.grid_x
		grid_y = block.grid_y

		for i in range(3 if block.block_type == ["LONG_BROWN"] else 2):
			if block.vertical:
				self.update_grid_pos(grid_x, grid_y + i, ".")
			else:
				self.update_grid_pos(grid_x + i, grid_y, ".")

		block.manager.remove(block)

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

	def remove(self):
		self.manager.remove(self)

	#used for duplicating a block from the block buttons
	def clone(self, manager):
		return Block(self.x, self.y, self.block_type, manager)

	#for custom buttons
	def write(self, manager)
	

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

#Create Grid encoding
grid = Grid()

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

#Create Button Manager
button_manager = Block_Manager()

#Add buttons
Block(700, 50, BLOCK_TYPES["RED"], button_manager)
Block(700, 250, BLOCK_TYPES["BROWN"], button_manager)
Block(700, 450, BLOCK_TYPES["LONG_BROWN"], button_manager)
Block()

#
# Blocks
#

#Create Block Manager
block_manager = Block_Manager()

# Track the currently selected block
selected_block = None



# Main game loop
running = True
while running:
    # Process events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            # Check if the left mouse button is pressed
            if event.button == 1:
                #check if a button has been clicked
            	button = button_manager.detect_click(pygame.mouse.get_pos())
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
            	else:
            		block = block_manager.detect_click(pygame.mouse.get_pos())
            		if not block == None:
            			grid.remove(block)

        elif event.type == pygame.KEYDOWN:
        	#rotate block
         	if event.key == pygame.K_r:
         		if not selected_block == None:
         			selected_block.rotate()
         	#put away selected block
         	if event.key == pygame.K_ESCAPE:
         		if not selected_block == None:
         			block_manager.remove(selected_block)

    #handle snapping
    if selected_block is not None:
            	new_pos = grid.snap(selected_block, pygame.mouse.get_pos())
    # Clear the window
    window.fill(WHITE)

    # Draw the block selection area
    pygame.draw.rect(window, GRAY, (WINDOW_HEIGHT, 0, SELECTION_WIDTH, SELECTION_HEIGHT))

    # Draw the block buttons in the selection area
    button_manager.draw()

    # Draw the other blocks
    block_manager.draw()

    #print grid
    grid.print_state()
    # Draw the grid
    for x in range(0, WINDOW_HEIGHT, BLOCK_SIZE):
        pygame.draw.line(window, GRAY, (0, x), (WINDOW_HEIGHT, x))
        pygame.draw.line(window, GRAY, (x, 0), (x, WINDOW_HEIGHT))

    # Update the display
    pygame.display.update()
    clock.tick(60)

# Quit the game
pygame.quit()
