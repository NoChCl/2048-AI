import time, pickle
from tqdm import tqdm
from game import *
from ai import *

if __name__ == "__main__":

	TABLE=[[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0]]

	nets=[]

	simGameNumb=int(input("Enter number of games to be simulated: "))

	print("\nGenerating Nets")
	for i in tqdm(range(simGameNumb)):
		nets+=[NuralNet(16,make()[1])]

	pickle.dump(nets, open("nets.txt","wb"))


	main()
