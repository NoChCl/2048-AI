import pickle, numpy as np, math

from ai import *
from game import directionIsValid, gameOver, getMtNumb, getScore, key, randomfill
from pygameTools import FPS, myPygame
from rich.table import Table
from rich.console import Console
from rich.live import Live

def getStrFromNumbList(li):
	string=""
	for item in li:
		string+=f"{int(item*100)/100}, "
	return string

def makeDemoTable(targs, actual):
	table = Table()

	table.add_column("")
	table.add_column("W")
	table.add_column("A")
	table.add_column("S")
	table.add_column("D")
	table.add_column("W-Valid")
	table.add_column("A-Valid")
	table.add_column("S-Valid")
	table.add_column("D-Valid")
	table.add_column("MT/16")

	table.add_row("TARGET", *[f"{x:.3f}" for x in targs])
	table.add_row("ACTUAL", *[f"{x:.3f}" for x in actual])

	return table

def runDemo(net):
	LETTERS=["w","a","s","d"]
	TABLE = np.zeros((4, 4), dtype=int)
	TABLE=randomfill(TABLE)
	TABLE=randomfill(TABLE)
	print("starting pygame")
	disp=myPygame()
	print("starting demo")
	displayTable=TABLE.copy()
	targs=[.5,.5,.5,.5, 0, 0, 0, 0, 0]
	iterations=1
	with Live(makeDemoTable(targs, targs), refresh_per_second=10) as live:
		while True:
			disp.FPSCLOCK.tick(FPS)
			disp.update(displayTable)
			displayTable=TABLE.copy()

			if iterations != 1:
				while not disp.buttonPressed():
					disp.FPSCLOCK.tick(FPS)


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

					validSecondaries=0
					for x, d in enumerate(["w", "a", "s", "d"]):
						if directionIsValid(d, TABLE):
							validSecondaries+=1
					if validSecondaries == 0:
						net.reward=-.2
					net.reward+=.1*validSecondaries
					
				else:
					net.reward-=.5
					if i == realI:
						disp.pygame.quit()
						return "Net made an invalid move, ending demo."
					

				if gameOver(TABLE):
					net.reward-=.25
					if i == realI:
						disp.pygame.quit()
						return getScore(TABLE)

				targs[i]+=maxMin(net.reward)



			for x, d in enumerate(["w", "a", "s", "d"]):
				if directionIsValid(d, trueTable):
					targs[x+4]=1
				else:
					targs[x]=0

			live.update(makeDemoTable(targs, n))
				


if __name__ == "__main__":
	console = Console()
	while True:
		try:
			with open("scoreNet.pkl","rb") as f: scoreNets = pickle.load(f)
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

	

	