import pickle, numpy as np, math

from ai import *
from game import directionIsValid, gameOver, getMtNumb, getScore, getTargs, key, randomfill
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


			n, net = netInput(net, TABLE)

			i=np.argmax(n[:4])

			targs=getTargs(TABLE, 10)

			
			direction = LETTERS[i]
			new_table = key(direction, TABLE.copy())


			if not np.array_equal(new_table, TABLE):
				TABLE = randomfill(new_table)

				iterations += 1
				
			else:
				disp.pygame.quit()
				return "Net made an invalid move, ending demo."
				

			if gameOver(TABLE):
				disp.pygame.quit()
				return getScore(TABLE)


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

	

	