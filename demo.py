import pickle, numpy as np

from ai import *
from game import gameOver, getScore, key, randomfill
from pygameTools import FPS, myPygame

with open("scoreNet.txt","rb") as f: scoreNets = pickle.load(f)

nets=[]
for i, scoreNet in enumerate(scoreNets):
    print(f"Score for net {i}: {scoreNet[0]}")
    nets+=[scoreNet[1]]

net=nets[int(input("Which net do you want to test? "))]

def runDemo(net):
	TABLE = np.zeros((4, 4), dtype=int)
	TABLE=randomfill(TABLE)
	TABLE=randomfill(TABLE)
	print("starting pygame")
	disp=myPygame()
	print("starting demo")
	while True:
		n = netInput(net, TABLE)

		indexy=np.argmax(n[:4])
		direction = ["w", "a", "s", "d"][indexy]
		new_table = key(direction, TABLE.copy())

		
		if not np.array_equal(new_table, TABLE):
			TABLE = randomfill(new_table)
		else:
			disp.pygame.quit()
			return "Net made an invalid move, ending demo."
			

		if gameOver(TABLE):
			disp.pygame.quit()
			return getScore(TABLE)
		disp.update(TABLE)
		
		while not disp.buttonPressed():
			disp.FPSCLOCK.tick(FPS)

			
		'''print(
    	"reward:", net.reward,
   		 "move:", direction,
   		 "mtDif:", mtDif
)'''

if __name__ == "__main__":
	score = runDemo(net)
	print("Final Score:", score)
	
	quit()

	

	