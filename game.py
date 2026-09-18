import random, sys, time, pickle
from tqdm import tqdm
from ai import *
from random import randint
import numpy as np
import math

UP = 'up'
DOWN = 'down'
LEFT = 'left'
RIGHT = 'right'

LETTERS = ['w', 'a', 's', 'd']




def avrgGame(net, logQueue, scoreUpdates, masterHighScores, id):
	
	TABLE = np.zeros((4, 4), dtype=int)

	sumScore=0
	sumError=0
	gamesPlayed=0
	stage=1
	
	localHighScore= masterHighScores[id]
	
	for i in range(500):
		try:
			thisGame, net, percentError = runGame(TABLE.copy(), net, logQueue, id, stage)
		
			sumScore+=thisGame
			sumError+=percentError
			gamesPlayed+=1

			avgScore=sumScore/gamesPlayed if gamesPlayed > 0 else 0
			avgError=sumError/gamesPlayed if gamesPlayed > 0 else 100

			if stage == 1 and avgError < 5: stage=2 and logQueue.put((id, "INFO", f"Promoted to Stage 2"))
			elif stage == 2 and thisGame >300: stage=3 and logQueue.put((id, "INFO", f"Promoted to Stage 3"))

			if stage > 1 and avgError > 10: stage=1 and logQueue.put((id, "INFO", f"Demoted to Stage 1"))
			elif stage > 2 and avgScore < 200: stage=2 and logQueue.put((id, "INFO", f"Demoted to Stage 2"))


			if thisGame > localHighScore:
				localHighScore = thisGame
				scoreUpdates.put((id, localHighScore))
				

		except Exception as e:
			logQueue.put((id, "ERROR", str(e)))

	# return the avrg score, the net and whatever errors it had
	return [avgScore, net, avgError]

def trainingSequence(TABLE, net=NuralNet(16,make()[1]), logQueue=None, id=-1, trainingStage=2):

	fullGame, net, error, replayQueue = runGame(TABLE, net, logQueue, id, trainingStage)


	with open(f"replays.pkl", "rb") as f:
		replays = pickle.load(f)

	replays += replayQueue

	newReplays = []

	for replay in replays:
		if not any(np.array_equal(replay, r) for r in newReplays):
			newReplays.append(replay)

	replays = newReplays

	if len(replays) > 1000:
		replays=replays[-1000:]

	with open(f"replays.pkl", "wb") as f:
		pickle.dump(replays, f)

	loopNumb = min(len(replays), 25)
	for i in range(loopNumb):
		thisTable=replays.pop(random.randint(0, len(replays)-1))

		net.train(getTargs(thisTable, trainingStage))


	return [fullGame, net, error]
	


def getMtNumb(TABLE):
	mts=0
	for row in TABLE:
		for cell in row:
			if cell == 0:
				mts+=1
	return mts



def randomfill(TABLE):
	if not np.any(TABLE == 0):
		return TABLE

	while True:
		w = randint(0, 15)
		row, col = divmod(w, 4)
		if TABLE[row][col] == 0:
			TABLE[row][col] = 4 if randint(1, 5) == 5 else 2
			break
	return TABLE

def gameOver(TABLE):
	for i in range(4):
		for j in range(4):
			if TABLE[i][j] == 0:
				return False
			for dx, dy in [(-1,0), (1,0), (0,-1), (0,1)]:
				ni, nj = i + dx, j + dy
				if 0 <= ni < 4 and 0 <= nj < 4 and TABLE[ni][nj] == TABLE[i][j]:
					return False
	return True

def getScore(table):
	return np.sum(table)


def runGame(TABLE, net=NuralNet(16,make()[1]), logQueue=None, id=-1, trainingStage=2):
	TABLE=randomfill(TABLE)
	TABLE=randomfill(TABLE)
	iterations=1
	done=False
	totalInvalidMoves=0
	stateInvalidMoves=0
	replayQueue = []
	while True:
		n, net = netInput(net, TABLE)

		net.train(getTargs(TABLE, trainingStage))

		index=np.argmax(n[:4])


		iterations += 1


		direction = LETTERS[index]

		new_table = key(direction, TABLE.copy())

		if not np.array_equal(new_table, TABLE):
			stateInvalidMoves=0
			TABLE = randomfill(new_table)
				
		else:
			totalInvalidMoves+=1
			stateInvalidMoves+=1

			if stateInvalidMoves>16:
				logQueue.put((id, "WARNING", "Too many invalid moves, ending game"))
				done=True

		validDirections=0
		for d in LETTERS:
			if directionIsValid(d, TABLE): validDirections+=1
		if validDirections <=2:
			replayQueue.append(TABLE.copy())
		

		if gameOver(TABLE):
			done=True

		if done:
			break
	

	return (getScore(TABLE), net, (totalInvalidMoves/(totalInvalidMoves+iterations))*100, replayQueue)

def getTargs(TABLE, trainingStage):

	targs=[.5,.5,.5,.5, 0, 0, 0, 0, 0]

	trueTable=TABLE.copy()
	trueMT=getMtNumb(trueTable)
	iterations += 1

	for i in range(4):
		TABLE=trueTable.copy()
		direction = LETTERS[i]
		new_table = key(direction, TABLE.copy())

		

		if not np.array_equal(new_table, TABLE):
			TABLE = randomfill(new_table)
			reward=.1
				
		else:
			reward=0
			

		mt=getMtNumb(TABLE)
		mtDif=mt-trueMT
		percentMtDif=mtDif/16

		if trainingStage >1:
			validSecondaries=0
			for d in LETTERS:
				if directionIsValid(d, TABLE): validSecondaries+=1
			if validSecondaries == 0: reward=-.2

			reward+=.05*validSecondaries
			
		elif trainingStage >2:
			reward+=percentMtDif*.4

		if gameOver(TABLE):
			reward-=.25


		targs[i]+=maxMin(reward)



	for x, d in enumerate(LETTERS):
		if directionIsValid(d, trueTable):
			targs[x+4]=1
		else:
			targs[x]=0


	targs[-1]=percentMtDif
	return targs

	
def directionIsValid(direction, oldTable):
	newTable=key(direction, oldTable.copy())

	return not np.array_equal(newTable, oldTable)




def key(direction, TABLE):
    # Work on a copy so the operation is atomic.
    newTable = TABLE.copy()

    def processLine(line):
        # Remove empty spaces
        line = [x for x in line if x != 0]

        result = []
        i = 0

        while i < len(line):
            # If this tile can merge with the next one,
            # merge them and skip BOTH original tiles.
            if i + 1 < len(line) and line[i] == line[i + 1]:
                result.append(line[i] * 2)
                i += 2
            else:
                result.append(line[i])
                i += 1

        # Fill remaining spaces with zeros
        result += [0] * (4 - len(result))

        return result

    if direction == 'a':  # left
        for i in range(4):
            newTable[i] = processLine(TABLE[i])

    elif direction == 'd':  # right
        for i in range(4):
            line = processLine(TABLE[i][::-1])
            newTable[i] = line[::-1]

    elif direction == 'w':  # up
        for j in range(4):
            line = processLine(TABLE[:, j])
            newTable[:, j] = line

    elif direction == 's':  # down
        for j in range(4):
            line = processLine(TABLE[::-1, j])
            newTable[:, j] = line[::-1]

    return newTable




#main()
