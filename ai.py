import random, math

class Nuron():
        def __init__(self, weights, bias):
                self.inputNumb=len(weights)
                self.weights=weights
                self.bias=bias
                self.output=0
        def update(self,vals):
                self.output=0
                for i in range(self.inputNumb):
                        a=vals[i]
                        w=self.weights[i]
                        self.output+=a*w
                #print(self.output)
                self.output+=self.bias
                self.output=sigmoid(self.output)
                return self.output
class NuralNet():
        def __init__(self, inputNumb, otherLayers):
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
                        
class AI():
  def __iniit__(self):
    self.score=0
  def giveScore(self, score):
    self.score+=score
    


def sigmoid(n):
        return 1/(1+(math.e**n))
                        

def netInput(myNet,t):
  ins =[]
  for row in t:
    for cell in row:
      ins+=[cell]
  

  myNet.update(ins)
  output=myNet.outputs[-1]
  if myNet.outputs[-1][0]==myNet.outputs[-1][1]==myNet.outputs[-1][2]==myNet.outputs[-1][3]:
    output[random.randint(0,3)]=2
  
  #print(myNet.outputs[-1])
  return output
def make():
    inputs=16
    firstLayer=[[[random.randint(-10,10),random.randint(-10,10),random.randint(-10,10),random.randint(-10,10),random.randint(-10,10),random.randint(-10,10),random.randint(-10,10),random.randint(-10,10),random.randint(-10,10),random.randint(-10,10),random.randint(-10,10),random.randint(-10,10),random.randint(-10,10),random.randint(-10,10),random.randint(-10,10),random.randint(-10,10)],20],[[random.randint(-10,10),random.randint(-10,10),random.randint(-10,10),random.randint(-10,10),random.randint(-10,10),random.randint(-10,10),random.randint(-10,10),random.randint(-10,10),random.randint(-10,10),random.randint(-10,10),random.randint(-10,10),random.randint(-10,10),random.randint(-10,10),random.randint(-10,10),random.randint(-10,10),random.randint(-10,10)],random.randint(-10,10)]]
    
    outputs=[[[random.randint(-10,10),random.randint(-10,10)],random.randint(-10,10)], [[random.randint(-10,10),random.randint(-10,10)],random.randint(-10,10)],[[random.randint(-10,10),random.randint(-10,10)],random.randint(-10,10)],[[random.randint(-10,10),random.randint(-10,10)],random.randint(-10,10)]]
    otherLayers=[firstLayer, outputs]
    output=inputs, otherLayers
    #f=open("nets.txt","a")
    #f.write(str(outputs)+"\n")
    #f.close()
    return output



