import pygame
from random import randint,choice
from time import sleep
pygame.init()    #Initialize necessary libraries

WIDTH,HEIGHT = 800,600
screen = pygame.display.set_mode((WIDTH,HEIGHT))   #Set screen width and height
gameFont = pygame.font.Font(None,25)
titleFont = pygame.font.Font(None,80)  #Create fonts for game
tick = 0

searchIcon = pygame.image.load("Images/searchIcon.png")
searchIcon = pygame.transform.scale(searchIcon,(20,20))

fireAnimation = []  #Store fireAnimation frames

for i in range(0,65):
    frame = pygame.image.load(f"Images/frame_{i}_delay-0.02s.png")
    frame = pygame.transform.scale(frame,(30,30))
    fireAnimation.append(frame)    #Loads each frame, transforms it to the correct size and 

# shotList, sinkList, missList, hitList and shipsList for both the enemy and player are two dimensional lists that correspond to each other:
# Each item corresponds to row number and the number after corresponds to column number:
# [[R1C1,R1C2,R1C3,R1C4],
# [R2C1,R2C2,R2C3,R2C4]] and so on and it confirms something
# For example, if R1C4 is True in missList, a red X will show over that square


playerShipsList = [[False for x in range(10)] for y in range(10)]   #Stores what tiles hold a player Ship
playerShipUnits = [[] for y in range(4)]   #List to prevent ships stacking on top of each other
enemyShipsList = [[False for x in range(10)] for y in range(10)]  #Stores what tiles hold an enemy Ship
enemyShipUnits = [[] for y in range(4)]    #List to prevent ships stacking on top of each other

playerShotList = [[False for x in range(10)] for y in range(10)] #Stores what tiles the player has already shot
playerMissList = [[False for x in range(10)] for y in range(10)] #Stores what tiles the player has shot and missed
playerHitList = [[False for x in range(10)] for y in range(10)] #Stores what tiles the player has shot and hit
enemyShotList = [[False for x in range(10)] for y in range(10)] #Stores what tiles the enemy has already show
enemyMissList = [[False for x in range(10)] for y in range(10)] #Stores what tiles the enemy has shot and missed
enemyHitList = [[False for x in range(10)] for y in range(10)] #Stores what tiles the enemy has shot and hit

enemyShipsSunk = [[False for x in range(10)] for y in range(10)] #Stores if any ship on that position is sunk to give it the right colour for the player
playerShipsSunk = [[False for x in range(10)] for y in range(10)] #Stores if any ship on that position is sunk to give it the right colour for the enemy

class Button:
    def __init__(self,xPos:int,yPos:int,text:str,textColor,buttonColor,colorOnClick,borderColor,width:int,height:int):
        self.xPos = xPos
        self.yPos = yPos
        self.text = text
        self.textColor = textColor
        self.buttonColor = buttonColor
        self.colorOnClick = colorOnClick
        self.borderColor = borderColor
        self.width = width
        self.height = height  #Initialize necessary variables

    def drawSelf(self):
        buttonText = gameFont.render(self.text,True,self.textColor)  #Render button font
        rectangleDim = pygame.Rect(self.xPos,self.yPos,self.width,self.height)  #Create a rectangle for the button
        mousePos = pygame.mouse.get_pos()
        if rectangleDim.collidepoint(mousePos):
            pygame.draw.rect(screen,self.colorOnClick,rectangleDim,0,3)  #If the mouse is hovering over button, give it a different colour
        else:
            pygame.draw.rect(screen,self.buttonColor,rectangleDim,0,3)
        pygame.draw.rect(screen,self.borderColor,rectangleDim,2,3)  #Give it a border
        textRect = buttonText.get_rect(center=rectangleDim.center) 
        screen.blit(buttonText,textRect.topleft)   #Blit in the text

    def checkForClick(self):
        mousePos = pygame.mouse.get_pos()
        rectangleDim = pygame.Rect(self.xPos,self.yPos,self.width,self.height)
        leftClick = pygame.mouse.get_pressed()[0]
        if leftClick and rectangleDim.collidepoint(mousePos):  #Check if mouse pressed and if mouse collides with the dimensions of the button
            return True
        else:
            return False

class ButtonGroup:   #Defines a buttonGroup Class
    def __init__(self,x:int,y:int,widthUnit:int,heightUnit:int,width:int,height:int,selectable:bool): #Initializes class attributes
        self.x = x
        self.y = y
        self.widthUnit = widthUnit  #Width of each square
        self.heightUnit = heightUnit  #Height of each square
        self.width = width  #Width of total grid
        self.height = height #Height of total grid
        self.selectable = selectable  #If grid is selectable (enemy vs player grid)
        self.xLines = self.width//self.widthUnit  #Number of horizontal lines to draw
        self.xIncrement = self.width//self.xLines  #Distance between each line
        self.yLines = self.height//self.heightUnit  #Number of vertical lines to draw
        self.yIncrement = self.height//self.yLines  #Distance between each line
        self.selectedX, self.selectedY = None,None  #Holds selected square information
        self.shipsSunk = 0  #Checks how many ships sunk
        global playerShipsList
        global enemyShipsList
        global playerShotList
        global enemyShotList
        global enemyShipUnits
        global playerShipUnits
        global enemyShipsSunk
        global playerShipsSunk
        global tick
        global fireAnimation
        self.rectanglesList = [[0 for j in range(self.yLines)] for i in range(self.xLines)]  #Stores the rect values for each tile
        for lineNumberY in range(0,self.yLines):
            for lineNumberX in range(0,self.xLines):
                self.rectanglesList[lineNumberY][lineNumberX] = pygame.Rect((self.x+(self.xIncrement*lineNumberX)+1.5),(self.y+(self.yIncrement*lineNumberY)+1.5),self.xIncrement,self.yIncrement)
                
    def checkKills(self,user=0):
        newShipSunk = False
        shipSunk = None
        numShipSunk = 0
        if user == 0:  #If checking kills for user 0 (player)
            # Iterate over each ship's unit in enemyShipUnits
            for shipIndex, ship in enumerate(enemyShipUnits):
                allHit = True
                for coord in ship:
                    if not(playerHitList[coord[0]][coord[1]]):  # Check all parts are hit
                        allHit = False
                        break 

                if allHit:  #Check if ship sunk and set ShipSunk to the index of ship
                    shipSunk = shipIndex
                    numShipSunk += 1

                if shipSunk != None:  #Flags enemy ships sunk for each square of the ship sunk
                    for thing in enemyShipUnits[shipSunk]:
                        if not(enemyShipsSunk[thing[0]][thing[1]]):
                            newShipSunk = True
                            enemyShipsSunk[thing[0]][thing[1]] = True
        
        if user == 1:  #If checking kills for user 1 (computer)
            # Iterate over each ship's unit in playerShipUnits
            for shipIndex, ship in enumerate(playerShipUnits):
                allHit = True
                for coord in ship:
                    if not(enemyHitList[coord[0]][coord[1]]):  # Check all parts are hit
                        allHit = False
                        break 

                if allHit:  #Check if ship sunk and set ShipSunk to the index of ship
                    shipSunk = shipIndex
                    numShipSunk += 1

                if shipSunk != None:  #Flags enemy ships sunk for each square of the ship sunk
                    for thing in playerShipUnits[shipSunk]:
                        if not(playerShipsSunk[thing[0]][thing[1]]):
                            newShipSunk = True
                            playerShipsSunk[thing[0]][thing[1]] = True
            return newShipSunk

    def drawSelf(self):  #Draw Self function
        mousePos = pygame.mouse.get_pos()
        for i,thing in enumerate(self.rectanglesList):
            for j,thing2 in enumerate(thing):
                if thing2.collidepoint(mousePos):      #Checks current grid square moused over
                    pygame.draw.rect(screen,(180,215,255),thing2)  #Makes it appear lighter than other squares
                    if pygame.mouse.get_pressed()[0]:
                        if not(playerShotList[i][j]):
                            self.selectedX = self.rectanglesList.index(thing)
                            self.selectedY = thing.index(thing2)
                                
                else:
                    pygame.draw.rect(screen,(0,119,190),thing2)
                
                if not(self.selectable) and playerShipsList[i][j]:    #Colours player ship a different colour
                    pygame.draw.rect(screen,(255,0,255),thing2,0,15)

                if (playerMissList[i][j] and self.selectable) or (enemyMissList[i][j] and not(self.selectable)):  #If grid square in list of missed squares
                    pygame.draw.line(screen,"red",thing2.topleft,thing2.bottomright,5)  #Draw Red X over square
                    pygame.draw.line(screen,"red",thing2.bottomleft,thing2.topright,5)
                
                elif (enemyShipsSunk[i][j] and self.selectable) or (playerShipsSunk[i][j] and not(self.selectable)):   #Sunk by player or enemy
                    pygame.draw.rect(screen,(47,58,100),thing2,0,15)  #Draw gray square to show sunken ship 

                elif (playerHitList[i][j] and self.selectable) or (enemyHitList[i][j] and not(self.selectable)): #If grid square in list of hit sqaures
                    screen.blit(fireAnimation[(tick//10)%65],(thing2.topleft[0],thing2.topleft[1]-3))  #Blit current fire frame as an animation

                try:
                    if (self.rectanglesList[self.selectedX][self.selectedY] == thing2 and self.selectable):  #If grid square has been selected
                        pygame.draw.circle(screen,"red",thing2.center,(self.widthUnit/3),4)
                        pygame.draw.circle(screen,"red",thing2.center,(self.widthUnit/25))  #Draw target circles

                        rightRect = pygame.Rect(thing2.center[0]+3,thing2.center[1]-1.5,10,3)
                        topRect = pygame.Rect(thing2.center[0]-1.5,thing2.center[1]-13 ,3,10)
                        leftRect = pygame.Rect(thing2.center[0]-13,thing2.center[1]-1.5,10,3)
                        bottomRect = pygame.Rect(thing2.center[0]-1.5,thing2.center[1]+3,3,10)

                        pygame.draw.rect(screen,"red",rightRect)
                        pygame.draw.rect(screen,"red",topRect)
                        pygame.draw.rect(screen,"red",leftRect)
                        pygame.draw.rect(screen,"red",bottomRect)   #Draw 4 rectangles, with one on each side
                except:  #Prevent errors when no square selected
                    continue

                
                    

        for xLine in range(0,int(self.xLines)+1):
            pygame.draw.line(screen,"black",(self.x,(self.y+(xLine*self.yIncrement))),(self.x+self.width,(self.y+(xLine*self.yIncrement))),3)
                #Create a certain amount of horizontal lines for the grid
        for yLine in range(0,int(self.yLines)+1):
            pygame.draw.line(screen,"black",((self.x+(yLine*self.xIncrement)),self.y),((self.x+(yLine*self.xIncrement)),self.y+self.height),3)
                #Create a certain amount of vertical lines for the grid

    def select(self,selectedX,selectedY): #Changes selected square
        self.selectedX = selectedX
        self.selectedY = selectedY
    
    def returnSelected(self):   #Returns True if a square is selected and False if no square is selected
        if self.selectable:  
            if (self.selectedX != None) and (self.selectedY != None):
                return True
            return False
        return False
    
    def guess(self,user=0,newX=None,newY=None):  #Takes guessed square and shoots at the enemy, args takes new position
        if user == 0:  #For player
            playerShotList[self.selectedX][self.selectedY] = True
            if enemyShipsList[self.selectedX][self.selectedY]: 
                playerHitList[self.selectedX][self.selectedY] = True    #Flags square as hit
                self.checkKills()    #Checks if any ships have been sunk
            else:
                playerMissList[self.selectedX][self.selectedY] = True   #Flags square as missed
            self.selectedX = None
            self.selectedY = None
        elif user == 1: #For computer
            enemyShotList[newX][newY] = True
            if playerShipsList[newX][newY]:
                enemyHitList[newX][newY] = True  #Flags square as hit
                sunk = self.checkKills(1)
                return True,sunk
            else:
                enemyMissList[newX][newY] = True  #Flags square as missed
                return False,False
        
        
#Creates button classes
startButton = Button(300,250,"Start!","black","orange","orange","gray",200,100)
quitButton = Button(300,400,"Quit :(","black","orange","orange","gray",200,100)
shootButton = Button(535,430,"Shoot!","black","red","orange","black",100,40)
restartButton = Button(300,250,"Play again!","black","orange","orange","gray",200,100)

def gradientBg(top_color, bottom_color):
    for y in range(HEIGHT):
        ratio = y / HEIGHT
        r = int(top_color[0] * (1 - ratio) + bottom_color[0] * ratio)
        g = int(top_color[1] * (1 - ratio) + bottom_color[1] * ratio)
        b = int(top_color[2] * (1 - ratio) + bottom_color[2] * ratio)
        pygame.draw.line(screen, (r, g, b), (0, y), (WIDTH, y))

def startScreen():
    gradientBg((0, 119, 190), (0, 180, 255))
    Battle = titleFont.render("BATTLESHIP", True, (255, 255, 255))
    subtitle = gameFont.render("Sink all enemy ships to win!", True, (255, 255, 255))
    # Center text
    screen.blit(Battle, Battle.get_rect(center=(WIDTH // 2, 100)))
    screen.blit(subtitle, subtitle.get_rect(center=(WIDTH // 2, 175)))
    startButton.drawSelf()
    quitButton.drawSelf()
    

class BattleShipBot():
    def __init__(self):
        global enemyHitList
        global playerShipsSunk
        global enemyMissList
        global enemyShotList
        self.listHits = []  #Already hit targets that have not been sunk
    
    def shoot(self):
        shiptoShoot = False
        for i,row in enumerate(enemyHitList):
            for j,tile in enumerate(row):
                if tile != playerShipsSunk[i][j]:
                    shiptoShoot = True
                    self.listHits.append((i,j))  #Checks if a ship has been shot but not sunk and appends the coordinates to listHits
        
        if shiptoShoot:
            self.targetShot()  #There is a ship - targets its shots around the ship
        else:
            self.nextShot()  #There is no ship - Shoot in a way that covers most of the grid as fast as possible
            
                
    def nextShot(self):
        for x in range(10):
            # For each row, shoot at every other tile (X pattern)
            if x % 2 == 0:
                for y in range(0, 10, 2):  #Even rows = Even columns 
                    if not enemyShotList[x][y]:  #Make sure the tile hasn't been shot
                        targetGrid.guess(1, x, y)  #Shoot at this tile
                        return 0  #Don't shoot again
            else:
                for y in range(1, 10, 2):  #Odd rows = Odd columns
                    if not enemyShotList[x][y]:  #Make sure the tile hasn't been shot
                        targetGrid.guess(1, x, y)  #Shoot at this tile
                        return 0  #Don't shoot again
        
    def targetShot(self):  #Checks all 4 adjacent squares and shoots all available squares
        for x,y in self.listHits[::-1]:
            adjacent1 = [x + 1, y]
            if 0 <= adjacent1[0] < 10 and 0 <= adjacent1[1] < 10:  # Check if within grid bounds
                if not enemyShotList[adjacent1[0]][adjacent1[1]]:  # Check if not already shot
                    targetGrid.guess(1, adjacent1[0], adjacent1[1])
                    return 0

            adjacent2 = [x - 1, y]
            if 0 <= adjacent2[0] < 10 and 0 <= adjacent2[1] < 10:  # Check if within grid bounds
                if not enemyShotList[adjacent2[0]][adjacent2[1]]:  # Check if not already shot
                    targetGrid.guess(1, adjacent2[0], adjacent2[1])
                    return 0

            adjacent3 = [x, y + 1]
            if 0 <= adjacent3[0] < 10 and 0 <= adjacent3[1] < 10:  # Check if within gridbounds
                if not enemyShotList[adjacent3[0]][adjacent3[1]]:  # Check if not already shot
                    targetGrid.guess(1, adjacent3[0], adjacent3[1])
                    return 0

            adjacent4 = [x, y - 1]
            if 0 <= adjacent4[0] < 10 and 0 <= adjacent4[1] < 10:  # Check if within bounds
                if not enemyShotList[adjacent4[0]][adjacent4[1]]:  # Check if not already shot
                    targetGrid.guess(1, adjacent4[0], adjacent4[1])
                    return 0
        self.nextShot()



def mainLoop(): #Renders letters A - J and numbers 1 - 10
    screen.fill((255,255,255))
    a = gameFont.render("A",True,"black")
    b = gameFont.render("B",True,"black")
    c = gameFont.render("C",True,"black")
    d = gameFont.render("D",True,"black")
    e = gameFont.render("E",True,"black")
    f = gameFont.render("F",True,"black")
    g = gameFont.render("G",True,"black")
    h = gameFont.render("H",True,"black")
    i = gameFont.render("I",True,"black")
    j = gameFont.render("J",True,"black")
    num1 = gameFont.render("1",True,"black")
    num2 = gameFont.render("2",True,"black")
    num3 = gameFont.render("3",True,"black")
    num4 = gameFont.render("4",True,"black")
    num5 = gameFont.render("5",True,"black")
    num6 = gameFont.render("6",True,"black")
    num7 = gameFont.render("7",True,"black")
    num8 = gameFont.render("8",True,"black")
    num9 = gameFont.render("9",True,"black")
    num10 = gameFont.render("10",True,"black")

    aRect = (a.get_rect(center=(90,35)),a.get_rect(center=(440,35)))
    bRect = (b.get_rect(center=(120,35)),b.get_rect(center=(470,35)))
    cRect = (c.get_rect(center=(150,35)),c.get_rect(center=(500,35)))
    dRect = (d.get_rect(center=(180,35)),d.get_rect(center=(530,35)))
    eRect = (e.get_rect(center=(210,35)),e.get_rect(center=(560,35)))
    fRect = (f.get_rect(center=(240,35)),f.get_rect(center=(590,35)))
    gRect = (g.get_rect(center=(270,35)),g.get_rect(center=(620,35)))
    hRect = (h.get_rect(center=(300,35)),h.get_rect(center=(650,35)))
    iRect = (i.get_rect(center=(330,35)),i.get_rect(center=(680,35)))
    jRect = (j.get_rect(center=(360,35)),j.get_rect(center=(710,35)))
    num1Rect = (num1.get_rect(center=(60,65)),num1.get_rect(center=(410,65)))
    num2Rect = (num2.get_rect(center=(60,95)),num2.get_rect(center=(410,95)))
    num3Rect = (num3.get_rect(center=(60,125)),num3.get_rect(center=(410,125)))
    num4Rect = (num4.get_rect(center=(60,155)),num4.get_rect(center=(410,155)))
    num5Rect = (num5.get_rect(center=(60,185)),num5.get_rect(center=(410,185)))
    num6Rect = (num6.get_rect(center=(60,215)),num6.get_rect(center=(410,215)))
    num7Rect = (num7.get_rect(center=(60,245)),num7.get_rect(center=(410,245)))
    num8Rect = (num8.get_rect(center=(60,275)),num8.get_rect(center=(410,275)))
    num9Rect = (num9.get_rect(center=(60,305)),num9.get_rect(center=(410,305)))
    num10Rect = (num10.get_rect(center=(60,335)),num10.get_rect(center=(410,335)))

    #Labels for your grid and enemy grid
    yourGridText = gameFont.render("Your Ships",True,"black")
    enemyGridText = gameFont.render("Enemy Grid",True,"black")

    #Blit in labels for grid
    screen.blit(a,aRect[0])
    screen.blit(b,bRect[0])
    screen.blit(c,cRect[0])
    screen.blit(d,dRect[0])
    screen.blit(e,eRect[0])
    screen.blit(f,fRect[0])
    screen.blit(g,gRect[0])
    screen.blit(h,hRect[0])
    screen.blit(i,iRect[0])
    screen.blit(j,jRect[0])
    screen.blit(a,aRect[1])
    screen.blit(b,bRect[1])
    screen.blit(c,cRect[1])
    screen.blit(d,dRect[1])
    screen.blit(e,eRect[1])
    screen.blit(f,fRect[1])
    screen.blit(g,gRect[1])
    screen.blit(h,hRect[1])
    screen.blit(i,iRect[1])
    screen.blit(j,jRect[1])
    screen.blit(num1,num1Rect[0])
    screen.blit(num2,num2Rect[0])
    screen.blit(num3,num3Rect[0])
    screen.blit(num4,num4Rect[0])
    screen.blit(num5,num5Rect[0])
    screen.blit(num6,num6Rect[0])
    screen.blit(num7,num7Rect[0])
    screen.blit(num8,num8Rect[0])
    screen.blit(num9,num9Rect[0])
    screen.blit(num10,num10Rect[0])
    screen.blit(num1,num1Rect[1])
    screen.blit(num2,num2Rect[1])
    screen.blit(num3,num3Rect[1])
    screen.blit(num4,num4Rect[1])
    screen.blit(num5,num5Rect[1])
    screen.blit(num6,num6Rect[1])
    screen.blit(num7,num7Rect[1])
    screen.blit(num8,num8Rect[1])
    screen.blit(num9,num9Rect[1])
    screen.blit(num10,num10Rect[1])

    #Draw grids and shoot button
    targetGrid.drawSelf()
    selfGrid.drawSelf()
    shootButton.drawSelf()

    #Blit in Your grid and enemy grid text
    screen.blit(yourGridText,yourGridText.get_rect(center=(225,375)))
    screen.blit(enemyGridText,enemyGridText.get_rect(center=(575,375)))

    if shootButton.checkForClick():   #If shoot button clicked and a target is selected
        if targetGrid.returnSelected():
            targetGrid.guess()
            targetGrid.drawSelf()
            Computer.shoot()

def searchGrid(searchString):  #Search menu that appears
    testList = []
    for coord in searchString:
        if coord != None:
            testList.append(coord)

    largerRect = pygame.Rect(100,500,100,30)
    smallerRect = pygame.Rect(107.5,505,80,20)
    pygame.draw.rect(screen,(150,150,150),largerRect)
    pygame.draw.rect(screen,(230,230,230),smallerRect)
    screen.blit(searchIcon,(107.5,505,20,20))  #Draws the search meny and icon
    try:
        search = gameFont.render("".join(testList),True,"black")
        screen.blit(search,(130,505))  #Blits the search string on the screen
    except:
        return 0
    
def loseScreen():
    gradientBg((30, 30, 60), (0, 119, 190))
    Battle = titleFont.render("YOU LOST! :(", True, (255, 80, 80))
    ship = titleFont.render("Play again?", True, (255, 255, 255))
    screen.blit(Battle, Battle.get_rect(center=(WIDTH // 2, 100)))
    screen.blit(ship, ship.get_rect(center=(WIDTH // 2, 180)))
    restartButton.drawSelf()
    quitButton.drawSelf()

def winScreen():
    gradientBg((0, 180, 255), (0, 119, 190))
    Battle = titleFont.render("YOU WIN!!", True, (0, 255, 127))
    ship = titleFont.render("Play again?", True, (255, 255, 255))
    screen.blit(Battle, Battle.get_rect(center=(WIDTH // 2, 100)))
    screen.blit(ship, ship.get_rect(center=(WIDTH // 2, 180)))
    restartButton.drawSelf()
    quitButton.drawSelf()

def randomizeShips():  #Randomize ship position for both player and enemy
    global enemyShipsList
    global playerShipsList
    global playerShipUnits
    global enemyShipUnits 

    tempShipsList = []   #A temporary holder for ship coordinates
    choices = ["H","V"]
    enemyShipsList = [[False for x in range(10)] for y in range(10)]
    playerShipsList = [[False for x in range(10)] for y in range(10)]
    while len(set(tuple(ship) for ship in tempShipsList)) != len(tempShipsList) or tempShipsList == []:   #Turns coordinates into set, removing duplicates, comparing length makes sure that ships do not stack
        tempShipsList = []
        for x in range(4,8):
            HV = choice(choices)  #Dictates if ship is placed vertically or horizontally
            if HV == "H":
                xPos,yPos = randint(0,x),randint(0,9)
                widthShip = 10-x
                for j in range(0,widthShip-1):   #Horizontally places ship coordinates
                    tempShipsList.append([xPos+j,yPos])

            if HV == "V":
                xPos,yPos = randint(0,9),randint(0,x)
                heightShip = 10-x
                for j in range(0,heightShip-1):   #Vertically places ship coordinates
                    tempShipsList.append([xPos,yPos+j])

    for i,thing in enumerate(tempShipsList):
        enemyShipsList[thing[0]][thing[1]] = True   #Sorts ships based on lengths and adds them to enemyShipUnits
        if i <= 4:
            enemyShipUnits[0].append([thing[0],thing[1]])
        elif i <= 8:
            enemyShipUnits[1].append([thing[0],thing[1]])
        elif i <= 11:
            enemyShipUnits[2].append([thing[0],thing[1]])
        else:
            enemyShipUnits[3].append([thing[0],thing[1]])


    tempShipsList = []

    while len(set(tuple(ship) for ship in tempShipsList)) != len(tempShipsList) or tempShipsList == []:
        tempShipsList = []
        for x in range(4,8):
            HV = choice(choices)  #Dictates if ship is placed vertically or horizontally
            if HV == "H":
                xPos,yPos = randint(0,x),randint(0,9)
                widthShip = 10-x
                for j in range(0,widthShip-1):
                    tempShipsList.append([xPos+j,yPos])

            if HV == "V":
                xPos,yPos = randint(0,9),randint(0,x)
                heightShip = 10-x
                for j in range(0,heightShip-1):
                    tempShipsList.append([xPos,yPos+j])
                    
    for i,thing in enumerate(tempShipsList):   #Sorts ships based on lengths and adds them to playerShipUnits
        playerShipsList[thing[0]][thing[1]] = True
        if i <= 4:
            playerShipUnits[0].append([thing[0],thing[1]])
        elif i <= 8:
            playerShipUnits[1].append([thing[0],thing[1]])
        elif i <= 11:
            playerShipUnits[2].append([thing[0],thing[1]])
        else:
            playerShipUnits[3].append([thing[0],thing[1]])

#Set game state
state = "start"
searchString = [None,None]  #String to search
showSearch = False #Whether search menu is shown
selfGrid = ButtonGroup(75,50,30,30,300,300,False) #Player's grid
targetGrid = ButtonGroup(425,50,30,30,300,300,True) #Enemy grid
possibleKeys = [pygame.K_a,pygame.K_b,pygame.K_c,pygame.K_d,pygame.K_e,pygame.K_f,pygame.K_g,pygame.K_h,pygame.K_i,pygame.K_j]  #Keys for alphabet part of the grid
possibleNumKeys = [pygame.K_1,pygame.K_2,pygame.K_3,pygame.K_4,pygame.K_5,pygame.K_6,pygame.K_7,pygame.K_8,pygame.K_9,pygame.K_0]  #Keys for number part of the grid
Computer = BattleShipBot()


while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
        #Key presses 
        elif event.type == pygame.KEYDOWN:

            if event.key == pygame.K_s:
                showSearch = not(showSearch)
            if event.key in possibleKeys and showSearch:
                alphabet = ["A","B","C","D","E","F","G","H","I","J"]    #Corresponds each key in possibleKeys with the letter
                searchString[0] = alphabet[possibleKeys.index(event.key)]
            if event.key in possibleNumKeys and showSearch:
                nums = ["1","2","3","4","5","6","7","8","9","10"]   #Corresponds each key in possibleNumKeys with the number
                searchString[1] = nums[possibleNumKeys.index(event.key)]
            if event.key == pygame.K_RETURN:
                if targetGrid.returnSelected() and not(showSearch):
                    targetGrid.guess()
                    targetGrid.drawSelf()
                    Computer.shoot()
                    searchString = [None,None]
                elif showSearch:
                    
                    targetGrid.select(int(searchString[1])-1,alphabet.index(searchString[0]))
            
                
    #Run loops based on game state 
    if state == "start":
        startScreen()   #Draw start screen
        if startButton.checkForClick():
            state = "Loop"
            randomizeShips()
        if quitButton.checkForClick():
            pygame.quit()
    if state == "Loop":
        mainLoop()   #Draw main grid
        if showSearch:
            searchGrid(searchString)
        tick += 1
        if playerHitList == enemyShipsList:
            state = "Win"
        if enemyHitList == playerShipsList:
            state = "Lose"
    
    if state == "Win":
        winScreen()
        if restartButton.checkForClick():
            state = "Loop"   #Restart game and reset essential variables
            playerShipsList = [[False for x in range(10)] for y in range(10)]
            playerShipUnits = [[] for y in range(4)]
            enemyShipsList = [[False for x in range(10)] for y in range(10)]
            enemyShipUnits = [[] for y in range(4)]

            playerShotList = [[False for x in range(10)] for y in range(10)]
            enemyShotList = [[False for x in range(10)] for y in range(10)]
            playerMissList = [[False for x in range(10)] for y in range(10)]
            playerHitList = [[False for x in range(10)] for y in range(10)]
            enemyMissList = [[False for x in range(10)] for y in range(10)]
            enemyHitList = [[False for x in range(10)] for y in range(10)]

            enemyShipsSunk = [[False for x in range(10)] for y in range(10)]
            playerShipsSunk = [[False for x in range(10)] for y in range(10)]

            randomizeShips()

    if state == "Lose":
        loseScreen()
        if restartButton.checkForClick():
            state = "Loop"   
            playerShipsList = [[False for x in range(10)] for y in range(10)]
            playerShipUnits = [[] for y in range(4)]
            enemyShipsList = [[False for x in range(10)] for y in range(10)]
            enemyShipUnits = [[] for y in range(4)]

            playerShotList = [[False for x in range(10)] for y in range(10)]
            enemyShotList = [[False for x in range(10)] for y in range(10)]
            playerMissList = [[False for x in range(10)] for y in range(10)]
            playerHitList = [[False for x in range(10)] for y in range(10)]
            enemyMissList = [[False for x in range(10)] for y in range(10)]
            enemyHitList = [[False for x in range(10)] for y in range(10)]

            enemyShipsSunk = [[False for x in range(10)] for y in range(10)]
            playerShipsSunk = [[False for x in range(10)] for y in range(10)]

            randomizeShips()

    pygame.display.update()
