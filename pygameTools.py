import pygame, math, sys
#defining the window size and other different specifications of the window
FPS = 5
WINDOWWIDTH = 640
WINDOWHEIGHT = 640
boxsize = min(WINDOWWIDTH,WINDOWHEIGHT)//4;
margin = 5
thickness = 0
#defining the RGB for various colours used
WHITE= (255, 255, 255)
BLACK= (  0,   0,   0)
RED = (255,   0,   0)
GREEN= (  0, 255,   0)
DARKGREEN= (  0, 155,   0)
DARKGRAY= ( 40,  40,  40)
LIGHTSALMON=(255, 160, 122)
ORANGE=(221, 118, 7)
LIGHTORANGE=(227,155,78)
CORAL=(255, 127, 80)
BLUE = (0, 0, 255)
LIGHTBLUE = (0, 0, 150)
colorback=(189,174,158)
colorblank=(205,193,180)
colorlight=(249,246,242)
colordark=(119,110,101)

fontSize=[100,85,70,55,40]

dictcolor1={
0:colorblank,
2:(238,228,218),
4:(237,224,200),
8:(242,177,121),
16:(245,149,99),
32:(246,124,95),
64:(246,95,59),
128:(237,207,114),
256:(237,204,97),
512:(237,200,80),
1024:(237,197,63),
2048:(237,194,46),
4096:(237,190,30),
8192:(239,180,25) }

dictcolor2={
2:colordark,
4:colordark,
8:colorlight,
16:colorlight,
32:colorlight,
64:colorlight,
128:colorlight,
256:colorlight,
512:colorlight,
1024:colorlight,
2048:colorlight,
4096:colorlight,
8192:colorlight }
BGCOLOR = LIGHTORANGE

class myPygame:
    def __init__(self):
        self.pygame = pygame
        self.pygame.init()
        self.screen = self.pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
        self.pygame.display.set_caption('2048')
        self.FPSCLOCK = self.pygame.time.Clock()
        self.pygame.font.init()
        self.BASICFONT = pygame.font.Font('freesansbold.ttf', 18)


    def update(self, TABLE):
        #   showing the table
        self.screen
        self.screen.fill(colorback)
        myfont = pygame.font.SysFont("Arial", 60, bold=True)
        for i in range(4):
            for j in range(4):
                pygame.draw.rect(self.screen, dictcolor1[TABLE[i][j]], (j*boxsize+margin,
                                                i*boxsize+margin,
                                                boxsize-2*margin,
                                                boxsize-2*margin),
                                                thickness)
                if TABLE[i][j] != 0:
                    order=int(math.log10(TABLE[i][j]))
                    myfont = pygame.font.SysFont("Arial", fontSize[order] , bold=True)
                    label = myfont.render("%4s" %(TABLE[i][j]), 1, dictcolor2[TABLE[i][j]] )
                    self.screen.blit(label, (j*boxsize+2*margin, i*boxsize+9*margin))
                    
        pygame.display.update()
    def buttonPressed(self):
        for event in self.pygame.event.get():
            if event.type == self.pygame.QUIT:
                self.pygame.quit()
                sys.exit()
            if event.type == self.pygame.KEYDOWN:
                if event.key == self.pygame.K_SPACE:
                    return True

        return False