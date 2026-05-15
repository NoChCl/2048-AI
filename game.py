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




def avrgGame(net, logQueue, id):
	
	TABLE = np.zeros((4, 4), dtype=int)
	
	avrgScore, net, avgError = runGame(TABLE.copy(), net, logQueue, id)
	

	# run it a total of 500 times, 499 extra and 1 starting
	for i in range(499):
		try:
			thisGame, net, percentError = runGame(TABLE.copy(), net, logQueue, id)
		
			avrgScore+=thisGame
			avgError+=percentError

			avrgScore/=2
			avgError/=2

		except Exception as e:
			logQueue.put((id, "ERROR", str(e)))
	# return the avrg score, the net and whatever errors it had
	return [avrgScore, net, avgError]


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
	z=0
	while True:
		n = netInput(net, TABLE)

		indexy=np.argmax(n[:4])
		direction = ["w", "a", "s", "d"][indexy]
		new_table = key(direction, TABLE.copy())

		
		mt=getMtNumb(new_table)
		mtDif=mt-oldMT
		oldMT=mt
		targs=[.5,.5,.5,.5, 0, 0, 0, 0, mt/16]

		net.reward=(max(mtDif*.15, -.1))

		for i, d in enumerate(["w", "a", "s", "d"]):
			if directionIsValid(d, TABLE):
				targs[i+4]=1


		if not np.array_equal(new_table, TABLE):
			TABLE = randomfill(new_table)
			net.reward+=.05
			iterations+=1
		else:
			net.reward-=.8
			invalidMoves+=1

			if invalidMoves>500:
				logQueue.put((id, "WARNING", "Too many invalid moves, ending game"))
				done=True
			

		if gameOver(TABLE):
			net.reward-=1
			done=True
			
		

		targs[indexy]+=maxMin(net.reward)

		'''print(
    	"reward:", net.reward,
   		 "move:", direction,
   		 "mtDif:", mtDif
)'''

		net.train(targs)

		if z<iterations:
			'''

			stwing=""

			
			print(f"\n{targs}")
			print(n)

			#time.sleep(.25)
			#'''
			z=iterations
		
		if done:
			break
	
	#print(f"Percent invalid: {(invalidMoves/(invalidMoves+iterations))*100}%")

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
