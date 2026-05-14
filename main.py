import time, pickle, queue, multiprocessing
from tqdm import tqdm
from game import *
from ai import *
from readScoreNet import *


def worker(net, id, queue):
	while True:
		result = avrgGame(net, id)
		queue.put((id, result))
		net=result[1]
		print(f"Net {id}:\n\tAverage Percent Error: {result[2]}\n\tAverage Score: {result[0]}\n")



if __name__ == "__main__":

	TABLE=[[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0]]

	nets=[]
	#nets=genNewNets(4)

	queue = multiprocessing.Queue()

	print("\nLoading Generated Nets")

	nets=pickle.load(open("nets.txt","rb"))
	
	scoreNet = [None] * len(nets)
	
	print("\nRunning Nets")

	proccesses=[]

	for i, net in enumerate(tqdm(nets)):

		proccesses += [multiprocessing.Process(target=worker, args=(net, i, queue))]
		proccesses[-1].start()
		

	n=0
	while True:
		
		id, thisScoreNet=queue.get()
		n+=1

		nets[id]=thisScoreNet[1]

		scoreNet[id]=thisScoreNet
		if n==4:
			print("\nSaving SCORE NETS")
			with open("scoreNet.txt","wb") as f: pickle.dump(scoreNet, f)
			
			print("\nSaving Nets")
			with open("nets.txt","wb") as f: pickle.dump(nets, f)
			
			n=0

		

