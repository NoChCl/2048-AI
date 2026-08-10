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
	oldMT=16
	done=False
	invalidMoves=0
	last3=[]
	while True:
		n = netInput(net, TABLE)

		realI=np.argmax(n[:4])

		targs=[.5,.5,.5,.5, 0, 0, 0, 0, 0]

		numList=[0,1,2,3]
		numList+=[numList.pop(realI)]

		trueTable=TABLE.copy()
		trueLast3=last3.copy()

		for i in numList:
			last3=trueLast3.copy()
			TABLE=trueTable.copy()
			direction = LETTERS[i]
			last3+=[direction]
			new_table = key(direction, TABLE.copy())


			mt=getMtNumb(new_table)
			mtDif=mt-oldMT
			
			if mtDif<0:
				net.reward=-.5/13
			else:
				net.reward=(((mtDif+1)**1.25)-.5)/13

			net.reward+=(mt-2)/160

			if len(last3)>3:
				last3=last3[-3:]
				if i<=1:
					dirOpposite=LETTERS[i+2]
				else:
					dirOpposite=LETTERS[i-2]
				if dirOpposite==last3[-2]:
					net.reward-=.03
				elif dirOpposite==last3[-3]:
					net.reward-=.015
			elif len(last3)==2:
				if i<=1:
					dirOpposite=LETTERS[i+2]
				else:
					dirOpposite=LETTERS[i-2]
				if dirOpposite==last3[-2]:
					net.reward-=.03



			if not np.array_equal(new_table, TABLE):
				TABLE = randomfill(new_table)
				net.reward+=.05
				if i == realI:
					iterations += 1
			else:
				net.reward-=.8
				if i == realI:
					invalidMoves+=1
					if invalidMoves>500:
						logQueue.put((id, "WARNING", "Too many invalid moves, ending game"))
						done=True
				

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

		targs[-1]=mt/16

		oldMT=mt


		net.train(targs)
		if done:
			break
	

	return (getScore(TABLE), net, (invalidMoves/(invalidMoves+iterations))*100)


	
def directionIsValid(direction, oldTable):
	newTable=key(direction, oldTable.copy())

	return not np.array_equal(newTable, oldTable)




def key(direction, TABLE):
	if direction == 'w':
		for pi in range(1, 4):
			for pj in range(4):
				if TABLE[pi][pj] != 0:
					TABLE = moveup(pi, pj, TABLE)
	elif direction == 's':
		for pi in range(2, -1, -1):
			for pj in range(4):
				if TABLE[pi][pj] != 0:
					TABLE = movedown(pi, pj, TABLE)
	elif direction == 'a':
		for pj in range(1, 4):
			for pi in range(4):
				if TABLE[pi][pj] != 0:
					TABLE = moveleft(pi, pj, TABLE)
	elif direction == 'd':
		for pj in range(2, -1, -1):
			for pi in range(4):
				if TABLE[pi][pj] != 0:
					TABLE = moveright(pi, pj, TABLE)
	return TABLE

def movedown(pi, pj, T):
	justcomb = False
	while pi < 3 and (T[pi+1][pj] == 0 or (T[pi+1][pj] == T[pi][pj] and not justcomb)):
		if T[pi+1][pj] == 0:
			T[pi+1][pj] = T[pi][pj]
		elif T[pi+1][pj] == T[pi][pj]:
			T[pi+1][pj] += T[pi][pj]
			justcomb = True
		T[pi][pj] = 0
		pi += 1
	return T

def moveleft(pi, pj, T):
	justcomb = False
	while pj > 0 and (T[pi][pj-1] == 0 or (T[pi][pj-1] == T[pi][pj] and not justcomb)):
		if T[pi][pj-1] == 0:
			T[pi][pj-1] = T[pi][pj]
		elif T[pi][pj-1] == T[pi][pj]:
			T[pi][pj-1] += T[pi][pj]
			justcomb = True
		T[pi][pj] = 0
		pj -= 1
	return T

def moveright(pi, pj, T):
	justcomb = False
	while pj < 3 and (T[pi][pj+1] == 0 or (T[pi][pj+1] == T[pi][pj] and not justcomb)):
		if T[pi][pj+1] == 0:
			T[pi][pj+1] = T[pi][pj]
		elif T[pi][pj+1] == T[pi][pj]:
			T[pi][pj+1] += T[pi][pj]
			justcomb = True
		T[pi][pj] = 0
		pj += 1
	return T

def moveup(pi, pj, T):
	justcomb = False
	while pi > 0 and (T[pi-1][pj] == 0 or (T[pi-1][pj] == T[pi][pj] and not justcomb)):
		if T[pi-1][pj] == 0:
			T[pi-1][pj] = T[pi][pj]
		elif T[pi-1][pj] == T[pi][pj]:
			T[pi-1][pj] += T[pi][pj]
			justcomb = True
		T[pi][pj] = 0
		pi -= 1
	return T




#main()
