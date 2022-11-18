import sys
import collections
import numpy as np
import heapq
import time
from newRender import Renderer
from board import BoardManager
import pygame
import psutil,os
from renderSolution import renderSolution
from datetime import datetime

# test memory
# from guppy import hpy
# import numpy as np

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
    layout = [x.replace('\n', '') for x in layout]
    layout = [','.join(layout[i]) for i in range(len(layout))]
    layout = [x.split(',') for x in layout]
    maxColsNum = max([len(x) for x in layout])
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
        if colsNum < maxColsNum:
            layout[irow].extend([1 for _ in range(maxColsNum-colsNum)])
    return np.array(layout)


def PosOfPlayer(gameState):
    """Return the position of agent"""
    return tuple(np.argwhere(gameState == 2)[0])  # e.g. (2, 2)


def PosOfBoxes(gameState):
    """Return the positions of boxes"""
    return tuple(tuple(x) for x in np.argwhere((gameState == 3) | (gameState == 5)))  # e.g. ((2, 3), (3, 4), (4, 4), (6, 1), (6, 4), (6, 5))


def PosOfWalls(gameState):
    """Return the positions of walls"""
    return tuple(tuple(x) for x in np.argwhere(gameState == 1))  # e.g. like those above


def PosOfGoals(gameState):
    """Return the positions of goals"""
    return tuple(tuple(x) for x in np.argwhere((gameState == 4) | (gameState == 5)))  # e.g. like those above


def isEndState(posBox):
    """Check if all boxes are on the goals (i.e. pass the game)"""
    return sorted(posBox) == sorted(posGoals)


def isLegalAction(action, posPlayer, posBox):
    """Check if the given action is legal"""
    xPlayer, yPlayer = posPlayer
    if action[-1].isupper():  # the move was a push
        x1, y1 = xPlayer + 2 * action[0], yPlayer + 2 * action[1]
    else:
        x1, y1 = xPlayer + action[0], yPlayer + action[1]
    return (x1, y1) not in posBox + posWalls


def legalActions(posPlayer, posBox):
    """Return all legal actions for the agent in the current game state"""
    allActions = [[-1, 0, 'u', 'U'], [1, 0, 'd', 'D'],
                  [0, -1, 'l', 'L'], [0, 1, 'r', 'R']]
    xPlayer, yPlayer = posPlayer
    legalActions = []
    for action in allActions:
        x1, y1 = xPlayer + action[0], yPlayer + action[1]
        if (x1, y1) in posBox:  # the move was a push
            action.pop(2)  # drop the little letter
        else:
            action.pop(3)  # drop the upper letter
        if isLegalAction(action, posPlayer, posBox):
            legalActions.append(action)
        else:
            continue
    # e.g. ((0, -1, 'l'), (0, 1, 'R'))
    return tuple(tuple(x) for x in legalActions)

def legalNodes(currentNode,currentNodeAction):
    """Return all legal actions for the agent in the current game state"""
    allActions = [[-1, 0, 'u', 'U'], [1, 0, 'd', 'D'],
                  [0, -1, 'l', 'L'], [0, 1, 'r', 'R']]
    posPlayer=currentNode[-1][0]     
    posBox=currentNode[-1][1]
    xPlayer, yPlayer = posPlayer
    child_node=PriorityQueue()
    child_action=PriorityQueue()
    for action in allActions:
        x1, y1 = xPlayer + action[0], yPlayer + action[1]
        if (x1, y1) in posBox:  # the move was a push
            action.pop(2)  # drop the little letter
        else:
            action.pop(3)  # drop the upper letter
        if isLegalAction(action, posPlayer, posBox):
            newPosPlayer, newPosBox = updateState(posPlayer, posBox, action)
            if isFailed(newPosBox):
                continue
            Heuristic = heuristic(newPosPlayer, newPosBox)
            Cost = cost(currentNodeAction[1:])
            child_node.push((newPosPlayer, newPosBox),Heuristic+Cost)
            child_action.push(action,Heuristic+Cost)
        else:
            continue
    # e.g. ((0, -1, 'l'), (0, 1, 'R'))
    return child_node,child_action


def updateState(posPlayer, posBox, action):
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

def breadthFirstSearch(renderSearch=False):
    """Implement breadthFirstSearch approach"""
    beginBox = PosOfBoxes(gameState)
    beginPlayer = PosOfPlayer(gameState)

    # e.g. ((2, 2), ((2, 3), (3, 4), (4, 4), (6, 1), (6, 4), (6, 5)))
    startState = (beginPlayer, beginBox)
    frontier = collections.deque([[startState]])  # store states
    actions = collections.deque([[0]])  # store actions
    exploredSet = set()
    while frontier:
        node = frontier.popleft()
        node_action = actions.popleft()
        if isEndState(node[-1][-1]):
            print(','.join(node_action[1:]).replace(',', ''))
            return node_action[1:]
        if node[-1] not in exploredSet:
            exploredSet.add(node[-1])
            for action in legalActions(node[-1][0], node[-1][1]):
                newPosPlayer, newPosBox = updateState(
                    node[-1][0], node[-1][1], action)
                if(renderSearch):
                    renderer.render(newPosPlayer, newPosBox)
                if isFailed(newPosBox):
                    continue
                frontier.append(node + [(newPosPlayer, newPosBox)])
                actions.append(node_action + [action[-1]])


def depthFirstSearch(renderSearch=False):
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
                if(renderSearch):
                    renderer.render(newPosPlayer, newPosBox)
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


def uniformCostSearch(renderSearch=False):
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
                if(renderSearch):
                    renderer.render(newPosPlayer, newPosBox)
                if isFailed(newPosBox):
                    continue
                frontier.push(node + [(newPosPlayer, newPosBox)], Cost)
                actions.push(node_action + [action[-1]], Cost)


def aStarSearch(renderSearch=False):
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
                if(renderSearch):
                    renderer.render(newPosPlayer, newPosBox)
                if isFailed(newPosBox):
                    continue
                Heuristic = heuristic(newPosPlayer, newPosBox)
                frontier.push(
                    node + [(newPosPlayer, newPosBox)], Heuristic + Cost)
                actions.push(node_action + [action[-1]], Heuristic + Cost)

# เหมือนกับ Astar แค่ลบ Cost ทิ้ง ตอนนี้เหมือนอมันจะติดลูป
def greedyBestFirstSearch(renderSearch=False):
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
            for action in legalActions(node[-1][0], node[-1][1]):
                newPosPlayer, newPosBox = updateState(
                    node[-1][0], node[-1][1], action)
                if(renderSearch):
                    renderer.render(newPosPlayer, newPosBox)
                if isFailed(newPosBox):
                    continue
                Heuristic = heuristic(newPosPlayer, newPosBox)
                frontier.push(
                    node + [(newPosPlayer, newPosBox)], Heuristic )
                actions.push(node_action + [action[-1]], Heuristic )


def iterative_deepening_a_star(renderSearch=False):
    beginBox = PosOfBoxes(gameState)
    beginPlayer = PosOfPlayer(gameState)
    threshold = heuristic(beginPlayer, beginBox)

    startState = [(beginPlayer, beginBox)]
    startAction=[0]
    while True:
        # print("Iteration with threshold: " + str(threshold))
        distance,solution = iterative_deepening_a_star_rec(startState,startAction, 0, threshold,renderSearch)
        if distance == float("inf"):
            # Node not found and no more nodes to visit
            return -1
        elif distance < 0:
            # if we found the node, the function returns the negative distance
            # print("Found the node we're looking for!")
            return solution
        else:
            # if it hasn't found the node, it returns the (positive) next-bigger threshold
            threshold = distance

def iterative_deepening_a_star_rec( node,node_action, distance, threshold,renderSearch):
    estimate = distance+heuristic(node[-1][0], node[-1][1])
    # print('estimate(f(n)): ',distance,'+',heuristic(node[-1][0], node[-1][1]),'=',estimate)
    # print('threshold:',threshold)
    
    if estimate > threshold:
        # print("Breached threshold with heuristic: " + str(estimate))
        return estimate,node_action[1:]
    if isEndState(node[-1][-1]):
        # We have found the goal node we we're searching for
        print(','.join(node_action[1:]).replace(',', ''))
        return -100,node_action[1:]
    
    min = float("inf")

    child_node,child_action=legalNodes(node,node_action)
    # ...then, for all neighboring nodes....
    for i in range(len(child_node.Heap)):
        new_node=child_node.pop()
        new_action=child_action.pop()
        if new_node not in node :
            node.append(new_node)
            node_action.append(new_action[-1])
            Cost = cost(node_action[1:])
            # print('Cost(g(n)): ',Cost)
            if(renderSearch):
                renderer.render(new_node[0], new_node[1])
            t, solution = iterative_deepening_a_star_rec(node,node_action, Cost, threshold,renderSearch)
            if t < 0:
                return t, solution
            elif t < min:
                min = t
            node.pop()
            node_action.pop()
    return min, node_action[1:]

"""Read command"""


def readCommand(argv):
    from optparse import OptionParser

    parser = OptionParser()
    parser.add_option('-l', '--level', dest='sokobanLevels',
                      help='level of game to play', default='level1.txt')
    parser.add_option('-m', '--method', dest='agentMethod',
                      help='research method', default='bfs')
    parser.add_option('-s', '--search', dest='search', action="store_true",
                      help='render searching with pygame', default=False)
    parser.add_option('-r', '--result', dest='result', action="store_true",
                      help='render result with pygame', default=False)
    args = dict()
    options, _ = parser.parse_args(argv)
    with open('sokobanLevels/'+options.sokobanLevels, "r") as f:
        layout = f.readlines()
    args['level'] = options.sokobanLevels
    args['layout'] = layout
    args['method'] = options.agentMethod
    args['renderSearch'] = options.search
    args['renderResult'] = options.result

    return args

"""Create Text result file"""

def createTextResultFile(csvFormat=False):

    # write solution detail to file (default format)
    resultDir = "results"
    filename = f"solution-{method}-{level}"
    relPath = os.path.join(resultDir, filename)
    with open(relPath, "w") as f:
        now = datetime.now()
        nowStrft = now.strftime("%d/%m/%Y, %H:%M:%S")
        f.write(f"Finished at: {nowStrft}\n")
        f.write(f"Number of action: {numAction}\n")
        f.write(f"Action : {','.join(solution).replace(',', '')} \n")
        f.write(f"Time usage: {timeUsage} seconds\n")
        f.write(f"Memory usage: {memoryUsage} bytes\n")
        f.write("\n")

    if csvFormat == False:
        return

    # write solution detail to file (csv format)
    methods_format = {'astar':'A*','dfs':'DFS','bfs':'BFS','idastar':'IDA*'}
    resultDir = "results_csv"
    filename = f"solution-{method}-{level}"
    relPath = os.path.join(resultDir, filename)
    with open(relPath, "w") as f:
        f.write(methods_format[method]+"\t")
        f.write(str(numAction)+"\t")
        f.write(str(round(timeUsage, 2))+"\t")
        f.write("0"+"\t")
        f.write(str(round(memoryUsage, 2)))


if __name__ == '__main__':
    p = psutil.Process()
    time_start = time.time()

    level,layout, method, renderSearch, renderResult = readCommand(sys.argv[1:]).values()
    gameState = transferToGameState(layout)
    posWalls = PosOfWalls(gameState)
    posGoals = PosOfGoals(gameState)
    solution = []

    if(renderSearch): renderer = Renderer(gameState)
    
    if method == 'astar':
        solution = aStarSearch(renderSearch)
    elif method == 'dfs':
        solution = depthFirstSearch(renderSearch)
    elif method == 'bfs':
        solution = breadthFirstSearch(renderSearch)
    elif method == 'ucs':
        solution = uniformCostSearch(renderSearch)
    elif method == 'gbfs':
        solution = greedyBestFirstSearch(renderSearch)
    elif method=='idastar':
        solution = iterative_deepening_a_star(renderSearch)
    else:
        raise ValueError('Invalid method.')
    time_end = time.time()

    timeUsage = time_end-time_start
    memoryUsage = (p.memory_info().peak_wset) / 1024**2
    numAction = len(','.join(solution).replace(',', ''))
    print('Number of Action:',numAction)
    print('Runtime of %s: %.2f second.' % (method,timeUsage ))
    print('Peak Memory Usage:',memoryUsage,'MB')

    createTextResultFile(csvFormat=True)

    if renderResult: renderSolution(layout, solution)
