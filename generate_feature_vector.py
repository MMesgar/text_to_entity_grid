#########################
##	We generate transitions by 
##  brute-force algorithms
#########################
def is_a_solution(x, n):
	# check if the length of a candidate is n
	return (len(x) == n)

def generate_all_childern(x, role_set):

	# given a candidate generates its all childeren
	childern = []
	
	for role in role_set:

		child  = x + tuple(role)

		childern.append(child)

	return childern

def generate_transitions(role_set, n):

	trans = []

	candidates  = [tuple()] # [()]

	while (len(candidates)>0):

		 cand = candidates.pop(0)

		 if  is_a_solution(cand, n):

			trans.append(cand)

		 else:

			candidates += generate_all_childern(cand, role_set)

	return trans

#########################
##	load a grid file
#########################
import pandas as pd
def load_grid_file(grid_path):

	with open(grid_path, 'rb') as f:

		grid_str = f.read()

	lines = grid_str.strip().split("\n")

	# A list of lists holding entity transitions.
	# This will become the data in a pandas
	# DataFrame representing the entity grid.
	grid = []

	# A list of entities in this document.
	# This will become the index of a pandas
	# DataFrame representing the entity grid.
	entities = []

	for line in lines:

		if (line.strip() is not ""):

			# Each entry is separated by a space.
			roles = line.strip().split(" ")

			# The first entry is the entity name. Add this to the index.
			entities.append(roles[0].decode("ascii", "ignore"))

			# Add the transitions (these start at index 1)
			# for this entity to egrid.
			roles = [roles[t].upper() for t in range(1, len(roles))]
			
			grid.append(roles)

	egrid_df = pd.DataFrame(grid, index=entities)

	return egrid_df, entities


#########################
##	compute the probabilities of transitions in a grid
## 	We define a dictionary whose keys are transtions and 
##  values are the count of corrosponding transitions in the grid
##  In this way, we traverse the grid only once. 
#########################
def get_trans_probability(grid, transitions):

	# map transitions to a dictionary
	transitions_dict = {}

	for tran in transitions:
	
		transitions_dict[tran] = 0.0

	# length of transitions
	trans_length = len(transitions[0])

	# traverse the grid
	n_entities, n_sentences =  grid.shape

	for row in range(0, n_entities):

		for col in range(0, n_sentences - trans_length + 1):
			
			visited_tran = tuple()

			for k in range(col, col + trans_length):

				visited_tran += tuple(grid[k][row].upper()) # data frame is like Excel, first you should give the column then row
			
			transitions_dict[visited_tran] += 1

	# total number of transitions
	n_t_star = sum([v for v in transitions_dict.values()])

	#conver row count numbers to probabilities
	for k,v in transitions_dict.items():

		transitions_dict[k] = v / n_t_star
	
	return transitions_dict



#########################
##	an interface for outter modules
#########################
def get_feat_vector(role_set= ['S','O','X','-'], n=2, grid_path=''):

	#####################
	## generate all possible transitions {S,O,X,-}^n
	## role_set = {S,O,X,-}
	## n = length of transitions
	##################### 
	transitions = generate_transitions(role_set, n=n)

	#####################
	## Let's load a grid file
	#####################
	grid, entities = load_grid_file(grid_path)

	#####################
	## compute the probability of each transition in a given grid
	## grid = entity grid
	## t = transtion
	#####################

	p = get_trans_probability(grid, transitions) 	

	return p

	
#########################
##	Main
#########################
if __name__ =="__main__":

	role_set=['S','O','X','-']
	n = 2

	#####################
	## generate all possible transitions {S,O,X,-}^n
	## role_set = {S,O,X,-}
	## n = length of transitions
	##################### 
	transitions = generate_transitions(role_set, n=n)

	print "The number transitions with length %d is %d"%(n, len(transitions))

	#####################
	## Let's load a grid file
	#####################
	grid_path = './grids/sample1.grid'
	
	grid, entities = load_grid_file(grid_path)

	print grid
	print

	#####################
	## compute the probability of each transition in a given grid
	## grid = entity grid
	## t = transtion
	#####################

	p = get_trans_probability(grid, transitions) 	

	print p
