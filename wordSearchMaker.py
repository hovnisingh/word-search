
import sys
import random
import copy 

global verbose
global solution
global count
global failures

#============================================================================
# get_arg() returns command line arguments.
#============================================================================
def get_arg(index, default=None):
    '''Returns the command-line argument, or the default if not provided'''
    return sys.argv[index] if len(sys.argv) > index else default


#--------------------------------------------------------------------------------
# GIRD CLASS

class Grid:

    #----------------------------------------------------------------------------
	# Grid: 
	# A NUM_ROWS x NUM_COLS grid of characters
	#----------------------------------------------------------------------------

    def __init__(self, nRows, nCols):
        self.NUM_ROWS = nRows
        self.NUM_COLS = nCols
        self.grid = [[" " for cols in range(nCols)] for rows in range(nRows)]

    def __getitem__(self, index):
        return self.grid[index]

    #========================================================================
	# Prints Puzzle 
	#========================================================================

    def __str__(self):
        out = "+" + "---+"*self.NUM_ROWS + "\n"
        for i in range(self.NUM_ROWS):
            for j in range(self.NUM_COLS):
                out += "| " + self.grid[i][j] + " "
            out += "|" + "\n"
            out += "+" + "---+"*self.NUM_COLS + "\n"
        return out

#--------------------------------------------------------------------------------

#--------------------------------------------------------------------------------
# STATE CLASS

class State:

    #----------------------------------------------------------------------------
	# State: 
	# A State consisting of a Grid and list of Words
	#----------------------------------------------------------------------------
    def __init__(self, grid, words):
        self.grid = grid
        self.words = words

    #----------------------------------------------------------------------------
	# Returns partially filled in grid with remaining words to be placed in grid
	#----------------------------------------------------------------------------

    def __str__(self):
        return str(self.grid) + str(self.words)

#--------------------------------------------------------------------------------

#--------------------------------------------------------------------------------
# RULE CLASS

class Rule:

    #-------------------------------------------------------------------------------------
	# Rule: 
	# A Rule consisting of a word, row, column, horizonal direction, and vertical direction
	#--------------------------------------------------------------------------------------
    def __init__(self, word, row, col, dh, dv):
        self.word = word
        self.row = row
        self.col = col
        self.dh = dh
        self.dv = dv
    
    #-------------------------------------------------------------------------------------
	# Returns string of the word, what position is it starting in, and what position it 
    # is proceeding in 
	#--------------------------------------------------------------------------------------

    def __str__(self):
        word = "Word: " + str(self.word)
        position = "Position: (%d, %d)" % (self.row, self.col)
        direction = "Direction: [%d, %d]" % (self.dh, self.dv)
        return str(word) + "\n" + str(position) + "\n" + str(direction)

    #----------------------------------------------------------------------------------------------
	# APPLYRULE:
    # Takes in state, creates deepcopy, checks if state meets all preconditions
    # If all preconditions are met, fill letter in grid and update row and column to match direction
    # Remove word and return updated state
    # If preconditions are not met, return original state
	#-----------------------------------------------------------------------------------------------

    def applyrule(self, state):
        state2 = copy.deepcopy(state) 
        for i in range(len(self.word)):
            if (self.precondition(state2)):
                state2.grid[self.row][self.col] = (self.word)[i]
                self.row += self.dv
                self.col += self.dh
            else:
                return state
        state2.words.remove(self.word)
        return state2

    #----------------------------------------------------------------------------------------------
	# PRECONDITION:
    # Takes in state, checks if row and column do not exceed grid boundaries
    # Checks if -1<= dh,dv <= 1 and |dh|+|dv| >0
    # Checks if place where letter is going to be filled in is empty or the same letter as the element already in it
	#-----------------------------------------------------------------------------------------------

    def precondition(self, state):
        if ((len(self.word)> state.grid.NUM_ROWS) or (len(self.word) > state.grid.NUM_COLS)):
            return False
        if ((self.row < 0) or (self.row >= state.grid.NUM_ROWS) or (self.col < 0) or (self.col >= state.grid.NUM_COLS)):
            return False
        if ((self.dh < -1) or (self.dv < -1) or (self.dh > 1) or (self.dv > 1) or ((abs(self.dh) + abs(self.dv)) <= 0)):
            return False
        for i in range(len(self.word)):
            if (state.grid[self.row][self.col] != " ") and (state.grid[self.row][self.col] != (self.word)[i]):
                return False
        return True

#---------------------------------------------------------------------------------------------


#----------------------------------------------------------------------------------------------
# ALLCANDIDATES:
# Takes in a word and state
# Loops through all possible rows, all possible columns, and all possible directions
# Checks if rules meet preconditions and creates list of all possible rules for a certain word
#-----------------------------------------------------------------------------------------------

def allcandidates(word, state):
    candidates = []
    DIRECTIONS  = [(-1,0), (-1,1), (-1,-1), (1,0), (1,1), (1,-1), (0,1), (0,-1)]
    row = range(0, state.grid.NUM_ROWS-1)
    col = range(0, state.grid.NUM_COLS-1)
    for i in row:
        for j in col:
            for x in DIRECTIONS:
                rule = Rule(word, i, j, x[0], x[1])
                if (rule.precondition(state)):
                    candidates.append(rule)
    return candidates

#----------------------------------------------------------------------------------------------
# GOAL:
# Takes in state and returns true if state's list of words is empty
#-----------------------------------------------------------------------------------------------

def goal(state):
    if (len(state.words) == 0):
        return True
    else:
        return False

#----------------------------------------------------------------------------------------------
# FLAILWILDLY:
# Takes in state
# While goal returns false, randomly choose a rule out of all the possible rules for a word
# Apply the rule and update the state
# Outputs rule chosen and current state
# When we have looped through all possible rules, exit
#-----------------------------------------------------------------------------------------------

def flailwildly(state):
    check = 0
    while (goal(state) == False):
        for x in state.words:
            allchoices = allcandidates(x, state)
            rule = random.choice(allchoices)
            print(rule)
            currentstate = rule.applyrule(state)
            print(currentstate)
            state = currentstate
            check += 1
            if (check > len(allchoices)):
                exit()

#------------------------------------------------------------------------------
# BACKTRACK: Takes in a statelist and depth bound (Iterative-Deepening Search)
# Intitializes state to first element in statelist
# FAILURE-1 : If state is already in the rest of the statelist
# FAILURE-2: If state reaches deadend
# FAILURE-3: If amount of states in statelist is greater than depth bound
# FAILURE-4: If there are no rules left for a word in the current state
# Loops through each word, and each possible word for a rule
# Applies rule and updates state and statelist, then backtracks
# FAILURE-5: End of loop and no successful paths found, all nodes were failures
#-------------------------------------------------------------------------------
def backtrack(statelist, depthbound):
    global count
    global failures
    state = statelist[0]
    if (statelist.count(state)>1):
        if (verbose):
            print("FAILURE-1: STATE ALREADY VISITED")
        return "FAILURE"
    if (deadend(state)):
        if (verbose):
            print("FAILURE-2: DEADEND")
        return "FAILURE"
    if (len(statelist) > depthbound):
        if (verbose):
            print("FAILURE-3: GREATER THAN DEPTHBOUND")
        return "FAILURE"
    if goal(state):
        return None
    for x in state.words:
        ruleset = (allcandidates(x, state))
        if (len(ruleset)==0):
            if verbose:
                print("FAILED-4: NO RULES")
            return "FAILURE"
        ruleset = heuristic(ruleset, state)
        for rule in ruleset:
            newstate = rule.applyrule(state)
            if (verbose):
                print(rule)
                print(newstate)
            newstatelist = [newstate] + statelist
            count += 1
            path = backtrack(newstatelist, depthbound)
            if (path != "FAILURE"):
                output = str(rule) +  "\n" + str(newstate.grid)
                solution.append(output)
                return solution
            else:
                failures+=1
    return "FAILURE"


#------------------------------------------------------------------------------
# DEADEND: If there is a word left in the current state's list of words, check
# if there are any possible rules left for that word
#-------------------------------------------------------------------------------
def deadend(state):
    for x in state.words:
        if (len(allcandidates(x,state)) ==0):
            return True
    return False


#------------------------------------------------------------------------------
# HEURISTIC: Loops through each rule in rulset and checks if each letter in the
# word overlaps
# Increments counter for every overlapping letter
# Sorts ruleset based on number of overlapping letters each rule's word contains
#-------------------------------------------------------------------------------

def heuristic(ruleset, state):
    overlapped = 0
    num = []
    for rule in ruleset:
        for i in range(len(rule.word)):
            if (state.grid[rule.row][rule.col] != (rule.word)[i]):
                overlapped += 1
        num.append(overlapped)
    rules_sorted = [ruleset for num, ruleset in sorted(zip(num, ruleset))]
    return rules_sorted

    
#--------------------------------------------------------------------------------
#  MAIN PROGRAM
#--------------------------------------------------------------------------------

if __name__ == '__main__':
    NUM_ROWS = int(get_arg(1))
    NUM_COLS = int(get_arg(2))
    filename = get_arg(3)
    is_verbose  = get_arg(4)
    if (is_verbose == 'verbose'):
        verbose = True
    else:
        verbose = False
    with open(filename, 'r') as infile:
        theWords = [line.strip() for line in infile]

    grid = Grid(NUM_ROWS, NUM_COLS)
    initialState = State(grid, theWords)
    state = State(initialState.grid, theWords)
    count = 0
    failures = 0
    statelist =[state]
    depthbound = len(state.words)*2
    solution = []
    path = backtrack(statelist, depthbound)
    if (path != "FAILURE"):
        path.reverse()
        for x in path:
            print(x)
    else:
        print(path)
    print("NUMBER OF FAILURES:", failures)
    print("NUMBER OF CALLS TO BACKTRACK:", count)


    
    