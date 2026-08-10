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
	last3=[]
	TABLE = np.zeros((4, 4), dtype=int)
	TABLE=randomfill(TABLE)
	TABLE=randomfill(TABLE)
	print("starting pygame")
	disp=myPygame()
	print("starting demo")
	oldMT=getMtNumb(TABLE)
	displayTable=TABLE.copy()
	first=True
	targs=[.5,.5,.5,.5, 0, 0, 0, 0, oldMT/16]
	with Live(makeDemoTable(targs, targs), refresh_per_second=10) as live:
		while True:
			disp.FPSCLOCK.tick(FPS)
			disp.update(displayTable)
			displayTable=TABLE.copy()

			if not first:
				while not disp.buttonPressed():
					disp.FPSCLOCK.tick(FPS)

			first=False

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

			targs[-1]=mt/16

			oldMT=mt

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

	

	