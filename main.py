import time, pickle, queue, multiprocessing
from tqdm import tqdm
from game import *
from ai import *
from readScoreNet import *

import time, pickle, multiprocessing
from rich.live import Live
from rich.table import Table


def worker(net, id, outQueue):
	print(f"Worker {id} started")
	while True:
		startTime=time.time()
		result = avrgGame(net)
		runTime=time.time()-startTime
		outQueue.put((id, result, runTime))
		net=result[1]
		#print(f"\n\n\n\nNet {id}:\n\tAverage Percent Error: {result[2]}\n\tAverage Score: {result[0]}\n")


def buildTable(netStats, lastRuntime, lastUpdateTime):

	table = Table()

	table.add_column("Net")
	table.add_column("Score")
	table.add_column("Error")
	table.add_column("Runtime")
	table.add_column("Last Seen")

	for index, stat in enumerate(netStats):

		if stat is None:

			table.add_row(
				str(index),
				"-",
				"-",
				"-",
				"never"
			)

		else:

			timeSince = time.time() - lastUpdateTime[index]

			table.add_row(
				str(index),
				str(stat[0]),
				str(stat[2]),
				f"{lastRuntime[index]:.1f}s",
				f"{timeSince:.1f}s ago"
			)

	return table


if __name__ == "__main__":

	nets=[]
	#nets=genNewNets(4)

	outputQueue = multiprocessing.Queue()

	print("\nLoading Nets")

	with open("scoreNet.txt","rb") as f: scoreNets = pickle.load(f)

	nets=[]
	for scoreNet in scoreNets:
		nets+=[scoreNet[1]]

	proccesses=[]

	print("Building Proccesses")

	for i, net in enumerate(nets):

		proccesses += [multiprocessing.Process(target=worker, args=(net, i, outputQueue))]
		proccesses[-1].start()
		
	n = 0
	runTime=[0,0,0,0]
	lastUpdateTime=[time.time(), time.time(), time.time(), time.time()]

	with Live(buildTable(scoreNets, runTime, lastUpdateTime), refresh_per_second=4) as live:

		

		while True:
			try:
				id, thisScoreNet, thisRunTime = outputQueue.get(timeout=.1)
				n += 1

				runTime[id] = thisRunTime
				lastUpdateTime[id] = time.time()

				nets[id] = thisScoreNet[1]
				scoreNets[id] = thisScoreNet
				

				if n == len(scoreNets):

					with open("scoreNet.txt", "wb") as f:
						pickle.dump(scoreNets, f)

					n = 0
			except queue.Empty:
				pass

			live.update(buildTable(scoreNets, runTime, lastUpdateTime))
			

