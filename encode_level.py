import pygame
import math

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

#function to handle grid snapping
def snap(block,pos):
	x = pos[0]
	y = pos[1]

	if block.vertical:
		ret = (x-50,y-25)
	else:
		ret = (x-25,y-50)
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
				ret = (point[0]-50,point[1]-50)
	#set grid position
	block.set_grid_pos(ret[0]%100,ret[1]%100)
	return ret

#Block class to allow for easier collision detection
class Block:

	def __init__(self, x, y, block_type, manager):
		self.x = x
		self.y = y
		self.width = BLOCK_SIZE * block_type[0][0]
		self.height = BLOCK_SIZE * block_type[0][1]
		self.block_type = block_type
		self.rect = pygame.draw.rect(window, self.block_type[1], (x, y, self.width, self.height))

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
                #TODO: check for clicking on a currently existing block to delete
                # place down currently selected block on grid
                if not selected_block == None:
                	#check if on grid
                		if selected_block.grid_x != None:
                				#deselect block
                				selected_block = None


        elif event.type == pygame.KEYDOWN:
         	if event.key == pygame.K_r:
         		if not selected_block == None:
         			selected_block.rotate()

    #handle snapping
    if selected_block is not None:
            	new_pos = snap(selected_block, pygame.mouse.get_pos())
            	#if block is red then lock it to row 3
            	selected_block.set_pos(new_pos[0],new_pos[1])
    # Clear the window
    window.fill(WHITE)

    # Draw the block selection area
    pygame.draw.rect(window, GRAY, (WINDOW_HEIGHT, 0, SELECTION_WIDTH, SELECTION_HEIGHT))

    # Draw the block buttons in the selection area
    button_manager.draw()

    # Draw the other blocks
    block_manager.draw()

    # Draw the grid
    for x in range(0, WINDOW_HEIGHT, BLOCK_SIZE):
        pygame.draw.line(window, GRAY, (0, x), (WINDOW_HEIGHT, x))
        pygame.draw.line(window, GRAY, (x, 0), (x, WINDOW_HEIGHT))

    # Update the display
    pygame.display.update()
    clock.tick(60)

# Quit the game
pygame.quit()
