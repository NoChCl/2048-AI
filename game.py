import random, sys, time, pickle
from tqdm import tqdm
from ai import *
from random import randint
from random import randint
import numpy as np
import math

UP = 'up'
DOWN = 'down'
LEFT = 'left'
RIGHT = 'right'


def main():    
	print("\nLoading Generated Nets")
	
	nets=pickle.load(open("nets.txt","rb"))
	
	scoreNet=[]
	
	print("\nRunning Nets")
	
	
	for i, net in enumerate(tqdm(nets)):

		scoreNet += [avrgGame(net)]   
		
		net=scoreNet[-1][1]

		if i%1000==0:
			#sleep(3)
			pass
	
	
	print("\nSaving SCORE NETS")
	pickle.dump(scoreNet, open("scoreNet.txt","wb"))

	print("\nSaving Nets")
	pickle.dump(nets, open("nets.txt","wb"))


'''
def worker(net, queue):
	result = avrgGame(net)
	
	queue.put(result)
	



def main():
	print("\nLoading Generated Nets")
	
	nets = pickle.load(open("nets.txt", "rb"))


	print("\nRunning Nets")
	
	MAX_PROCESSES = max(multiprocessing.cpu_count() - 2, 1)
		
	scoreNet = []
	
	queue = multiprocessing.Queue()
	
	processes = []
	
	active = 0
	
	for net in tqdm(nets):
		
		while active>=MAX_PROCESSES:
			if not queue.empty():
				scoreNet.append(queue.get())
			
			processes = remvDedProc(processes)
			active=len(processes)
			
		p = multiprocessing.Process(target=worker, args=(net, queue))
		p.start()
		active+=1
		processes.append(p)
		
		

			
	while active !=0:
		if not queue.empty():
			scoreNet.append(queue.get())
		processes = remvDedProc(processes)
		active=len(processes)


	# Collect finished processes
	while not queue.empty():
		scoreNet.append(queue.get())

	
	print("\nSaving SCORE NETS")
	
	pickle.dump(scoreNet, open("scoreNet.txt", "wb"))
	
def remvDedProc(processes):
	for p in processes:
		if not p.is_alive():
			p.join()
			processes.remove(p)
	return processes

'''


def avrgGame(net):
	
	TABLE = np.zeros((4, 4), dtype=int)
	
	errors=[]
	
	# try 10 times to get valid starting avrg
	# if ever succede, move on, else, try again
	
	for i in range(10):
		try:
			avrgScore = runGame(TABLE.copy(), net)[0]
			errored=False
			break
		except Exception as e:
			if str(e) != "'builtin_function_or_method' object is not iterable":
				print(e)
			errored=True
			
			
	# after 10 times, its a lost cause, write it off as a 0
	if errored:
		return [0, net]
	

	# run it a total of 1000 times, 9999 extra and 1 starting
	for i in tqdm(range(999)):
		try:
			thisGame, net = runGame(TABLE.copy(), net)
		
			avrgScore+=thisGame

			avrgScore/=2
		except Exception as e:
			print(e)
	
	# return the avrg score, the net and whatever errors it had
	return [avrgScore, net]


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


def runGame(TABLE, net=NuralNet(16,make()[1])):
	TABLE=randomfill(TABLE)
	TABLE=randomfill(TABLE)
	iterations=1
	oldMT=16
	done=False
	gmBonus=.05
	invalidMoves=0
	while True:
		
		n = netInput(net, TABLE)

		indexy=np.argmax(n[:4])
		direction = ["w", "a", "s", "d"][indexy]
		new_table = key(direction, TABLE.copy())

		
		mt=getMtNumb(new_table)
		mtDif=mt-oldMT
		oldMT=mt
		targs=[.5,.5,.5,.5, 0, 0, 0, 0, mt/16]

		net.reward=(mtDif*.15)

		for i, d in enumerate(["w", "a", "s", "d"]):
			if directionIsValid(d, TABLE):
				targs[i+3]=1


		if not np.array_equal(new_table, TABLE):
			TABLE = randomfill(new_table)
			net.reward+=gmBonus
			net.reward+=.05*iterations
			iterations+=1
		else:
			net.reward-=.8
			invalidMoves+=1
			

		if gameOver(TABLE):
			net.reward-=5
			done=True
			
		

		targs[indexy]=maxMin(net.reward)

		'''print(
    	"reward:", net.reward,
   		 "move:", direction,
   		 "mtDif:", mtDif
)'''

		net.trianOutLayer(targs, .0005)



		
		if done:
			break
	
	#print(f"Percent invalid: {(invalidMoves/(invalidMoves+iterations))*100}%")

	return (getScore(TABLE), net)


	
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
