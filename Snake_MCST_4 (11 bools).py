import pygame
import random
import sys
import math
import time
from datetime import datetime

GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

NUM_BLOCKS = 30

SQ_SZ = 25




def draw_board(tail, foodLoc):
    global score, hiScore

    screen.fill(WHITE)

    pygame.font.init()  # you have to call this at the start,
    # if you want to use this module.
    myfont = pygame.font.SysFont('Comic Sans MS', 15)
    textsurface = myfont.render('SCORE: ' + str(score), False, BLACK)
    textsurface2 = myfont.render('HI:    ' + str(hiScore), False, BLACK)  # 'HI:    '+ str(hiScore)
    screen.blit(textsurface, (side - 100, 10))
    screen.blit(textsurface2, (side - 100, 30))

    foodY = int(foodLoc[0] * SQ_SZ + SQ_SZ * 0 / 4)
    foodX = int(foodLoc[1] * SQ_SZ + SQ_SZ * 0 / 4)
    pygame.draw.rect(screen, RED, (foodX, foodY, SQ_SZ * 2 / 2, SQ_SZ * 2 / 2))

    node = tail
    while node is not None:
        snekY = int(node.loc[0] * SQ_SZ + SQ_SZ * 0 / 1)
        snekX = int(node.loc[1] * SQ_SZ + SQ_SZ * 0 / 1)

        pygame.draw.rect(screen, BLACK, (snekX, snekY, SQ_SZ, SQ_SZ))
        node = node.par

    pygame.display.update()


class Snake:
    def __init__(self, loc, par):
        self.loc = loc
        self.par = par

    def __str__(self):
        if self.par is None:
            return str(self.loc) + "/"
        else:
            return str(self.loc) + " " + str(self.par.__str__())


def move(command):
    global tail
    thisMove = ''
    dir = (-100, -100)
    if command == 'UP':
        dir = (-1, 0)
        thisMove = 'UP'
    elif command == 'DOWN':
        dir = (1, 0)
        thisMove = 'DOWN'
    elif command == 'LEFT':
        dir = (0, -1)
        thisMove = 'LEFT'
    elif command == 'RIGHT':
        dir = (0, 1)
        thisMove = 'RIGHT'

    node = tail
    # loops through every node except head, starting at tail
    while node.par is not None:
        node.loc = node.par.loc
        node = node.par

    # head
    r = node.loc[0] + dir[0]
    c = node.loc[1] + dir[1]
    node.loc = (r, c)

    return thisMove


def checkEvent():
    # 1: Food
    # -1: Loss
    # 0: no event
    global head, foodLoc, tail
    if head.loc == foodLoc:
        return 1

    if not (0 <= head.loc[0] < NUM_BLOCKS):
        return -1
    if not (0 <= head.loc[1] < NUM_BLOCKS):
        return -1

    node = tail
    while node != head:
        if head.loc == node.loc:
            return -1
        node = node.par

    # TODO: check if it runs into itself, return -1
    return 0


def addSnake(tail):
    newSnek = Snake(tail.loc, tail)
    tail = newSnek
    return tail


def getRandomFoodLoc(tail):
    # returns a
    a = []
    for r in range(NUM_BLOCKS):
        for c in range(NUM_BLOCKS):
            a.append((r, c))

    node = tail
    # loop every snek
    while node is not None:
        a.remove(node.loc)
        node = node.par

    return random.choice(a)


def possibleChoices(lastMove):
    # TODO: don't allow complete 180 from last move
    a = ['UP', 'DOWN', 'LEFT', 'RIGHT']
    if lastMove is None:
        return ['UP']

    # Remove Opposite From last Move
    if lastMove == 'UP':
        a.remove('DOWN')
    if lastMove == 'DOWN':
        a.remove('UP')
    if lastMove == 'LEFT':
        a.remove('RIGHT')
    if lastMove == 'RIGHT':
        a.remove('LEFT')

    return a


def numToDir(n):
    if n == 0:
        return 'DOWN'
    if n == 1:
        return 'UP'
    if n == 2:
        return 'RIGHT'
    if n == 3:
        return 'LEFT'


def dirToNum(dir):
    if dir == 'DOWN':
        n = 0
    elif dir == 'UP':
        n = 1
    elif dir == 'RIGHT':
        n = 2
    elif dir == 'LEFT':
        n = 3
    else:
        print("Not Valid Direction")
        return None
    return n


def getDistance(head, foodLoc):
    d = math.sqrt(math.pow(head.loc[0] - foodLoc[0], 2) + math.pow(head.loc[1] - foodLoc[1], 2))
    return d


# TODO: UPDATE KEY TABLE. Takes in list of ks, and goes through, backtracking through the moves since it was last processed.

def getKvalues(head, foodLoc, recentMove, tailB):
    # Returns (leftDanger, straightDanger, rightDanger, movingLeft, movingRIght, movingUp, movingDown, f1, f2, f3, f4
    # vars
    # XDanger: is there danger to your immediate X
    # movingX: if the snake is moving in the X direction, that var is 1. Otherwise the var is 0
    # fX: food is in quadrant X. Quadrants, 1 = top-left 2 = top-right 3 = bottom-right 4 = bottom left

    # TODO: In order to update Q_table, we need a dict of keys and the decision they made ((1, 1, 0, 0..., 1), 'UP'). (start these decisions random, then choose from q)
    # the code below generates all the parts of k. When playing, we calculate this after every move made. Then when a reward or punishment is reached, we scale back and assign q-values
    forwardDanger, leftDanger, rightDanger = 0, 0, 0
    movingLeft, movingRight, movingUp, movingDown = 0, 0, 0, 0
    f1, f2, f3, f4 = 0, 0, 0, 0
    if recentMove == 'UP':
        trn = 0  # how much to turn to get the quadrant based on which way the snake is facing
        movingUp = 1
        forward = (-1, 0)
        right = (0, 1)
        left = (0, -1)
    elif recentMove == 'LEFT':
        trn = 1
        movingLeft = 1
        forward = (0, -1)
        right = (-1, 0)
        left = (1, 0)

    elif recentMove == 'RIGHT':
        trn = 3
        movingRight = 1
        forward = (0, 1)
        right = (1, 0)
        left = (-1, 0)

    elif recentMove == 'DOWN':
        trn = 2
        movingDown = 1
        forward = (1, 0)
        right = (0, -1)
        left = (0, 1)

    if not (0 <= head.loc[0] + forward[0] < NUM_BLOCKS):
        forwardDanger = 1
    if not (0 <= head.loc[1] + forward[1] < NUM_BLOCKS):
        forwardDanger = 1

    if not (0 <= head.loc[0] + left[0] < NUM_BLOCKS):
        leftDanger = 1
    if not (0 <= head.loc[1] + left[1] < NUM_BLOCKS):
        leftDanger = 1

    if not (0 <= head.loc[0] + right[0] < NUM_BLOCKS):
        rightDanger = 1
    if not (0 <= head.loc[1] + right[1] < NUM_BLOCKS):
        rightDanger = 1

    vec = (head.loc[0] - foodLoc[0], head.loc[1] - foodLoc[1])
    q = -1  # quadrant 1 2
    #         # 4 3
    if vec[0] < 0:
        if vec[1] > 0:
            q = 1
        else:
            q = 4
    else:
        if vec[1] > 0:
            q = 2
        else:
            q = 3

    q = (q + trn) % 4
    if q == 0:
        q = 4  # 1-4, not 0-3

    if q == 1:
        f1 = 1
    elif q == 2:
        f2 = 1
    elif q == 3:
        f3 = 1
    elif q == 4:
        f4 = 1
    else:
        print("error. ~ln. 268")

    # tailB = False
    if tailB:
        node = tail
        while node != head:
            if (head.loc[0] + forward[0], head.loc[1] + forward[1]) == node.loc:
                forwardDanger = 1

            if (head.loc[0] + left[0], head.loc[1] + left[1]) == node.loc:
                leftDanger = 1

            if (head.loc[0] + right[0], head.loc[1] + right[1]) == node.loc:
                rightDanger = 1

            node = node.par

    # Each description of k values at top
    k = (leftDanger, forwardDanger, rightDanger, movingLeft, movingRight, movingUp, movingDown, f1, f2, f3, f4)
    return k


def update_Q_table2(kDirList, r):
    global Q_table, GAMMA, recentMoves
    # Function:
    # kDirList: list of pairs of k's and directions
    # k's -look at above return-, direction-direction chosen at the last state-)
    # r: reward

    rew = r  # starts at r, decreases (based off GAMMA)

    if recentMoves == []:
        return


    # recent list becomes last move
    if r == neuReward: # or r == negReward:
        n = len(recentMoves)
        lastMove = recentMoves[n - 1]
        kDirList = []
        kDirList.append(lastMove)

    kDirList.reverse()
    i = 0
    for el in kDirList:
        i += 1
        if i >= 15:
            break
        # el is a pair of k's and direction
        k = el[0]
        dir = el[1]

        dNum = dirToNum(dir)

        if k not in Q_table.keys():
            Q_table[k] = [0, 0, 0, 0, 0, 0, 0, 0]

        # print (rew)
        Q_table[k][dNum] += rew

        Q_table[k][dNum + 4] += 1

        if rew > 0:
            rew *= GAMMA
        elif rew < 0:
            rew *= NEGAM

    if r != neuReward:
        recentMoves = []


def chooseFromQ(k, a, test=False):
    # if test is true, then exploitation > exploration
    global Q_table

    if k not in Q_table.keys():
        return random.choice(a)

    # Choose based on exploration and winning choices
    vals = Q_table[k][0:4].copy()
    views = Q_table[k][4:].copy()

    for i in range(4):
        if numToDir(i) not in a:
            vals[i] = -math.inf
            removed = i

    if test:  # then just choose the highest score
        c = vals.index(max(vals))
        # print(c, vals[c], "   ", vals)
        return numToDir(c)

    scores = []
    N = sum(views)
    C = 5  # Higher c, higher exploration
    for i in range(4):
        if i == removed:
            scores.append(-math.inf)
            continue
        w = vals[i]
        n = views[i]
        if n == 0:
            scores.append(math.inf)
        else:
            left = w / n
            # left = sigmoid(left1)
            right1 = math.sqrt(math.log(N, math.e) / n)
            right = C * right1
            # left is how high the score, right is how explored
            UCB1 = left + right
            rand01 = random.uniform(0, 1)
            if rand01 < 0.000000001:
                print(left, "///", right, "   (score =", w, ", views =", n, ")")
            scores.append(UCB1)
    c = scores.index(max(scores))
    return numToDir(c)

    # print ("MX: ", vals.index(mx))


def sigmoid(x):
    return 1 / (1 + math.exp(-x))


# main

# Setup
stLoc = (int((NUM_BLOCKS - 1) / 2), int((NUM_BLOCKS - 1) / 2))
head = Snake(stLoc, None)
tail = head

snek2 = Snake((stLoc[0] + 1, stLoc[1]), head)
tail = snek2

foodLoc = getRandomFoodLoc(tail)
#
f = open('hiScoreLog.txt', 'r+')
f.truncate(0)  # need '0' when using r+
f.close()

# CONSTANTS
Q_table = {}

# high score initialization
fileHandle = open('hiScoreLog.txt', "r")
lineList = fileHandle.readlines()
fileHandle.close()
if len(lineList) == 0:
    hiScore = 0
else:
    latestLog = lineList[-1]
    hiScore = int(latestLog)

GAMMA = 0.6
NEGAM = 0.8 #.6

posReward = 10
neuReward = -0.00
negReward = -70 #18

limit = 500

# games
trainingTrials = 20000 * 100  # OVERNIGHT: 20000 * 10 * 20, don't record until morning


# TRAINING
print("training...  ({})".format(trainingTrials))
millis = int(round(time.time() * 1000))

score = 0

# draw_board(tail, foodLoc)

recentMoves = []

m = 'UP'

curSum = 0
cnt = 0

i = 0


side = SQ_SZ * NUM_BLOCKS
size = (side, side)
screen = pygame.display.set_mode(size)

startingTimeTraining = datetime.now()

pygame.init()
pygame.display.set_caption('SNEK')



timeElapsed = 0

prevScore = 0

first = True
while i < trainingTrials:
    if i == 1:
        print("beginning (now that score >= 3 exists")
    i += 1

    perc = 100 * i / trainingTrials
    # print ("Q_table: ", Q_table)
    if i % (trainingTrials / 100) == 0:
        print("-----")
        print("{} % \t(trial = {})".format(perc, i))
        print("Avg = {}   ({}/{})".format(curSum / cnt, curSum, cnt))
        print ("Q-table: ", Q_table)
        print("-----")
        curSum = 0
        cnt = 0

    # print("Game {}: \n\t{}".format(i + 1, Q_table))
    # print ("### k = (leftDanger, forwardDanger, rightDanger, movingLeft, movingRight, movingUp, movingDown, f1, f2, f3, f4)")

    movesSince = 0
    while True:
        movesSince += 1
        # if moves >= 1000:

        if movesSince > limit:
            # print ("too many moves")
            update_Q_table2(recentMoves, negReward)
            break

        # www
        # each game:
        choices = possibleChoices(m)
        tailVar = True
        if perc > 0:
            tailVar = True
        k = getKvalues(head, foodLoc, m, tailVar)
        # m: chosen move
        m = chooseFromQ(k, choices)
        move(m)
        recentMoves.append((k, m))

        # xxx (printing board)
        if (hiScore >= 55 and score > 38) or (score > hiScore and score > 30):
            if (first):
                first = False
                timeElapsed = datetime.now() - startingTimeTraining
                print("StartOfRun = {}".format(timeElapsed, score))
            draw_board(tail, foodLoc)
            pygame.time.wait(18)
        else:
            if not first:
                timeElapsed = datetime.now() - startingTimeTraining
                print("EndOfRun = {} (score = {})".format(timeElapsed, prevScore))
            first = True

        # print ("Q: ", Q_table)

        # if a decision is made (r is picked), look through list ofrecent state-action pairs
        event = checkEvent()  # 1: Food -1: Loss 0: no event
        # print (event
        # print (moves)

        if event == 0:
            pass
            # update_Q_table2(recentMoves, neuReward)

        elif event == 1:
            if score > 15:
                # pos = (1/4)* score# *(1/2)
                pos = (curSum / cnt)/4 + score/4
            else:
                pos = 5
            movesSince = 0
            score += 1
            update_Q_table2(recentMoves, pos)
            foodLoc = getRandomFoodLoc(tail)
            tail = addSnake(tail)

        elif event == -1:
            update_Q_table2(recentMoves, negReward)
            movesSince = 0
            break

        # pygame.time.wait(4)

    # print ("Game {}: \n\t{}".format(i+1, Q_table))
    # print ("### k = (leftDanger, forwardDanger, rightDanger, movingLeft, movingRight, movingUp, movingDown, f1, f2, f3, f4)")

    ## high score logic
    if score > hiScore:
        print("Q_table:", Q_table)
        print("\tNew High Score = ", score)
        hiScore = score
        with open("hiScoreLog.txt", "a") as text_file:
            text_file.write(str(hiScore) + "\n")
            text_file.close()

    if hiScore <= 2:
        i = 0

    # Setup
    stLoc = (int((NUM_BLOCKS - 1) / 2), int((NUM_BLOCKS - 1) / 2))
    head = Snake(stLoc, None)
    tail = head

    snek2 = Snake((stLoc[0] + 1, stLoc[1]), head)
    tail = snek2

    curSum += score
    cnt += 1
    prevScore = score
    score = 0

millis2 = int(round(time.time() * 1000))

t = 0
print ("Waiting {} minutes".format(t))
print ("\t Time =", datetime.now().strftime("%H:%M:%S"))
pygame.time.wait(t * 1000 * 60)






# pygame.display.quit()
# sys.exit()


# waitMS = 600000  # 60,000 : 10m
#
# # 10
# print ()
# while (waitMS  >= 30000):
#     print ("{} minutes until test".format(waitMS/60/1000))
#     waitMS = int( waitMS / 2)
#     pygame.time.wait(waitMS)
#
# waitMS = 30000
# while waitMS > 0:
#     waitMS -= 1000     #30
#     print ("{}s".format(waitMS/60/1000))
# print ("")
# waitMS = 180000
# print ("------------")
# print ("... wait {} s ...".format(waitMS/1000))
# pygame.time.wait(waitMS)



print()
print("Hi Score = ", hiScore)

testingTrials = 10000
print("Q_table", Q_table)
print("testing...")



startingTime = datetime.now()
i = 0
while i < testingTrials:
    i += 1
    # print ("Test", i)
    movesSince = 0
    while True:
        movesSince += 1
        if movesSince > limit:
            update_Q_table2(recentMoves, negReward)
            break
        # www
        # each game:
        choices = possibleChoices(m)
        k = getKvalues(head, foodLoc, m, False)
        # m: chosen move
        m = chooseFromQ(k, choices, True)

        move(m)

        draw_board(tail, foodLoc)

        recentMoves.append((k, m))

        # if a decision is made (r is picked), look through list of recent state-action pairs
        event = checkEvent()  # 1: Food -1: Loss 0: no event
        if event == 0:
            update_Q_table2(recentMoves, neuReward)
        elif event == 1:
            if score > 10:
                pos = 3*math.log(score, math.e)
            else:
                pos = 8
            movesSince = 0
            score += 1
            update_Q_table2(recentMoves, pos)
            foodLoc = getRandomFoodLoc(tail)
            tail = addSnake(tail)

        elif event == -1:
            update_Q_table2(recentMoves, negReward)
            break
        pygame.time.wait(18)

    # Setup
    stLoc = (int((NUM_BLOCKS - 1) / 2), int((NUM_BLOCKS - 1) / 2))
    head = Snake(stLoc, None)
    tail = head

    snek2 = Snake((stLoc[0] + 1, stLoc[1]), head)
    tail = snek2

    # print("score = {} \t(Q: {})".format(score, Q_table))
    if (score >= 80):
        timeElapsed = datetime.now() - startingTime
        print ("Score  = {}, TimeElapsed = {}".format(score, timeElapsed))
    score = 0




print("------------")

print("{} seconds to complete ({} tests)".format((millis2 - millis) / 1000, trainingTrials))
print()
print("Hi score = {}".format(hiScore))
print()
print("Q_table = ", Q_table)

print("\n\n\n")
print("#Trials \tPos/Neg/Neu \t\tHigh Score")
print("{}\t\t{}/{}/{} \t\t {}".format(trainingTrials, "score/2", negReward, neuReward, hiScore))

pygame.display.quit()
sys.exit()
