import random, math
from tqdm import tqdm


class Nuron():
        def __init__(self, weights, bias):
                self.inputNumb=len(weights)
                self.weights=weights
                self.bias=bias
                self.output=0
                
                self.lastInputs = []
                self.rawOutput = 0
                self.output = 0
                self.error = 0


        def update(self, vals):
                self.lastInputs = vals

                self.rawOutput=0
                for i in range(self.inputNumb):
                        a=vals[i]
                        w=self.weights[i]
                        self.rawOutput+=a*w
                #print(self.output)
                self.rawOutput+=self.bias
                self.output=sigmoid(self.rawOutput)
                return self.output

        def train(self, targ, lr):
              error=targ-self.output

              for i in range(self.inputNumb):
                    self.weights[i]+=lr*error*self.lastInputs[i]
              self.bias+=lr*error


class NuralNet():
        def __init__(self, inputNumb, otherLayers):
                self.reward=0
                self.inputNumb=inputNumb
                self.otherLayers=otherLayers
                self.numbLayers=len(otherLayers)
                
                self.outputs=[]
                
                self.nurons=[]
                for layer in self.otherLayers:
                        thislayer=[]
                        for nuron in layer:
                                thislayer+=[Nuron(nuron[0], nuron[1])]
                        self.nurons+=[thislayer]
                
                
        def update(self,inputs):
                self.outputs=[]
                for i,layer in enumerate(self.nurons):
                        layerOuts=[]
                        for nuron in layer:
                                if i ==0:
                                        nuron.update(inputs)
                                else:
                                        nuron.update(self.outputs[i-1])
                                layerOuts+=[nuron.output]
                        self.outputs+=[layerOuts]

        def trianOutLayer(self, targs, lr):
              
              outLayer=self.nurons[-1]

              for i, nuron in enumerate(outLayer):
                    nuron.train(targs[i], lr)
              self.reward=0
                        
class AI():
  def __init__(self):
    self.score=0
  def giveScore(self, score):
    self.score+=score
    
def maxMin(targ):
      return max(-.5, min(.5, targ))

def sigmoid(n):
        return 1/(1+(math.e**-n))
def sigmoidDeriv(x):
    s = sigmoid(x)
    return s * (1 - s)
                        

def netInput(myNet,t):
  ins =[]
  for row in t:
    for cell in row:
      if cell == 0:
        ins+=[0]
      else:
        ins+=[math.log(cell, 2)]
  

  myNet.update(ins)
  
  
  #print(myNet.outputs[-1])
  return handelNetOut(myNet)

def handelNetOut(myNet):
        output=myNet.outputs[-1]
        if myNet.outputs[-1][0]==myNet.outputs[-1][1]==myNet.outputs[-1][2]==myNet.outputs[-1][3]:
                output[random.randint(0,3)]=2
        return output


def generateWeights(count):
        weightRange = (-100, 100)
        output=[]
        
        for i in range(count):
                output += [random.randint(*weightRange)/100]
        return output

def generateNeuron(inputCount):
        weightRange = (-100, 100)
        
        return [generateWeights(inputCount), random.randint(*weightRange)/100]

def make():
    inputCount = 16
        
        #generate first layer, with inputCount weights, 32 total
    firstLayer = [generateNeuron(inputCount) for _ in range(32)]
    
    #generate first layer, with inputCount weights, 2 total
    secondLayer = [generateNeuron(32) for _ in range(32)]
    
    #generate last layer, with 2 weights, 4 total
    outputLayer = [generateNeuron(32) for _ in range(9)]

    otherLayers = [firstLayer, secondLayer, outputLayer]
    return inputCount, otherLayers


def genNewNets(netNumb):
        nets=[]
        print("\nGenerating Nets")
        for i in tqdm(range(netNumb)):
                nets+=[NuralNet(16,make()[1])]

        return nets