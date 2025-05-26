import pickle
from tqdm import tqdm

print("Loading SCORE NETS")

scoreNets = pickle.load(open("scoreNet.txt","rb"))

top2=[scoreNets[0],[0,0]]

errors=[]

print("\nFinding best SCORE NETS")
for scoreNet in tqdm(scoreNets):
	if scoreNet[0]>top2[0][0]:
		top2[1]=top2[0]
		top2[0]=scoreNet


print(top2)
