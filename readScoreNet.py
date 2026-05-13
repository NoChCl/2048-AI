import pickle
from tqdm import tqdm





def loadScoreNets():
	print("Loading SCORE NETS")

	scoreNets = pickle.load(open("scoreNet.txt","rb"))

	return scoreNets

def printTop2(scoreNets):
	top2=[scoreNets[0],[0,0]]

	errors=[]

	print("\nFinding best SCORE NETS")
	for scoreNet in tqdm(scoreNets):
		if scoreNet[0]>top2[0][0]:
			top2[1]=top2[0]
			top2[0]=scoreNet


	print(top2)


if __name__ == "__main__":
	printTop2(loadScoreNets())
	
