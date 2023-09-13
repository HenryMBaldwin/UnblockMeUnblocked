
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

		for i in range()