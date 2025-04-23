import time
from game import *

def printHighScore():
  f=open("highScore.txt", "r")
  scores=f.read()
  f.close()
  
  scores=list(scores.split('\n'))
  
  highScores=[]
  for score in scores:
    try:
      score=int(score)
    except:
      score=0
    if score>=100:
      highScores+=[score]
  print(highScores)
  
  highest=highScores[0]
  for score in highScores:
      if score>highest:
        highest=[score]
  print(highest)

#printHighScore()
#quit()
TABLE=[[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0]]

a=open("highScore.txt", "r")
b=open("netValues.txt", "r")

scores=list(a.read().split("\n"))
nets=list(b.read().split("\n"))

c=open("gen1Scores.txt", "a")
d=open("gen1Nets.txt", "a")

for i, score in enumerate(scores):
    try:
        if int(score) >= 100:
            pass
            c.write(str(score)+"\n")
            d.write(str(nets[i])+"\n")
    except Exception as e:
        print(score)
        print(e)
#quit()

try:
    main()
except Exception as e:
    print(e)
