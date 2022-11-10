import pygame
import numpy as np
import sys
import collections

wall = pygame.image.load("assets/images/wall.png")
box = pygame.image.load("assets/images/box.png")
box_on_target = pygame.image.load("assets/images/box_on_target.png")
player = pygame.image.load("assets/images/player.png")
space = pygame.image.load("assets/images/space.png")
target = pygame.image.load("assets/images/target.png")


DEFAULT_RENDER_MAP = {
    1: wall,
    0: space,
    3: box,
    4: target,
    2: player,
    5: box_on_target,
    6: player,
}

DEFAULT_BOX_SIZE = wall.get_width()
DEFAULT_SCREEN_SIZE = (600, 400)


class Renderer:
    def __init__(self, gameState):
        pygame.init()
        self.gameState = gameState
        self.renderMap = DEFAULT_RENDER_MAP
        self.renderBoxSize = DEFAULT_BOX_SIZE
        self.screen = None
        self.setDisplaySize(DEFAULT_SCREEN_SIZE)
        self.setCaption("Sokoban")
        self.posPlayer = self.xPosOfPlayer()
        self.posBoxes = self.xPosOfBoxes()
        self.posWalls = self.xPosOfWalls()
        self.posGoals = self.xPosOfGoals()

    def xPosOfPlayer(self):
        """Return the position of agent"""
        return tuple(np.argwhere(self.gameState == 2)[0])  # e.g. (2, 2)

    def xPosOfBoxes(self):
        """Return the positions of boxes"""
        return tuple(tuple(x) for x in np.argwhere((self.gameState == 3) | (self.gameState == 5)))  # e.g. ((2, 3), (3, 4), (4, 4), (6, 1), (6, 4), (6, 5))

    def xPosOfWalls(self):
        """Return the positions of walls"""
        return tuple(tuple(x) for x in np.argwhere(self.gameState == 1))  # e.g. like those above

    def xPosOfGoals(self):
        """Return the positions of goals"""
        return tuple(tuple(x) for x in np.argwhere((self.gameState == 4) | (self.gameState == 5)))

    def setDisplaySize(self, size: tuple[int, int]):
        self.screen = pygame.display.set_mode(size)
        return self

    def setCaption(self, name: str):
        pygame.display.set_caption(name)
        return self

    def setRenderMap(self, renderMap: dict[str, pygame.Surface]):
        self.renderMap = renderMap
        return self

    def setRenderBoxSize(self, size):
        self.renderBoxSize = size
        return self

    def fromInstance(self, board):
        self.board = board
        return self

    def clear(self):
        self.screen.fill((42, 42, 42))

    def showMessageBox(self, message: str):
        font = pygame.font.SysFont('arial', 60)
        # center
        text = font.render(message, True, (255, 255, 255))
        textRect = text.get_rect()
        textRect.centerx = self.screen.get_rect().centerx
        textRect.centery = self.screen.get_rect().centery
        self.screen.blit(text, textRect)
        pygame.display.update()

    def render(self, newPosPlayer, newPosBoxes):
        self.clear()
        for pos in self.posWalls:
            self.screen.blit(
                wall, (pos[1] * self.renderBoxSize, pos[0] * self.renderBoxSize))
        for pos in self.posGoals:
            self.screen.blit(
                target, (pos[1] * self.renderBoxSize, pos[0] * self.renderBoxSize))
        self.screen.blit(
            player, (newPosPlayer[0] * self.renderBoxSize, newPosPlayer[1] * self.renderBoxSize))
        for pos in newPosBoxes:
            self.screen.blit(
                box, (pos[0] * self.renderBoxSize, pos[1] * self.renderBoxSize))
        self.posPlayer = newPosPlayer
        self.posBoxes = newPosBoxes
        pygame.display.update()
        pygame.time.delay(5)
