import random, sys,time, pickle
from tqdm import tqdm
from ai import *
from random import randint
import copy
import math

UP = 'up'
DOWN = 'down'
LEFT = 'left'
RIGHT = 'right'

TABLE=[[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0]]

def main():
    #myNet=NuralNet(16,make()[1])
    
    print("\nLoading Generated Nets")
    
    nets=pickle.load(open("nets.txt","rb"))
    
    scoreNet=[]
    
    print("\nRunning Nets")

    for net in tqdm(nets):
        
        
        
        try:
            scoreNet += [runGame(TABLE, net)]   
        except Exception as e:
            scoreNet+=[[0, net, "Error: "+str(e)]]
    
    print("/nSaving SCORE NETS")
    pickle.dump(scoreNet, open("scoreNet.txt","wb"))
    


def newGame():
    runGame(TABLE)

def randomfill(TABLE):
    # search for zero in the game table and randomly fill the places
    flatTABLE = sum(TABLE,[])
    if 0 not in flatTABLE:
        return TABLE
    empty=False
    w=0
    while not empty:
        w=randint(0,15)
        if TABLE[w//4][w%4] == 0:
            empty=True
    z=randint(1,5)
    if z==5:
        TABLE[w//4][w%4] = 4
    else:
        TABLE[w//4][w%4] = 2
    return TABLE

def gameOver(TABLE):
    # returns False if a box is empty or two boxes can be merged
    x = [-1, 0, 1, 0 ]
    y = [0 , 1, 0, -1]
    for pi in range(4):
        for pj in range(4):
            if TABLE[pi][pj] == 0:
                return False
            for point in range(4):
                if pi+x[point] > -1 and pi+x[point] < 4 and pj+y[point] > -1 and pj+y[point] < 4 and TABLE[pi][pj] == TABLE[pi+x[point]][pj+y[point]]:
                    return False
    return True

def checkForKeyPress():
    #checking if a key is pressed or not
    if len(pygame.event.get(QUIT)) > 0:
        terminate()

    keyUpEvents = pygame.event.get(KEYUP)
    if len(keyUpEvents) == 0:
        return None
    if keyUpEvents[0].key == K_ESCAPE:
        terminate()
    return keyUpEvents[0].key

def getScore(table):
    # to show game over screen
    score=0
    for collem in table:
      for cell in collem:
        score+=cell
    return score

def saveScore(table):
    score=getScore(table)
    f=open("highScore.txt","a")
    f.write(str(score)+"\n")
    f.close()
    #print("Game Over", str(score))

def runGame(TABLE, net=NuralNet(16,make()[1])):
    TABLE=randomfill(TABLE)
    TABLE=randomfill(TABLE)

    running=True
    game=True

    while game:   
        n=netInput(net,TABLE)
        
        #print(n)
        
        big=0
        for y,x in enumerate(n):
          #print(y)
          
          if x>=big:
            if y==0: desired_key = "w"
            if y==1: desired_key = "a"
            if y==2: desired_key = "s"
            if y==3: desired_key = "d"
            big = x
            '''
        y=random.randint(0,3)
        
        if y==0: desired_key = "w"
        if y==1: desired_key = "a"
        if y==2: desired_key = "s"
        if y==3: desired_key = "d"  
'''

        #print(desired_key)
        new_table = key(desired_key, copy.deepcopy(TABLE))
        if new_table != TABLE:
            TABLE=randomfill(new_table)
            #show(TABLE)
        else:
          game=False
          score = getScore(TABLE)

          #showGameOverMessage(TABLE)
        if gameOver(TABLE):
            game=False
            score = getScore(TABLE)

            #showGameOverMessage(TABLE)
    return [score, net]

def key(DIRECTION,TABLE):
    if   DIRECTION =='w':
        for pi in range(1,4):
            for pj in range(4):
                if TABLE[pi][pj] !=0: TABLE=moveup(pi,pj,TABLE)
    elif DIRECTION =='s':
        for pi in range(2,-1,-1):
            for pj in range(4):
                if TABLE[pi][pj] !=0: TABLE=movedown(pi,pj,TABLE)
    elif DIRECTION =='a':
        for pj in range(1,4):
            for pi in range(4):
                if TABLE[pi][pj] !=0: TABLE=moveleft(pi,pj,TABLE)
    elif DIRECTION =='d':
        for pj in range(2,-1,-1):
            for pi in range(4):
                if TABLE[pi][pj] !=0: TABLE=moveright(pi,pj,TABLE)
    return TABLE

def movedown(pi,pj,T):
    justcomb=False
    while pi < 3 and (T[pi+1][pj] == 0 or (T[pi+1][pj] == T[pi][pj] and not justcomb)):
        if T[pi+1][pj] == 0:
            T[pi+1][pj] = T[pi][pj]
        elif T[pi+1][pj]==T[pi][pj]:
            T[pi+1][pj] += T[pi][pj]
            justcomb=True
        T[pi][pj]=0
        pi+=1
    return T

def moveleft(pi,pj,T):
    justcomb=False
    while pj > 0  and (T[pi][pj-1] == 0 or (T[pi][pj-1] == T[pi][pj] and not justcomb)):
        if T[pi][pj-1] == 0:
            T[pi][pj-1] = T[pi][pj]   
        elif T[pi][pj-1]==T[pi][pj]:
            T[pi][pj-1] += T[pi][pj]
            justcomb=True
        T[pi][pj]=0
        pj-=1
    return T

def moveright(pi,pj,T):
    justcomb=False
    while pj < 3 and (T[pi][pj+1] == 0 or (T[pi][pj+1] == T[pi][pj] and not justcomb)):
        if T[pi][pj+1] == 0:
            T[pi][pj+1] = T[pi][pj]
        elif T[pi][pj+1]==T[pi][pj]:
            T[pi][pj+1] += T[pi][pj]
            justcomb=True
        T[pi][pj] = 0
        pj+=1
    return T

def moveup(pi,pj,T):
    justcomb=False
    while pi > 0 and (T[pi-1][pj] == 0 or (T[pi-1][pj] == T[pi][pj] and not justcomb)):
        if T[pi-1][pj] == 0:
            T[pi-1][pj] = T[pi][pj] 
        elif T[pi-1][pj]==T[pi][pj]:
            T[pi-1][pj] += T[pi][pj]
            justcomb=True
        T[pi][pj]=0
        pi-=1
    return T

def leaderboard():
    s = 'to show leaderboard'

def terminate():
    pygame.quit()
    sys.exit()

#main()
