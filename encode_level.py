import pygame

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
		if block_type[2] == "RED":
			return
		self.vertical = not self.vertical
		temp = self.width
		self.width = self.height
		self.height = temp


	def set_grid_pos(self, x, y):
		self.grid_x = x
		self.grid.y = y
		#set block top position to align to grid
		self.set_pos(100*grid_x, 100*grid_y)

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
                #TODO: check for placing down currently selected block on grid

        elif event.type == pygame.MOUSEMOTION:
            # Update the position of the selected block based on mouse movement
            if selected_block is not None:
            	#if block is red then lock it to row 3
            	if selected_block.block_type[2] == "RED":
            		selected_block.set_pos(event.pos[0] - 25,200)
            	else:
                	selected_block.set_pos(event.pos[0] - 25,event.pos[1] -50)

        elif event.type == pygame.KEYDOWN:
         	if event.key == pygame.K_r:
         		if not selected_block == None:
         			selected_block.rotate()

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
