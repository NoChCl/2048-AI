import random, sys, time, pickle
from tqdm import tqdm
from ai import *
from random import randint
from random import randint
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
		
		if i%1000==0:
			sleep(3)
    
    
    print("\nSaving SCORE NETS")
    pickle.dump(scoreNet, open("scoreNet.txt","wb"))


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
            avrgScore=runGame(TABLE.copy(), net)
            errored=False
            break
        except Exception as e:
            errors+=[e]
            errored=True
            
            
    # after 10 times, its a lost cause, write it off as a 0
    if errored:
        return [0, net, errors]
    
    # run it a total of 10 times, 9 extra and 1 starting
    for i in range(9):
        try:
            avrgScore+=runGame(TABLE.copy, net)
            avrgScore/=2
        except Exception as e:
            errors+=[e]
    
    # return the avrg score, the net and whatever errors it had
    return [avrgScore, net, errors]





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
    
    while True:
        n = netInput(net, TABLE)
        direction = ["w", "a", "s", "d"][np.argmax(n)]
        new_table = key(direction, TABLE.copy())

        if not np.array_equal(new_table, TABLE):
            TABLE = randomfill(new_table)
        else:
            break

        if gameOver(TABLE):
            break

    return getScore(TABLE)
    

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
