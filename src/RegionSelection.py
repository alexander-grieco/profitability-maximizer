import sys
import math

# calculates estimated region profitability value from historical (i.e. Yesterday's)
# region profitability values
def newVal(val):
	tot = sum(val)

	for i in range(len(val)):
		val[i] = (tot/float(len(val))+val[i])/float(2)

	return(val)

# Gets list of region profitability and region adjacency info
def getRegion(file, day):
	temp = file.readline().rstrip()
	temp = temp[1:-1]
	temp = temp.split('),(')

	new = []
	for item in temp:
		new.append(item.split(','))

	val = []
	adj = []
	for item in new:
		val.append(int(item[1]))

	# if going off historical data, use historical region values
	if day == 'Yesterday':
		val = newVal(val)

	# stores region info along with adjaceny information
	final = []
	for i in range(len(temp)):
		#retrieves adjaceny information for next row
		adj.append(getAdj(file))
		final.append((new[i][0], val[i], adj[i]))

	passAdj = [0 for i in adj[0]]
	final.append(("PASS", 0, passAdj))
	return(final)

# selects the next row in the adjaceny matrix and converts
# string representation into an array
def getAdj(file):
	adj = []
	test = file.readline().rstrip()[1:-1].split(',')
	for x in test:
		adj.append(int(x))
	return(adj)


# Extracts the starting info from the input file
def getInfo(file):
	day = file.readline().rstrip()
	player = file.readline().rstrip()

	# gets region profitability and adjacency info
	info = sorted(getRegion(file, day), key=lambda x: (len(x[0]), x[0]))

	# extracts which regions have already been selected
	picked = file.readline().rstrip().split(',')
	# case when no regions have been selected
	if picked[0] == '*':
		picked = []

	#extracts the maximum depth of search tree
	maxDepth = int(file.readline().rstrip())

	return(day, player, info, picked, maxDepth)

# determines who picked first (player 1 or 2) and
# fills their picked queues appropriately
def getFirst(picked):
	if len(picked)%2 == 0:
		maxNodes = picked[0:][::2]
		minNodes = picked[1:][::2]

	else:
		minNodes = picked[0:][::2]
		maxNodes = picked[1:][::2]

	return maxNodes, minNodes

# rounds number to nearest whole number
def roundNum(num):
	if num >= 0:
		if num - math.floor(num) < 0.5:
			return math.floor(num)
		return math.ceil(num)
	else:
		if num - math.floor(num) <= 0.5:
			return math.floor(num)
		return math.ceil(num)

# returns total profitability of most profitable path
def rVal(info):
	tot = 0
	for val in maxNodes:
		for tup in info:
			if val == tup[0]:
				tot = tot + tup[1]

	return(roundNum(tot))

def findAdj(info, player):
	if player == "R1":
		node = maxNodes
	else:
		node = minNodes

	options = []
	for item in node:
		for i in range(len(info)):
			if item == info[i][0]:
				adj = info[i][2]
				pos = i

		for i in range(len(adj)):
			if i != pos and adj[i] == 1 and (info[i][0] not in maxNodes and info[i][0] not in minNodes) and info[i][0] not in options:
					options.append(info[i][0])


	sorted(options)
	return(options)

# returns a list of available regions the player can selects
# if none available, returns "PASS"
def getOptions(info, player):
	node = 0
	if player == "R1":
		if len(maxNodes) == 0:
			node = None

	else:
		if len(minNodes) == 0:
			node = None

	options = []
	if node != None:
		options = findAdj(info, player)
	else:
		for item in info:
			if item[0] not in maxNodes and item[0] not in minNodes and item[0] != "PASS":
				options.append(item[0])

	if len(options) == 0:
		options.append("PASS")
	return options

# returns the node that maximizes the profitability of the next player to go
def minimaxDecision(depth, info):
	# a list of available regions for the next player
	options = getOptions(info, "R1")

	node = None
	val = -sys.maxsize

	# Searches over all regions available to player
	for i in range(len(options)):
		#initiates minimax search with alpha-beta pruning
		maxNodes.append(options[i])
		temp_val = minVal(depth + 1, info, val, sys.maxsize)
		maxNodes.pop()
		# If profitability is greater than current most profitable...
		if temp_val > val:
			node = options[i]
			val = temp_val

	return node

# determines maximum profitability for next pick for R1
def maxVal(depth, info, alpha, beta):
	options = getOptions(info, "R1")

	# recursion end
	if depth >= maxDepth:
		maxNodes.append(options[0])
		val = rVal(info)
		final.append(val)
		maxNodes.pop()
		return val

	v = -sys.maxsize
	for item in options:
		maxNodes.append(item)
		temp_val = minVal(depth + 1, info, alpha, beta)
		maxNodes.pop()

		if temp_val > v:
			v = temp_val
		if v >= beta:
			return v

		alpha = max(alpha, v)
	return v

# determines minimum profitability for R1 given R2's selection
def minVal(depth, info, alpha, beta):
	options = getOptions(info, "R2")
	if depth >= maxDepth:
		minNodes.append(options[0])
		val = rVal(info)
		final.append(val)
		minNodes.pop()
		return val


	v = sys.maxsize
	for item in options:
		minNodes.append(item)
		temp_val = maxVal(depth + 1, info, alpha, beta)
		minNodes.pop()

		if temp_val < v:
			v = temp_val
		if v <= alpha:
			return v
		beta = min(beta, v)
	return v

maxNodes = []
minNodes = []
final = []

if __name__ == '__main__':
	#Creating input and output files
	inputFile = open(sys.argv[2])

	outputFile = open("output.txt", "w")

	#gathering info from input file
	day, player, info, picked, maxDepth = getInfo(inputFile)

	#filling up arrays with areas already picked
	depth = len(picked)
	maxNodes, minNodes = getFirst(picked)

	#adjusting maxDepth if it is greater than the number of nodes
	if(maxDepth > len(info) - 1): #the minus 1 is for the "PASS" that I add to info
		maxDepth = len(info) - 1

	#minimax with alpha-beta pruning
	node = minimaxDecision(depth, info)

	#Reading to the output file
	outputFile = open("output.txt", "w")
	outputFile.write(node + '\n')
	outputFile.write(str(final)[1:-1].replace(" ", ""))
