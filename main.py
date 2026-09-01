import os
import time, pickle, queue, multiprocessing
from tqdm import tqdm
from game import *
from ai import *
from readScoreNet import *

from rich.live import Live
from rich.table import Table
from rich.panel import Panel
from rich.layout import Layout


def worker(net, id, outQueue, logQueue, scoreUpdates, highScores):
	logQueue.put((id, "INFO", f"Worker {id} started"))
	while True:
		try:
			startTime=time.time()
			result = avrgGame(net, logQueue, scoreUpdates, highScores, id)
			runTime=time.time()-startTime
			outQueue.put((id, result, runTime))
			net=result[1]
		except Exception as e:
			logQueue.put((id, "ERROR", str(e)))


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

def buildHighScores(logs, logQueue, highScores):

	for entry in logs:
		id, score = entry[0]
		if score > highScores[id]:
			
			highScores[id] = score
			logQueue.put((id, "INFO", f"Updated High Score for Net {id}"))
	text=""
	for index, score in enumerate(highScores):
		text += f"Net {index}, High Score: {score}\n"
		
	return Panel(text, title="High Scores")


def buildLogs(logs):

	text = ""

	for entry in logs:

		id, level, msg = entry[0]

		text += f"{entry[1]}: [{level}] Net {id}: {msg}\n"

	return Panel(text, title="Logs")

def getTime():
	return time.strftime("%H:%M:%S", time.localtime()) + f".{int((time.time() % 1) * 1000):03d}"

if __name__ == "__main__":

	nets=[]
	
	logQueue = multiprocessing.Queue()
	logs = []
	maxLogs = 10

	outputQueue = multiprocessing.Queue()

	scoreUpdates = multiprocessing.Queue()
	highScores = multiprocessing.Array('i', [0, 0, 0, 0])
	scoreUpdateList = []

	coreNumb = min(4, os.cpu_count()-1)

	makeNewNets = False

	if not makeNewNets:
		print("\nLoading Nets")

		with open("scoreNet.pkl","rb") as f: scoreNets = pickle.load(f)

		nets=[]
		for scoreNet in scoreNets:
			nets+=[scoreNet[1]]

	else:
		nets=genNewNets(coreNumb)
		scoreNets=[[0, net, 100] for net in nets]

	print("Building Proccesses")
	proccesses=[]



	for i, net in enumerate(nets):
		proccesses += [multiprocessing.Process(target=worker, args=(net, i, outputQueue, logQueue, scoreUpdates, highScores))]
		if i < coreNumb:
			proccesses[-1].start()


	n = 0
	runTime=[0,0,0,0]
	lastUpdateTime=[time.time(), time.time(), time.time(), time.time()]

	layout = Layout()

	layout.split_column(
		Layout(name="table", size=8),
		Layout(name="highScores"),
		Layout(name="logs", size=10)

	)

	



	with Live(layout, refresh_per_second=4) as live:


		while True:
			try:
				id, thisScoreNet, thisRunTime = outputQueue.get(timeout=.1)
				n += 1

				runTime[id] = thisRunTime
				lastUpdateTime[id] = time.time()

				nets[id] = thisScoreNet[1]
				scoreNets[id] = thisScoreNet
				

				if n == len(scoreNets):

					with open("scoreNet.pkl", "wb") as f:
						pickle.dump(scoreNets, f)

					n = 0
			except queue.Empty:
				pass
			try:
				msg = logQueue.get_nowait()

				logs.append([msg, getTime()])

				if len(logs) > maxLogs:
					logs.pop(0)

			except queue.Empty:
				pass

			try:
				msg = scoreUpdates.get_nowait()

				scoreUpdateList.append([msg, getTime()])

				if len(scoreUpdateList) > maxLogs:
					scoreUpdateList.pop(0)

			except queue.Empty:
				pass

			
			layout["table"].update(buildTable(scoreNets, runTime, lastUpdateTime))
			layout["logs"].update(buildLogs(logs))
			layout["highScores"].update(buildHighScores(scoreUpdateList, logQueue, highScores))

			live.update(layout)

			

