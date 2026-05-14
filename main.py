import time, pickle, queue
from tqdm import tqdm
from game import *
from ai import *
from readScoreNet import *


def worker(net, id):
	while True:
		result = avrgGame(net)
		resultQueue.put((id, result))
		net=result[1]



if __name__ == "__main__":

	TABLE=[[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0]]

	nets=[]
	#nets=genNewNets(4)

	resultQueue = queue.Queue()

	
	

	it=0
	while True:
		
		
		print("\nLoading Generated Nets")
	
		nets=pickle.load(open("nets.txt","rb"))
		
		scoreNet=[]
		
		print("\nRunning Nets")
		
		
		for i, net in enumerate(tqdm(nets)):

			scoreNet += [avrgGame(net)]   
			
			net=scoreNet[-1][1]

			if i%1000==0:
				#sleep(3)
				pass
		
		
		print("\nSaving SCORE NETS")
		pickle.dump(scoreNet, open("scoreNet.txt","wb"))

		print("\nSaving Nets")
		pickle.dump(nets, open("nets.txt","wb"))
		

		print("\033[H\033[2J", end="")
		

		strin="\nScores: "

		for score in scoreNet: strin+= f"{score[0]}, "
		strin+="\nPercent Errors: "
		for score in scoreNet: strin+= f"{score[2]}, "

		print(strin)

		it+=1
		
		print(f"Itterations: {it}")

