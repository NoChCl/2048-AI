import pickle, numpy as np, math

from ai import *
from game import directionIsValid, gameOver, getMtNumb, getScore, key, randomfill
from pygameTools import FPS, myPygame

def getStrFromNumbList(li):
	string=""
	for item in li:
		string+=f"{int(item*100)/100}, "
	return string


def runDemo(net):
	TABLE = np.zeros((4, 4), dtype=int)
	TABLE=randomfill(TABLE)
	TABLE=randomfill(TABLE)
	print("starting pygame")
	disp=myPygame()
	print("starting demo")
	oldMT=getMtNumb(TABLE)
	while True:
		disp.FPSCLOCK.tick(FPS)
		disp.update(TABLE)
		
		while not disp.buttonPressed():
			disp.FPSCLOCK.tick(FPS)




		n = netInput(net, TABLE)

		indexy=np.argmax(n[:4])
		direction = ["w", "a", "s", "d"][indexy]
		new_table = key(direction, TABLE.copy())



		mt=getMtNumb(new_table)
		mtDif=mt-oldMT
		oldMT=mt
		targs=[.5,.5,.5,.5, 0, 0, 0, 0, mt/16]
		
		if mtDif<0:
			net.reward=-.5/6.5
		else:
			net.reward=(((mtDif+1)**1.25)-.5)/6.5

		net.reward+=(mt-1)/160
		for i, d in enumerate(["w", "a", "s", "d"]):
			if directionIsValid(d, TABLE):
				targs[i+4]=1



		disp.update(TABLE)
		if not np.array_equal(new_table, TABLE):
			TABLE = randomfill(new_table)
			net.reward+=.05
		else:
			net.reward-=.8
			disp.pygame.quit()
			return "Net made an invalid move, ending demo."
			

		if gameOver(TABLE):
			disp.pygame.quit()
			return getScore(TABLE)
		
		targs[indexy]+=maxMin(net.reward)

		print(f"Targets: {getStrFromNumbList(targs)}\nOutput: {getStrFromNumbList(n)}"
		)
			
		'''print(
    	"reward:", net.reward,
   		 "move:", direction,
   		 "mtDif:", mtDif
)'''

if __name__ == "__main__":
	while True:
		try:
			with open("scoreNet.txt","rb") as f: scoreNets = pickle.load(f)
			nets=[]
			for i, scoreNet in enumerate(scoreNets):
				print(f"Score for net {i}: {scoreNet[0]}")
				nets+=[scoreNet[1]]
			netIndex = int(input("Which net do you want to test? "))
			net = nets[netIndex]
		except (ValueError, IndexError):
			print("Invalid input. Please enter a valid net index.")
		
		score = runDemo(net)
		print("Final Score:", score)
		
	quit()

	

	