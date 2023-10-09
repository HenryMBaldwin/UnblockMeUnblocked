from tensorflow.keras.models import load_model
import numpy as np
import data_factory
import unblock
# Load the model

class ml_unblocker:

	def __init__(self):
		self.model = load_model('models/unblock_me_solver')
		#need some functions from here
		self.data_f = data_factory.Level_Factory() 
		self.unblocker = unblock.Unblocker()

	def solve_state(self, state):

		processed_state = self.data_factory.convert_to_one_hot(state)

		# Ensure that this new_state should be preprocessed (normalized/encoded) in the same way as your training data.
		new_state = np.array([processed_new_state])  # Replace processed_new_state with your preprocessed state.

		new_state = new_state.reshape(-1, 6, 6, 6) 

		# Use the model to predict the best move for the given state.
		predicted_move = model.predict(new_state)

		print(type(predicted_move))
		# Now, you can decode the predicted_move back to your move representation.
		decoded_move = decode_move(predicted_move)  # Replace decode_move with the actual function you use to decode your moves.
	
	#takes in a move from the ml model and outputs a state
	def decode_move(self, move, state):


		move = list(map(lambda x: int(x*5),move))

		r1,c1,r2,c2 = move
		gridside = self.unblocker.get_gridside(r1,c1,state)

		direction = ""
		#get move direction and check for move validity based on coordinates
		if r1 != r2 && c1 != c2:
			self.move_error("Can't move diagonally.", move)
		if abs(r1-r2) > 1 || abs(c1-c2) > 1;
			self.move_error("Can't move more than one position at a time.", move)
		if r1 > r2:
			direction = "u"
		elif r2 > r1:
			direction = "d"
		elif c1 > c2:
			direction = "l"
		elif c2 > c1:
			direction = "u"
		else:
			self.move_error("No move was made.", move)

		#check for move validity based on gridside of startin coordinate
		if gridside == "m":
			self.move_error("Can't perform move on middle of block.", move)
			
		if gridside == 

	def move_error(self, details, move):
		print("Error Invalid Move: " + details + "\n" + self.pretty_print_move(move))
		quit()
	def pretty_print_move(self,move):
		#pretty prints a move array 
		r1,c1,r2,c2 = move
		return "(" + str(r1) + "," +str(c1) + ") -> " + "(" + str(r2) + "," + str(c2) +")"





