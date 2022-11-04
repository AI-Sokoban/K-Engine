import pygame


class BoardManager:
    def __init__(self, board):
        for b in range(len(board)):
            board[b] = list(board[b].replace('\n', ''))

        self.board_lst = board
        self.obj = ['B', 'X', '#']
        self.block = ['B', 'X']
        return

    def __str__(self):
        return self.getBoard()

    def getBoard(self):
        board_lst = []
        for bb in self.board_lst:
            board_lst.append("".join(bb))
        board_lst = [''] + board_lst + ['']
        return "\n".join(board_lst)

    def getBoardList(self):
        return self.board_lst

    def updateBoard(self, new_board):
        self.board_lst = new_board

    def playerPosition(self):
        for i in range(len(self.board_lst)):
            for j in range(len(self.board_lst[i])):
                if self.board_lst[i][j] == '&' or self.board_lst[i][j] == '@':
                    return i, j

    def genNewBoard(self, board):
        board_ = board.split('\n')[1:-1]

        for b in range(len(board_)):
            board_[b] = list(board_[b])

        self.board_lst = board_

    def movePlayer(self, act):
        if act == 'u':
            return self.up()
        elif act == 'd':
            return self.down()
        elif act == 'l':
            return self.left()
        elif act == 'r':
            return self.right()
        else:
            return False

    def up(self):
        i, j = self.playerPosition()
        boardlist = self.getBoardList()

        # move กล่อง ถ้ามี
        if boardlist[i-1][j] in self.block:
            boardlist[i-1][j] = "." if boardlist[i-1][j] == "X" else " "
            boardlist[i-2][j] = "X" if boardlist[i-2][j] == "." else "B"

        # move player
        boardlist[i-1][j] = "@" if boardlist[i-1][j] == "." else "&"
        boardlist[i][j] = "." if boardlist[i][j] == "@" else " "

        self.updateBoard(boardlist)
        return True

    def down(self):
        i, j = self.playerPosition()
        boardlist = self.getBoardList()

        # move กล่อง ถ้ามี
        if boardlist[i+1][j] in self.block:
            boardlist[i+1][j] = "." if boardlist[i+1][j] == "X" else " "
            boardlist[i+2][j] = "X" if boardlist[i+2][j] == "." else "B"

        # move player
        boardlist[i+1][j] = "@" if boardlist[i+1][j] == "." else "&"
        boardlist[i][j] = "." if boardlist[i][j] == "@" else " "

        self.updateBoard(boardlist)
        return True

    def left(self):
        i, j = self.playerPosition()
        boardlist = self.getBoardList()

        # move กล่อง ถ้ามี
        if boardlist[i][j-1] in self.block:
            boardlist[i][j-1] = "." if boardlist[i][j-1] == "X" else " "
            boardlist[i][j-2] = "X" if boardlist[i][j-2] == "." else "B"

        # move player
        boardlist[i][j-1] = "@" if boardlist[i][j-1] == "." else "&"
        boardlist[i][j] = "." if boardlist[i][j] == "@" else " "

        self.updateBoard(boardlist)
        return True

    def right(self):
        i, j = self.playerPosition()
        boardlist = self.getBoardList()

        # move กล่อง ถ้ามี
        if boardlist[i][j+1] in self.block:
            boardlist[i][j+1] = "." if boardlist[i][j+1] == "X" else " "
            boardlist[i][j+2] = "X" if boardlist[i][j+2] == "." else "B"

        # move player
        boardlist[i][j+1] = "@" if boardlist[i][j+1] == "." else "&"
        boardlist[i][j] = "." if boardlist[i][j] == "@" else " "

        self.updateBoard(boardlist)
        return True
