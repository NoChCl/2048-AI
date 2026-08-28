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




def avrgGame(net, logQueue, id):
	
	TABLE = np.zeros((4, 4), dtype=int)

	sumScore=0
	sumError=0
	gamesPlayed=0
	
	
	for i in range(500):
		try:
			thisGame, net, percentError = runGame(TABLE.copy(), net, logQueue, id)
		
			sumScore+=thisGame
			sumError+=percentError
			gamesPlayed+=1


		except Exception as e:
			logQueue.put((id, "ERROR", str(e)))

	avgScore=sumScore/gamesPlayed if gamesPlayed > 0 else 0
	avgError=sumError/gamesPlayed if gamesPlayed > 0 else 100

	# return the avrg score, the net and whatever errors it had
	return [avgScore, net, avgError]


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


def runGame(TABLE, net=NuralNet(16,make()[1]), logQueue=None, id=-1):
	TABLE=randomfill(TABLE)
	TABLE=randomfill(TABLE)
	iterations=1
	done=False
	invalidMoves=0
	while True:
		n = netInput(net, TABLE)

		realI=np.argmax(n[:4])

		targs=[.5,.5,.5,.5, 0, 0, 0, 0, 0]

		numList=[0,1,2,3]
		numList+=[numList.pop(realI)]

		trueTable=TABLE.copy()

		for i in numList:
			TABLE=trueTable.copy()
			direction = LETTERS[i]
			new_table = key(direction, TABLE.copy())



			if not np.array_equal(new_table, TABLE):
				TABLE = randomfill(new_table)
				net.reward=.1
				if i == realI:
					iterations += 1
			else:
				net.reward=-.2
				if i == realI:
					invalidMoves+=1
					if invalidMoves>500:
						logQueue.put((id, "WARNING", "Too many invalid moves, ending game"))
						done=True

			validSecondaries=0
			for x, d in enumerate(["w", "a", "s", "d"]):
				if directionIsValid(d, TABLE):
					validSecondaries+=1
			

			if gameOver(TABLE):
				net.reward-=.25
				if i == realI:
					done=True

			targs[i]+=maxMin(net.reward)



		for x, d in enumerate(["w", "a", "s", "d"]):
			if directionIsValid(d, trueTable):
				targs[x+4]=1
			else:
				targs[x]=0




		net.train(targs)
		if done:
			break
	

	return (getScore(TABLE), net, (invalidMoves/(invalidMoves+iterations))*100)


	
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
