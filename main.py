import time, pickle
from tqdm import tqdm
from game import *
from ai import *
from readScoreNet import *

if __name__ == "__main__":

	TABLE=[[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0]]

	nets=[]

	
	#simGameNumb=int(input("Enter number of games to be simulated: "))

	'''	
	simGameNumb = 10

	print("\nGenerating Nets")
	for i in tqdm(range(simGameNumb)):
		nets+=[NuralNet(16,make()[1])]

	pickle.dump(nets, open("nets.txt","wb"))
	#'''

	it=0
	while True:
		main()
		sn=loadScoreNets()

		strin="\nScores: "

		for score in sn: strin+=f"{score[0]}, "
		print(strin)

		it+=1
		
		print(f"Itterations: {it}")

