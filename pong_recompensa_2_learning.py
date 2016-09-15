import pygame, sys
from pygame.locals import *
import random as rand

# Number of frames per second
# Change this value to speed up or slow down your game
#FPS = float(raw_input("choose speed: "))
# FPS = 500
def pause():
    raw_input("Continue")
    #just a pause function for debugging
#Global Variables to be used through our program
WINDOWWIDTH = 300
WINDOWHEIGHT = 200
LINETHICKNESS = 10
PADDLESIZE = 40
PADDLEOFFSET = 20
ACTIONS = {'up':0,'down':1,'stop':2}
actionList = ['up', 'down', 'stop']
XSTATES = (range(WINDOWWIDTH+1))
YSTATES = (range(WINDOWHEIGHT+1))
ANGLES = (1,-1)
ERROS = 0
epsGreedy = 0.5
steps = 0;


POSICOES_DO_PADDLE = 10
STEP_PADDLE = (WINDOWHEIGHT-2*LINETHICKNESS)/POSICOES_DO_PADDLE

PADDLEPOS = (range(0,POSICOES_DO_PADDLE))

Q = [ [ [ [ [ [rand.uniform(0.5,1)]for i in ACTIONS] for i in  PADDLEPOS] for i in ANGLES] for i in YSTATES] for i in XSTATES]
#print len(Q[300][200][1][9][2])


# Set up the colours
BLACK     = (0  ,0  ,0  )
WHITE     = (255,255,255)

#Draws the arena the game will be played in.
def drawArena():
    DISPLAYSURF.fill((0,0,0))
    #Draw outline of arena
    pygame.draw.rect(DISPLAYSURF, WHITE, ((0,0),(WINDOWWIDTH,WINDOWHEIGHT)), LINETHICKNESS*2)
    #Draw centre line
    pygame.draw.line(DISPLAYSURF, WHITE, ((WINDOWWIDTH/2),0),((WINDOWWIDTH/2),WINDOWHEIGHT), (LINETHICKNESS/4))


#Draws the paddle
def drawPaddle(paddle):
    #Stops paddle moving too low
    if paddle.bottom > WINDOWHEIGHT - LINETHICKNESS:
        paddle.bottom = WINDOWHEIGHT - LINETHICKNESS
    #Stops paddle moving too high
    elif paddle.top < LINETHICKNESS:
        paddle.top = LINETHICKNESS
    #Draws paddle
    pygame.draw.rect(DISPLAYSURF, WHITE, paddle)


#draws the ball
def drawBall(ball):
    pygame.draw.rect(DISPLAYSURF, WHITE, ball)

#moves the ball returns new position
def moveBall(ball, ballDirX, ballDirY):
    ball.x += ballDirX
    ball.y += ballDirY
    return ball

#Checks for a collision with a wall, and 'bounces' ball off it.
#Returns new direction
def checkEdgeCollision(ball, ballDirX, ballDirY):
    if ball.top == (LINETHICKNESS) or ball.bottom == (WINDOWHEIGHT - LINETHICKNESS):
        ballDirY = ballDirY * -1
    if ball.left == (LINETHICKNESS) or ball.right == (WINDOWWIDTH - LINETHICKNESS):
        ballDirX = ballDirX * -1
    return ballDirX, ballDirY

#Checks is the ball has hit a paddle, and 'bounces' ball off it.
def checkHitBall(ball, paddle1, paddle2, ballDirX):
    if ballDirX == -1 and paddle1.right == ball.left and paddle1.top < ball.bottom and paddle1.bottom > ball.top:
        return -1
    elif ballDirX == 1 and paddle2.left == ball.right and paddle2.top < ball.bottom and paddle2.bottom > ball.top:
        return -1
    else: return 1

#Checks to see if a point has been scored returns new score
def checkPointScored(paddle1, ball, score, ballDirX):
    #reset points if left wall is hit
    if ball.left == LINETHICKNESS:

        return score
    #1 point for hitting the ball
    elif ballDirX == -1 and paddle1.right == ball.left and paddle1.top < ball.bottom and paddle1.bottom > ball.top:
        score += 1
        return score
    #5 points for beating the other paddle
    elif ball.right == WINDOWWIDTH - LINETHICKNESS:
        score += 0
        return score
    #if no points scored, return score unchanged
    else: return score

#Artificial Intelligence of computer player
def artificialIntelligence(ball, ballDirX, paddle2):
    #If ball is moving away from paddle, center bat
    if ballDirX == -1:
        if paddle2.centery < (WINDOWHEIGHT/2):
            paddle2.y += 1
        elif paddle2.centery > (WINDOWHEIGHT/2):
            paddle2.y -= 1
    #if ball moving towards bat, track its movement.
    elif ballDirX == 1:
        if paddle2.centery < ball.centery:
            paddle2.y += 1
        else:
            paddle2.y -=1
    return paddle2

#Displays the current score on the screen
def displayScore(score):
    resultSurf = BASICFONT.render('Score = %s' %(score), True, WHITE)
    resultRect = resultSurf.get_rect()
    resultRect.topleft = (WINDOWWIDTH - 150, 25)
    DISPLAYSURF.blit(resultSurf, resultRect)

def getPaddlePos(paddle):
    paddlePos = int(paddle.y/16)
    return paddlePos


def rewardFunction( ball , paddle1, ballDir , acao):
    global ERROS
    ballDirX = ballDir[0]
    ballDirY = ballDir[1]

    if ball.left  > ((2*LINETHICKNESS)+PADDLEOFFSET):
        if ballDirY > 0:
            if acao == "down":
                R = 10
            elif acao == "up":
                R = -10
            else:
                R = 0

        elif ballDirY < 0:
            if acao == "down":
                R = -10
            elif acao == "up":
                R = 10
            else:
                R = 0

    if (ballDirX == -1) and (ball.left == paddle1.right):

        if (paddle1.top < ball.bottom) and (paddle1.bottom > ball.top):

            R = 50
            print ERROS
            # pause()
            ERROS = 0


        else:
            R = -50
            ERROS = ERROS + 1
            # print ERROS


    else:
        R = 0
    return R

def CALCQ( ball , angle , paddle1 , action, ballDir):

    global Q

    X = ball.x
    Y = ball.y
    paddle_pos = getPaddlePos(paddle1)


    ALPHA = 0.1
    GAMMA = 0.01

    Q[X][Y][angle][paddle_pos][action][0] = (Q[ball.x][ball.y][angle][paddle_pos][action][0]
    + ALPHA*(rewardFunction( ball , paddle1, ballDir , action) + GAMMA*( MAX_NEXT_STATE(X,Y,angle,paddle1, action) -  Q[ball.x][ball.y][angle][paddle_pos][action][0]) ) )

    #print "Q[ball.x][ball.y][angle][paddle_pos][ACTION][0]: ", Q[ball.x][ball.y][angle][paddle_pos][ACTION][0]



def MAX_NEXT_STATE(X,Y,angle,paddle1, action):

    global Q

    if action == 0: #PADDLE GOES UP
        paddle1.y = paddle1.y + STEP_PADDLE
        if paddle1.y > 150:
           paddle1.y = 150
    elif action == 1: #PADDLE GOES DOWN
        paddle1.y = paddle1.y - STEP_PADDLE
        if paddle1.y < 10:
           paddle1.y = 10

    paddle_pos = getPaddlePos(paddle1)

    Q1 = Q[X][Y][angle][paddle_pos][ACTIONS['up']][0]
    Q2 = Q[X][Y][angle][paddle_pos][ACTIONS['down']][0]
    Q3 = Q[X][Y][angle][paddle_pos][ACTIONS['stop']][0]

    Qmax = max(Q1,Q2,Q3)

    return Qmax

def choose_action( ball , angle , paddle1, score):
    global epsGreedy

    if rand.random() < epsGreedy:
        achosen = actionList[rand.randint(0,2)]
        # print "RANDOM"
    else:
        qmax = 0.001
        # VALORES LIMITE DE ACESSO EM Q: Q[300][200][1][9][2]
        # em ordem: posX, posY, angle, posPADDLE, ACTION
        paddle_pos = getPaddlePos(paddle1)
        entradas = 0

        for a in ACTIONS:
            Q_value = Q[ball.x][ball.y][angle][paddle_pos][ACTIONS[a]][0]

            if Q_value >= qmax:
                entradas = entradas+1
                qmax = Q_value
                achosen = a

            else:
                if entradas == 0:
                    achosen = "stop"
        # print "CHOSEN"
    if epsGreedy > 1e-16:
        epsGreedy = 0.99999*epsGreedy

    else:
        epsGreedy = 0

    return achosen


#Main function
def main():
    pygame.init()
    global DISPLAYSURF
    ##Font information
    global BASICFONT, BASICFONTSIZE

    # BASICFONTSIZE = 20
    # BASICFONT = pygame.font.Font('freesansbold.ttf', BASICFONTSIZE)
    #
    # FPSCLOCK = pygame.time.Clock()
    # DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH,WINDOWHEIGHT))
    # pygame.display.set_caption('Pong')

    #Initiate variable and set starting positions
    #any future changes made within rectangles
    ballX = WINDOWWIDTH/2 - LINETHICKNESS/2
    ballY = WINDOWHEIGHT/2 - LINETHICKNESS/2
    playerOnePosition = (WINDOWHEIGHT - PADDLESIZE) /2
    playerTwoPosition = (WINDOWHEIGHT - PADDLESIZE) /2
    score = 0

    #Keeps track of ball direction
    ballDirX = -1 ## -1 = left 1 = right
    ballDirY = -1 ## -1 = up 1 = down

    #Creates Rectangles for ball and paddles.
    paddle1 = pygame.Rect(PADDLEOFFSET,playerOnePosition, LINETHICKNESS,PADDLESIZE)
    paddle2 = pygame.Rect(WINDOWWIDTH - PADDLEOFFSET - LINETHICKNESS, playerTwoPosition, LINETHICKNESS,PADDLESIZE)
    ball = pygame.Rect(ballX, ballY, LINETHICKNESS, LINETHICKNESS)

    # Draws the starting position of the Arena

    # drawArena()
    # drawPaddle(paddle1)
    # drawPaddle(paddle2)
    # drawBall(ball)

    #pygame.mouse.set_visible(0) # make cursor invisible

    while True: #main game loop
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            # mouse movement commands

            #elif event.type == MOUSEMOTION:
                #mousex, mousey = event.pos
                #paddle1.y = mousey

        # drawArena()
        # drawPaddle(paddle1)
        # drawPaddle(paddle2)
        # drawBall(ball)

        ball = moveBall(ball, ballDirX, ballDirY)
        ballDirX, ballDirY = checkEdgeCollision(ball, ballDirX, ballDirY)

        ballDir = [ballDirX, ballDirY]

        score = checkPointScored(paddle1, ball, score, ballDirX)
        ballDirX = ballDirX * checkHitBall(ball, paddle1, paddle2, ballDirX)
        paddle2 = artificialIntelligence (ball, ballDirX, paddle2)

        # displayScore(score)


        if ballDirX == -1:
            angle = 0
        else:
            angle = 1

        acao = choose_action( ball , angle , paddle1, score)
        #print "acao: ", acao
        CALCQ( ball , angle , paddle1 , ACTIONS[acao],  ballDir)

        # pygame.display.update()
        # FPSCLOCK.tick(FPS)

if __name__=='__main__':
    main()
