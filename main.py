import os
import time, pickle, queue, multiprocessing, traceback
from game import *
from ai import *
from readScoreNet import *

from rich.live import Live
from rich.table import Table
from rich.panel import Panel
from rich.layout import Layout


def worker(netSave, id, outQueue, logQueue, scoreUpdates, highScores):
	logQueue.put((id, "INFO", f"Worker {id} started"))
	while True:
		try:
			startTime=time.time()
			netSave = avrgGame(netSave, logQueue, scoreUpdates, highScores, id)
			runTime=time.time()-startTime
			outQueue.put((id, netSave, runTime))

		except Exception as e:
			logQueue.put((id, "ERROR", f"{e}\n{traceback.format_exc()}"))


def buildTable(netSaves, lastRuntime, lastUpdateTime):

	table = Table()

	table.add_column("Net")
	table.add_column("Score")
	table.add_column("Delta")
	table.add_column("Error")
	table.add_column("Delta")
	table.add_column("Valid Dif")
	table.add_column("% Invalid")
	table.add_column("Runtime")
	table.add_column("Last Seen")

	for index, save in enumerate(netSaves):
		timeSince = time.time() - lastUpdateTime[index]

		table.add_row(
			str(index),
			str(round(save.avgScore, 3)),
			str(round(save.scoreDeltaTrend, 3)),
			str(round(save.error, 4)),
			str(round(save.errorDeltaTrend, 5)),
			str(round(save.validDif, 4)),
			str(round(save.percentInvalid, 2)) + "%",
			f"{lastRuntime[index]:.1f}s",
			f"{timeSince:.1f}s ago"
		)

	return table

def round(num, digits):
	return int(num*(10**digits))/(10**digits)

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
	fullLogs = ""
	maxLogs = 10

	outputQueue = multiprocessing.Queue()

	coreNumb = min(4, os.cpu_count()-1)

	scoreUpdates = multiprocessing.Queue()
	highScores = multiprocessing.Array('i', [0] * coreNumb)
	scoreUpdateList = []

	makeNewNets = False

	if not makeNewNets:
		print("\nLoading Nets")

		with open("netSaves.pkl","rb") as f: netSaves = pickle.load(f)

		nets=[]
		newNetSaves=[]
		for i, save in enumerate(netSaves):
			newNetSaves += [netSave(save.net, save.stage, save.avgScore, save.error, save.highScore, save.validDif, save.percentInvalid)]
			nets += [save.net]
			highScores[i] = save.highScore

		netSaves = newNetSaves
		del newNetSaves


	else:
		nets=genNewNets(coreNumb)
		netSaves=[netSave(net) for net in nets]

	print("Building Proccesses")
	proccesses=[]


	for save in netSaves:
		i=netSaves.index(save)
		proccesses += [multiprocessing.Process(target=worker, args=(save, i, outputQueue, logQueue, scoreUpdates, highScores))]
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
				id, thisNetSave, thisRunTime = outputQueue.get(timeout=.1)
				n += 1

				runTime[id] = thisRunTime
				lastUpdateTime[id] = time.time()

				nets[id] = thisNetSave.net
				netSaves[id] = thisNetSave

				if n == len(netSaves):

					with open("netSaves.pkl", "wb") as f:
						pickle.dump(netSaves, f)

					n = 0
			except queue.Empty:
				pass
			try:
				msg = logQueue.get_nowait()

				logs.append([msg, getTime()])
				fullLogs += f"{getTime()}: [{msg[1]}] Net {msg[0]}: {msg[2]}\n"

				with open("logs.txt", "w") as f:
					f.write(fullLogs)

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

			
			layout["table"].update(buildTable(netSaves, runTime, lastUpdateTime))
			layout["logs"].update(buildLogs(logs))
			layout["highScores"].update(buildHighScores(scoreUpdateList, logQueue, highScores))

			live.update(layout)

			

