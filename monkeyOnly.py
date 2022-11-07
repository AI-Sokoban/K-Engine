import sys
import collections
import numpy as np
import heapq
import time
# from render import Renderer
# from board import BoardManager
# import pygame


class PriorityQueue:
    """Define a PriorityQueue data structure that will be used"""

    def __init__(self):
        self.Heap = []
        self.Count = 0

    def push(self, item, priority):
        entry = (priority, self.Count, item)
        heapq.heappush(self.Heap, entry)
        self.Count += 1

    def pop(self):
        (_, _, item) = heapq.heappop(self.Heap)
        return item

    def isEmpty(self):
        return len(self.Heap) == 0


"""Load puzzles and define the rules of sokoban"""


def transferToGameState(layout):
    """Transfer the layout of initial puzzle"""
    layout = [x.replace('\n', '') for x in layout] #ตัด \n
    layout = [','.join(layout[i]) for i in range(len(layout))]
    layout = [x.split(',') for x in layout] # ทำให้ map ออกมาในรูปของ [[' ', ' ', '#', '#', '#', '#', '#'], ['#', '#', '#', ' ', ' ', ' ', '#'], ['#', '.', '&', 'B', ' ', ' ', '#'], ['#', '#', '#', ' ', 'B', '.', '#'], ['#', '.', '#', '#', 'B', ' ', '#'], ['#', ' ', '#', ' ', '.', ' ', '#', '#'], ['#', 'B', ' ', 'X', 'B', 'B', '.', '#'], ['#', ' ', ' ', ' ', '.', ' ', ' ', '#'], ['#', '#', '#', '#', '#', '#', '#', '#', ' ']]
    #print('layout -> ',layout)
    maxColsNum = max([len(x) for x in layout]) #จำนวน คอลัมน์สูงสุดของ map
    #print('maxColsNum -> ',maxColsNum)
    for irow in range(len(layout)):
        for icol in range(len(layout[irow])):
            if layout[irow][icol] == ' ':
                layout[irow][icol] = 0   # free space
            elif layout[irow][icol] == '#':
                layout[irow][icol] = 1  # wall
            elif layout[irow][icol] == '&':
                layout[irow][icol] = 2  # player
            elif layout[irow][icol] == 'B':
                layout[irow][icol] = 3  # box
            elif layout[irow][icol] == '.':
                layout[irow][icol] = 4  # goal
            elif layout[irow][icol] == 'X':
                layout[irow][icol] = 5  # box on goal
        colsNum = len(layout[irow])
        #print('layout to number -> ',layout,' colsNum-> ',colsNum)
        if colsNum < maxColsNum:
            layout[irow].extend([1 for _ in range(maxColsNum-colsNum)]) # ถ้าจำนวน column ใน row นั้นๆ น้อยกว่า maxColumn ก็ทำให้ column นี้ เท่ากับ maxColumn โดยเพิ่มกำแพงเข้ามา
            #print('colsNum < maxColsNum -> extend : ',layout)
    return np.array(layout)


def PosOfPlayer(gameState):
    """Return the position of agent"""
    return tuple(np.argwhere(gameState == 2)[0])  # e.g. (2, 2)


def PosOfBoxes(gameState):
    """Return the positions of boxes"""
    return tuple(tuple(x) for x in np.argwhere((gameState == 3) | (gameState == 5)))  # e.g. ((2, 3), (3, 4), (4, 4), (6, 1), (6, 4), (6, 5))


def PosOfWalls(gameState):
    """Return the positions of walls"""
    return tuple(tuple(x) for x in np.argwhere(gameState == 1))  # e.g. like those above # return ตำแหน่งที่เป็นกำแพง ในลักษณะ พิกัด (row,column)


def PosOfGoals(gameState):
    """Return the positions of goals"""
    return tuple(tuple(x) for x in np.argwhere((gameState == 4) | (gameState == 5)))  # e.g. like those above # return ตำแหน่งที่เป็น goal ในลักษณะ พิกัด (row,column)


def isEndState(posBox):
    """Check if all boxes are on the goals (i.e. pass the game)"""
    return sorted(posBox) == sorted(posGoals)


def isLegalAction(action, posPlayer, posBox): #เช็คว่า เมื่อเดินแล้ว ไม่ชนกล่อง
    """Check if the given action is legal"""
    xPlayer, yPlayer = posPlayer
    if action[-1].isupper():  # the move was a push
        x1, y1 = xPlayer + 2 * action[0], yPlayer + 2 * action[1] # เข้า case นี้ ต่อเมื่อ ที่เดินไป ชนกล่อง ก็เลยมา get ค่า x,y ของกล่องที่ถูกดันแล้ว
    else:
        x1, y1 = xPlayer + action[0], yPlayer + action[1] # เข้า case นี้ต่อเมื่อ ที่เดินไป ไม่ชนกล่อง ดังนั้นเลยมา get ค่า x,y ที่เดินแล้วของ player
    return (x1, y1) not in posBox + posWalls # เช็คว่า ค่า x,y ที่ได้มาข้างบน ติดกล่องอื่นๆ


def legalActions(posPlayer, posBox): #return valid action ออกไป
    """Return all legal actions for the agent in the current game state"""
    allActions = [[-1, 0, 'u', 'U'], [1, 0, 'd', 'D'],
                  [0, -1, 'l', 'L'], [0, 1, 'r', 'R']]
    xPlayer, yPlayer = posPlayer
    legalActions = []
    for action in allActions:
        x1, y1 = xPlayer + action[0], yPlayer + action[1]
        if (x1, y1) in posBox:  # the move was a push
            action.pop(2)  # drop the little letter #เอาพิมเล็กออกจาก list ทำให้ action ที่เลื่อนกล่อง จะเป็น พิมใหญ่
        else:
            action.pop(3)  # drop the upper letter #เอาพิมใหญ่ออกจาก list ทำให้ action ที่ไม่เลื่อนกล่อง จะเป็น พิมเล็ก
        if isLegalAction(action, posPlayer, posBox): # ไปเช็คว่าที่เดินไป ติด obj อื่นๆไหม (ถ้าทับกล่อง จะไปเช็คช่องที่กล่องถูกดันว่าชน obj ไหม)
            legalActions.append(action)
        else:
            continue
    # e.g. ((0, -1, 'l'), (0, 1, 'R'))
    return tuple(tuple(x) for x in legalActions)


def updateState(posPlayer, posBox, action): # อัพเดท node 
    """Return updated game state after an action is taken"""
    xPlayer, yPlayer = posPlayer  # the previous position of player
    newPosPlayer = [xPlayer + action[0], yPlayer +
                    action[1]]  # the current position of player
    posBox = [list(x) for x in posBox]
    if action[-1].isupper():  # if pushing, update the position of box
        posBox.remove(newPosPlayer)
        posBox.append([xPlayer + 2 * action[0], yPlayer + 2 * action[1]])
    posBox = tuple(tuple(x) for x in posBox)
    newPosPlayer = tuple(newPosPlayer)
    return newPosPlayer, posBox


def isFailed(posBox):
    """This function used to observe if the state is potentially failed, then prune the search"""
    rotatePattern = [[0, 1, 2, 3, 4, 5, 6, 7, 8],
                     [2, 5, 8, 1, 4, 7, 0, 3, 6],
                     [0, 1, 2, 3, 4, 5, 6, 7, 8][::-1],
                     [2, 5, 8, 1, 4, 7, 0, 3, 6][::-1]]
    flipPattern = [[2, 1, 0, 5, 4, 3, 8, 7, 6],
                   [0, 3, 6, 1, 4, 7, 2, 5, 8],
                   [2, 1, 0, 5, 4, 3, 8, 7, 6][::-1],
                   [0, 3, 6, 1, 4, 7, 2, 5, 8][::-1]]
    allPattern = rotatePattern + flipPattern

    for box in posBox:
        if box not in posGoals:
            board = [(box[0] - 1, box[1] - 1), (box[0] - 1, box[1]), (box[0] - 1, box[1] + 1),
                     (box[0], box[1] - 1), (box[0],
                                            box[1]), (box[0], box[1] + 1),
                     (box[0] + 1, box[1] - 1), (box[0] + 1, box[1]), (box[0] + 1, box[1] + 1)]
            for pattern in allPattern:
                newBoard = [board[i] for i in pattern]
                if newBoard[1] in posWalls and newBoard[5] in posWalls:
                    return True
                elif newBoard[1] in posBox and newBoard[2] in posWalls and newBoard[5] in posWalls:
                    return True
                elif newBoard[1] in posBox and newBoard[2] in posWalls and newBoard[5] in posBox:
                    return True
                elif newBoard[1] in posBox and newBoard[2] in posBox and newBoard[5] in posBox:
                    return True
                elif newBoard[1] in posBox and newBoard[6] in posBox and newBoard[2] in posWalls and newBoard[3] in posWalls and newBoard[8] in posWalls:
                    return True
    return False


"""Implement all approcahes"""


def breadthFirstSearch(isRender=False):
    """Implement breadthFirstSearch approach"""
    beginBox = PosOfBoxes(gameState)
    beginPlayer = PosOfPlayer(gameState)
    print('ค่า beginBox (ตำแหน่ง 3 และ 5) \n',beginBox)
    print('ค่า beginPlayer (ตำแหน่ง 2) \n',beginPlayer)

    # e.g. ((2, 2), ((2, 3), (3, 4), (4, 4), (6, 1), (6, 4), (6, 5)))
    startState = (beginPlayer, beginBox)
    frontier = collections.deque([[startState]])  # store states
    actions = collections.deque([[0]])  # store actions

    print('ค่า frontier \n',frontier)
    print('ค่า actions \n',actions)

    exploredSet = set()

    while frontier:
        #print('print frontier : ',frontier) 1 node จะเก็บเส้นทางการเดินตั้งแต่เริ่มต้น ถึงปัจจุบัน
        #print('action : ',actions)
        node = frontier.popleft()
        node_action = actions.popleft()

        if isEndState(node[-1][-1]):
            print(node_action)
            print(','.join(node_action[1:]).replace(',', ''))
            return node_action[1:]

        if node[-1] not in exploredSet: #เอาจุดสุดท้ายของการเดินใน node นั้นๆ มาคิดต่อว่าจะเดินต่อไปทางไหนได้อีก
            exploredSet.add(node[-1])

            for action in legalActions(node[-1][0], node[-1][1]):
                # action e.g. (0, 1, 'r')

                newPosPlayer, newPosBox = updateState(
                    node[-1][0], node[-1][1], action)

                if isFailed(newPosBox):#อ่านแล้ว งง คือไรอะ??
                    continue

                frontier.append(node + [(newPosPlayer, newPosBox)]) #append ทั้งเส้นการเดินตั้งแต่จุดเริ่มต้นถึงปัจจุบัน + จุดใหม่ที่เดินได้ไปด้วย
                actions.append(node_action + [action[-1]]) # เหมือนกับ frontier เปะๆ แค่อยู่ในรูป action
 


def depthFirstSearch(isRender=False):
    """Implement depthFirstSearch approach"""
    beginBox = PosOfBoxes(gameState)
    beginPlayer = PosOfPlayer(gameState)

    startState = (beginPlayer, beginBox)
    frontier = collections.deque([[startState]])
    exploredSet = set()
    actions = [[0]]
    while frontier:
        node = frontier.pop()
        node_action = actions.pop()
        if isEndState(node[-1][-1]):
            print(','.join(node_action[1:]).replace(',', ''))
            return node_action[1:]
        if node[-1] not in exploredSet:
            exploredSet.add(node[-1])
            for action in legalActions(node[-1][0], node[-1][1]):
                newPosPlayer, newPosBox = updateState(
                    node[-1][0], node[-1][1], action)
                if isFailed(newPosBox):
                    continue
                frontier.append(node + [(newPosPlayer, newPosBox)])
                actions.append(node_action + [action[-1]])


def heuristic(posPlayer, posBox):
    """A heuristic function to calculate the overall distance between the else boxes and the else goals"""
    distance = 0
    completes = set(posGoals) & set(posBox)
    sortposBox = list(set(posBox).difference(completes))
    sortposGoals = list(set(posGoals).difference(completes))
    for i in range(len(sortposBox)):
        distance += (abs(sortposBox[i][0] - sortposGoals[i][0])) + \
            (abs(sortposBox[i][1] - sortposGoals[i][1]))
    return distance


def cost(actions):
    """A cost function"""
    return len([x for x in actions if x.islower()])


def uniformCostSearch(isRender=False):
    """Implement uniformCostSearch approach"""
    beginBox = PosOfBoxes(gameState)
    beginPlayer = PosOfPlayer(gameState)

    startState = (beginPlayer, beginBox)
    frontier = PriorityQueue()
    frontier.push([startState], 0)
    exploredSet = set()
    actions = PriorityQueue()
    actions.push([0], 0)
    while frontier:
        node = frontier.pop()
        node_action = actions.pop()
        if isEndState(node[-1][-1]):
            print(','.join(node_action[1:]).replace(',', ''))
            return node_action[1:]
        if node[-1] not in exploredSet:
            exploredSet.add(node[-1])
            Cost = cost(node_action[1:])
            for action in legalActions(node[-1][0], node[-1][1]):
                newPosPlayer, newPosBox = updateState(
                    node[-1][0], node[-1][1], action)
                if isFailed(newPosBox):
                    continue
                frontier.push(node + [(newPosPlayer, newPosBox)], Cost)
                actions.push(node_action + [action[-1]], Cost)


def aStarSearch(isRender=False):
    """Implement aStarSearch approach"""
    beginBox = PosOfBoxes(gameState)
    beginPlayer = PosOfPlayer(gameState)

    start_state = (beginPlayer, beginBox)
    frontier = PriorityQueue()
    frontier.push([start_state], heuristic(beginPlayer, beginBox))
    exploredSet = set()
    actions = PriorityQueue()
    actions.push([0], heuristic(beginPlayer, start_state[1]))
    while frontier:
        node = frontier.pop()
        node_action = actions.pop()
        if isEndState(node[-1][-1]):
            print(','.join(node_action[1:]).replace(',', ''))
            return node_action[1:]
        if node[-1] not in exploredSet:
            exploredSet.add(node[-1])
            Cost = cost(node_action[1:])
            for action in legalActions(node[-1][0], node[-1][1]):
                newPosPlayer, newPosBox = updateState(
                    node[-1][0], node[-1][1], action)
                if isFailed(newPosBox):
                    continue
                Heuristic = heuristic(newPosPlayer, newPosBox)
                frontier.push(
                    node + [(newPosPlayer, newPosBox)], Heuristic + Cost)
                actions.push(node_action + [action[-1]], Heuristic + Cost)


"""Read command"""


def readCommand(argv):
    from optparse import OptionParser

    parser = OptionParser()
    parser.add_option('-l', '--level', dest='sokobanLevels',
                      help='level of game to play', default='level1.txt')
    parser.add_option('-m', '--method', dest='agentMethod',
                      help='research method', default='bfs')
    args = dict()
    options, _ = parser.parse_args(argv)
    with open('sokobanLevels/'+options.sokobanLevels, "r") as f:
        layout = f.readlines()
    args['layout'] = layout
    args['method'] = options.agentMethod
    return args


if __name__ == '__main__':
    time_start = time.time()
    layout, method = readCommand(sys.argv[1:]).values()

    print("layout : ",layout)
    print("method :",method)

    gameState = transferToGameState(layout)
    print('ค่า gameState \n',gameState)

    posWalls = PosOfWalls(gameState)
    print('ค่า posWalls (ตำแหน่ง 1) \n',posWalls)

    posGoals = PosOfGoals(gameState)
    print('ค่า posGoals (ตำแหน่ง 4 และ 5) \n',posGoals)

    if method == 'astar':
        solution = aStarSearch()
    elif method == 'dfs':
        solution = depthFirstSearch()
    elif method == 'bfs':
        solution = breadthFirstSearch(isRender=True)
    elif method == 'ucs':
        solution = uniformCostSearch()
    else:
        raise ValueError('Invalid method.')


    # time_end = time.time()
    # print('Runtime of %s: %.2f second.' % (method, time_end-time_start))


    # # board = BoardManager(layout)
    # # renderer = Renderer(board).setCaption("Sokoban")
    # # renderer.render()
    # # solution = []

    # isButtonClick = False
    # while True:
    #     for event in pygame.event.get():
    #         if event.type == pygame.MOUSEBUTTONDOWN:
    #             isButtonClick = True
    #         if event.type == pygame.QUIT:
    #             pygame.quit()
    #     if isButtonClick == True and len(solution) > 0:
    #         act = solution.pop(0)
    #         board.movePlayer(act.lower())
    #         renderer.fromInstance(board).render()
    #         pygame.time.wait(50)
    #     elif isButtonClick == True and len(solution) == 0:
    #         renderer.showMessageBox(message='Sokoban solved!')
