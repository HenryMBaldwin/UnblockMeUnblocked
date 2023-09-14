
import generate_level
import unblock

#Produces solvable levels with metadata including solution
class Level_Factory:

	def __init__(self):
		self.generator = generate_level.Generator
		self.unblocker = unblock.unblocker

	#generates and stores num levels, by default these are the number of solvable levels to generate
	#if !solvable then this will log both solvable
	def generate_levels(self, num, solvable = True):

		for i in range(num):
			grid_data = generator.generate_level()
			grid = grid_data["grid"]

			#this line represents a failure in so  many ways at a very high level. TBF I wrote the initial solver years before I decide to write the rest of this.
			#I could refactor this pretty easily, but I wont.
			#Don't smooth moves for clean data
			solution = unblocker.unblock(board = grid, grid = None, smooth = False)