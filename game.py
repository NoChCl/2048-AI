import random, pickle
from ai import *
from random import randint
import numpy as np
import math

UP = 'up'
DOWN = 'down'
LEFT = 'left'
RIGHT = 'right'

LETTERS = ['w', 'a', 's', 'd']




def avrgGame(netSave, logQueue, scoreUpdates, masterHighScores, id):
	
	table = np.zeros((4, 4), dtype=int)

	sumScore=0
	sumError=0
	gamesPlayed=0
	
	localHighScore= masterHighScores[id]

	numbGames=50
	
	for i in range(numbGames):
		thisGameScore, netSave.net, percentError = trainingSequence(table.copy(), netSave.net, logQueue, id, netSave.stage)
	
		sumScore+=thisGameScore
		sumError+=percentError
		gamesPlayed+=1

		avgScore = ( sumScore + ( ( numbGames - gamesPlayed ) * netSave.avgScore ) ) / numbGames
		avgError = ( sumError + ( ( numbGames - gamesPlayed ) * netSave.error ) ) / numbGames

		if netSave.stage == 1 and avgError < 5:
			netSave.stage=2
			logQueue.put((id, "INFO", f"Promoted to Stage 2"))
		elif netSave.stage == 2 and thisGameScore > 300:
			netSave.stage=3
			logQueue.put((id, "INFO", f"Promoted to Stage 3"))

		if netSave.stage > 1 and avgError > 10:
			netSave.stage=1
			logQueue.put((id, "INFO", f"Demoted to Stage 1"))
		elif netSave.stage > 2 and avgScore < 200:
			netSave.stage=2
			logQueue.put((id, "INFO", f"Demoted to Stage 2"))


		if thisGameScore > localHighScore:
			localHighScore = thisGameScore
			scoreUpdates.put((id, localHighScore))

	netSave.avgScore = sumScore / gamesPlayed
	netSave.error = sumError / gamesPlayed
	netSave.highScore = localHighScore
	netSave.stage = netSave.stage

	# return the avrg score, the net and whatever errors it had
	return netSave

def trainingSequence(table, net=NuralNet(16,make()[1]), logQueue=None, id=-1, trainingStage=2):

	fullGameScore, net, error, replayBoards = runGame(table, net, logQueue, id, trainingStage)


	try:
		with open(f"replays_{id}.pkl", "rb") as f:
			replays = pickle.load(f)
	except FileNotFoundError:
		replays = []
		with open(f"replays_{id}.pkl", "wb") as f:
			pickle.dump(replays, f)

	replays += replayBoards

	newReplays = []

	for replay in replays:
		if not any(np.array_equal(replay, r) for r in newReplays):
			newReplays.append(replay)

	replays = newReplays

	minLen=250

	catagorizedBoards = catagorizeBoard(replays)

	for cat in catagorizedBoards:
		if len(cat) < minLen and len(cat) > 0:
			minLen=len(cat)

	for cat in catagorizedBoards:
		if len(cat) > minLen:
			random.shuffle(cat)
			del cat[minLen:]

	replays = []
	for cat in catagorizedBoards:
		replays.extend(cat)


	with open(f"replays_{id}.pkl", "wb") as f:
		pickle.dump(replays, f)

	loopNumb = min(len(replays), 128)
	for i in range(loopNumb):
		thisTable=replays.pop(random.randint(0, len(replays)-1))
		n, net = netInput(net, thisTable)
		index=np.argmax(n[:4])
		net.train(getTargs(thisTable, trainingStage, index))


	return [fullGameScore, net, error]

def catagorizeBoard(tables):
	catagorizedBoards = [[] for _ in range(4)]
	for table in tables:
		validDirections=0
		for d in LETTERS:
			if directionIsValid(d, table):
				validDirections+=1
		if validDirections > 0:
			catagorizedBoards[validDirections-1].append(table)
	return catagorizedBoards	


def getMtNumb(table):
	mts=0
	for row in table:
		for cell in row:
			if cell == 0:
				mts+=1
	return mts



def randomfill(table):
	if not np.any(table == 0):
		return table

	while True:
		w = randint(0, 15)
		row, col = divmod(w, 4)
		if table[row][col] == 0:
			table[row][col] = 4 if randint(1, 5) == 5 else 2
			break
	return table

def gameOver(table):
	for i in range(4):
		for j in range(4):
			if table[i][j] == 0:
				return False
			for dx, dy in [(-1,0), (1,0), (0,-1), (0,1)]:
				ni, nj = i + dx, j + dy
				if 0 <= ni < 4 and 0 <= nj < 4 and table[ni][nj] == table[i][j]:
					return False
	return True

def getScore(table):
	return np.sum(table)


def runGame(table, net=NuralNet(16,make()[1]), logQueue=None, id=-1, trainingStage=2):
	table=randomfill(table)
	table=randomfill(table)
	iterations=0
	done=False
	totalInvalidMoves=0
	stateInvalidMoves=0
	boards = [table.copy()]
	while True:
		n, net = netInput(net, table)
		
		index=np.argmax(n[:4])

		net.train(getTargs(table, trainingStage, index))

		iterations += 1


		direction = LETTERS[index]

		oldTable=table.copy()
		new_table = key(direction, table.copy())


		if not np.array_equal(new_table, table):
			stateInvalidMoves=0
			table = randomfill(new_table)
			boards.append(table.copy())
				
		else:
			totalInvalidMoves+=1
			stateInvalidMoves+=1

			if stateInvalidMoves>=64:
				logQueue.put((id, "WARNING", "Too many invalid moves, ending game"))
				done=True


		validDirections=0
		for d in LETTERS:
			if directionIsValid(d, table): validDirections+=1


		

		if gameOver(table):
			done=True

		if done:
			break
	

	return (getScore(table), net, (totalInvalidMoves/(totalInvalidMoves+iterations))*100, boards)

def getTargs(table, trainingStage, realDir):

	targs=[.5,.5,.5,.5, 0, 0, 0, 0, 0]

	trueTable=table.copy()
	trueMT=getMtNumb(trueTable)

	for x, d in enumerate(LETTERS):
		if directionIsValid(d, trueTable):
			targs[x+4]=1
		else:
			targs[x]=0


	rangeFour = [0, 1, 2, 3]
	rangeFour+=[rangeFour.pop(realDir)]

	
	for i in rangeFour:
		table=trueTable.copy()
		direction = LETTERS[i]
		new_table = key(direction, table.copy())

		

		if not np.array_equal(new_table, table):
			table = randomfill(new_table)
			reward=.1
				
		else:
			targs[i]=0
			continue

		mt=getMtNumb(table)
		mtDif=mt-trueMT
		percentMtDif=mtDif/16

		if trainingStage >1:
			if gameOver(table):
				reward-=.25

			validSecondaries=0
			for d in LETTERS:
				if directionIsValid(d, table): validSecondaries+=1
			if validSecondaries == 0: reward=-.2

			reward+=.05*validSecondaries
			
		if trainingStage >2:
			reward+=percentMtDif*.4

		targs[i]+=maxMin(reward)

	targs[-1]=percentMtDif+.5

	return targs

	
def directionIsValid(direction, oldTable):
	newTable=key(direction, oldTable.copy())

	return not np.array_equal(newTable, oldTable)




def key(direction, table):
    # Work on a copy so the operation is atomic.
    newTable = table.copy()

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
            newTable[i] = processLine(table[i])

    elif direction == 'd':  # right
        for i in range(4):
            line = processLine(table[i][::-1])
            newTable[i] = line[::-1]

    elif direction == 'w':  # up
        for j in range(4):
            line = processLine(table[:, j])
            newTable[:, j] = line

    elif direction == 's':  # down
        for j in range(4):
            line = processLine(table[::-1, j])
            newTable[:, j] = line[::-1]

    return newTable




#main()
