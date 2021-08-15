import time
import random

# ☺☻♥♦♣♠•◘○◙♂♀♪♫☼►◄↕‼¶§▬↨↑↓→←∟↔▲▼ !\"#$%&'()*+,-./0123456789:;<=>?@ABDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_`abcdefghijklmnopqrstuvwxyz{|}~⌂ÇüéâäàåçêëèïîìÄÅÉæÆôöòûùÿÖÜ¢£¥₧ƒáíóúñÑªº¿⌐¬½¼¡«»░▓│┤╡╢╖╜╣║╗╝╜╛┐└┴┬├─┼╞╟╚╔╩╦╠═╬╧╨╤╥╙╘╒╓╫╪┘┌█▄▌▐▀αßΓπΣσµτΦΘΩδ∞φε∩≡±≥≤⌠⌡÷≈°∙·√ⁿ²■ 

lWall = "▌"
rWall = "▐"
floor = "▀"
block = "█"

import curses
scr = curses.initscr()
curses.curs_set(0)
curses.noecho()

curses.start_color()
curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_BLACK)
curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)
curses.init_pair(3, curses.COLOR_GREEN, curses.COLOR_BLACK)
curses.init_pair(4, curses.COLOR_BLUE, curses.COLOR_BLACK)
curses.init_pair(5, curses.COLOR_YELLOW, curses.COLOR_BLACK)
curses.init_pair(6, curses.COLOR_CYAN, curses.COLOR_BLACK)
curses.init_pair(7, curses.COLOR_MAGENTA, curses.COLOR_BLACK)

colors = {}
colors["E"] = 1
colors["R"] = 2
colors["G"] = 3
colors["B"] = 4
colors["Y"] = 5
colors["C"] = 6
colors["M"] = 7
colorSchema = "RGBYCM"

STATE_WON = 1
STATE_PLAYING = 2

class Tube:
    def __init__(self, height = 4):
        self.balls = []
        self.height = height
        self.loc = (30, 20)
        self.active = False
        self.mapping = ""

    def push(self, balls):
        for ball in balls:
            if ball == "E": continue
            self.balls.append(ball)

    def pop(self):
        self.balls = self.balls[:-1]

    def topBall(self):
        if len(self.balls) == 0: return "E"
        return self.balls[-1]

    def isFull(self):
        if len(self.balls) == self.height: return True
        return False

    def isSolved(self):
        if (len(self.balls) == self.height) and (len(set(self.balls)) == 1): return True
        if len(self.balls) == 0: return True    # Empty tubes count as solved
        return False

    def render(self):
        scr.addstr(self.loc[1] + 2, self.loc[0], self.mapping)
        scr.addstr(self.loc[1] + 1, self.loc[0] - 2, floor * 5)

        balls = self.balls

        if self.active:
            top = self.topBall()
            balls = balls[:-1]

            goalHeight = self.height + 2
            currentHeight = len(balls)
            delta = goalHeight - currentHeight
            for n in range(delta): balls.append("E")
            balls.append(top)

        # Render tube walls
        for h in range(self.height):
            scr.addstr(self.loc[1] - h, self.loc[0] - 2, f"{block}{' ' * 3}{block}")

        # Render balls
        balls = self.balls
        if self.active:
            top = self.topBall()
            balls = balls[:-1]

            goalHeight = self.height + 1
            currentHeight = len(balls)
            delta = goalHeight - currentHeight
            for n in range(delta): balls.append("E")
            balls.append(top)

        for h in range(len(balls)):
            c = colors[balls[h]]
            scr.addstr(self.loc[1] - h, self.loc[0] - 1, f"{block * 3}", curses.color_pair(c))

    # Returns a padded string of self.balls' representation
    def algorithm(self):
        retVal = ""
        for ball in self.balls[::-1]: retVal += ball
        Es = self.height - len(retVal)
        retVal += "E" * Es
        return retVal

class TubeGame:
    def __init__(self):
        self.tubes = []
        self.levels = []

        #self.levels.append("4:RRBBRRBBEEEE")
        #self.levels.append("4:BYBYYBYEBEEE")
        #self.levels.append("4:YBRBBYRRRBYYEEEEEEEE")
        self.levels.append("4:RYBYRRBBBRYYEEEEEEEE")
        self.levels.append("4:BYBYYRRBBRYREEEEEEEE")

        self.mapping = "asdkl;"
        #self.mapping = "asdfjkl;"
        #self.mapping = "sdfjkl"

    def generateLevel(self, height = 4, difficulty = 0):
        tubeCount = random.randint(3, 6)
        colorCount = tubeCount - 1
        tubes = []
        height = 4

        # Generate temporary tubes to mess around with
        for n in range(tubeCount):
            tube = Tube(height = height)
            tubes.append(tube)

        # Fill temporary tubes with colors
        for n in range(colorCount):
            for c in range(height): tubes[n].push(colorSchema[n])
            tubes[n]

        # Now we randomize mixing up the balls
        for n in range(1000):
            tubeA = tubes[random.randint(0, tubeCount - 1)]
            tubeB = tubes[random.randint(0, tubeCount - 1)]

            tubeATop = tubeA.topBall()
            tubeBTop = tubeB.topBall()
            if tubeBTop == "E" or tubeBTop == tubeATop:    # Can't just move things willy nilly!
            #if True:    # [TODO] Find out if this actually is allowed, or possible for every situation... Not sure it is
                if len(tubeB.balls) < height:
                    ball = tubeA.topBall()
                    tubeA.balls = tubeA.balls[:-1]
                    tubeB.push(ball)

        algorithm = f"{height}:"
        for tube in tubes: algorithm += tube.algorithm()

        return algorithm

    def setupNextLevel(self, replay = False):
        if replay == False: self.currentLevel = self.generateLevel()
        # [TODO/BUG] I really want to generate random levels, but the current system can generate impossible levels...
        #self.levels.append(self.currentLevel)

        if len(self.levels) == 0: return False

        nextLevel = self.levels[0]
        self.levels = self.levels[1:]

        self.tubes = []
        parts = nextLevel.split(":")
        height = int(parts[0])
        ballSets = parts[1]
        ballSets = [ballSets[i : i + height] for i in range(0, len(ballSets), height)]

        self.height = height
        for balls in ballSets: self.addTube(balls, height)

        return True

    def addTube(self, balls, height):
        mapping = self.mapping[len(self.tubes)]

        tube = Tube()
        tube.height = height
        tube.mapping = mapping
        tube.push(balls)

        xOffset = 9 * len(self.tubes)
        tube.loc = (tube.loc[0] + xOffset, tube.loc[1])

        self.tubes.append(tube)

    def toggleTube(self, index):
        if index >= len(self.tubes): return    # Not particularly interested in toggling tubes that don't exist!

        activeTube = None

        # [TODO] Add some protection here to account for an outlier error where more than one tube is active at any one time
        # This situation should never happen and it should be accounted for
        for tube in self.tubes:
            if tube.active and activeTube == None: activeTube = tube

        # [TODO] Fix this ugly nested loop nonsense logic here
        if activeTube == None:
            self.tubes[index].active = True    # Toggle selected tube on
        else:
            if self.tubes[index] == activeTube: activeTube.active = False    # Toggle selected tube off

            else:
                destinationTube = self.tubes[index]
                if not destinationTube.isFull():
                    ball = activeTube.topBall()
                    destinationBall = destinationTube.topBall()

                    if ball != "E":    # Musn't try to move an empty space!
                        # Cannot move ball if ball colors do not match
                        if destinationBall == ball or destinationBall == "E":
                            activeTube.pop()
                            activeTube.active = False
                            destinationTube.push(ball)
                else: pass    # Cannot move ball since destination is full of balls already

    def gameState(self):
        state = STATE_PLAYING

        solvedTubeCount = 0
        for tube in self.tubes:
            if tube.isSolved(): solvedTubeCount += 1

        if solvedTubeCount == len(self.tubes): state = STATE_WON

        return state

    def play(self):
        FPS = 30

        if self.setupNextLevel() == False: exit()
        while True:
            scr.clear()

            for tube in self.tubes: tube.render()

            scr.refresh()

            if self.gameState() == STATE_WON:
                scr.addstr(1, 1, "You Won!")
                scr.getkey()
                if self.setupNextLevel() == False: exit()
                continue

            input = scr.getkey()

            selectedTube = None
            if input in self.mapping: selectedTube = self.mapping.index(input)
            if selectedTube != None: self.toggleTube(selectedTube)
            if input == "r": self.setupNextLevel(replay = True)
            if input == "q": break

            #time.sleep(1.0 / FPS)

game = TubeGame()
game.play()
