import sys
import collections
import numpy as np
import heapq
import time
from render import Renderer
from board import BoardManager
import pygame


def renderSolution(layout, solution):
    board = BoardManager(layout)
    renderer = Renderer(board).setCaption("Sokoban")
    renderer.render()
    renderer.showMessageBox(
        message='K-Engine finished | Click to show solution')
    isButtonClick = False
    while True:
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                isButtonClick = True
            if event.type == pygame.QUIT:
                pygame.quit()
        if isButtonClick == True and len(solution) > 0:
            act = solution.pop(0)
            board.movePlayer(act.lower())
            renderer.fromInstance(board).render()
            pygame.time.wait(50)
        elif isButtonClick == True and len(solution) == 0:
            renderer.showMessageBox(message='Sokoban solved!')
