# cython: profile=True
# -*- coding: utf-8 -*-
"""
anigma.games.tic - Tic Tac Toe
"""

import sys
import operator
from copy import deepcopy

from .abstract import AbstractGame
from anigmo.util import get_enemy

EMPTY = '-'
HEIGHT = 8
WIDTH = 8


class Reversi(AbstractGame):
    def __init__(self, board=[]):
        self.width = WIDTH
        self.height = HEIGHT
        self.board = board
        for i in xrange(self.width):
            try:
                self.board[i]
            except IndexError:
                self.board.append([EMPTY] * self.height)
                continue
            for k in xrange(self.height):
                try:
                    self.board[i][k]
                except IndexError:
                    self.board[i].append(EMPTY)
        if board == []:
            self.board[3][3] = 'O'
            self.board[4][4] = 'O'
            self.board[3][4] = 'X'
            self.board[4][3] = 'X'
        self.history = []

    def show(self):
        sys.stdout.write("-|")
        for k in xrange(self.width):
            sys.stdout.write("%d|" % (k))
        print
        for k in xrange(self.width + 1):
            sys.stdout.write('--')
        print
        for i in xrange(self.height):
            sys.stdout.write("%d|" % (i))
            for k in xrange(self.width):
                sys.stdout.write("%s|" % self.board[k][i])
            sys.stdout.write("\n")

    def isOnBoard(self, x, y):
        # Returns True if the coordinates are located on the board.
        return x >= 0 and x <= 7 and y >= 0 and y <= 7

    def isValidMove(self, player, xstart, ystart):
        # Returns False if the player's move on space xstart, ystart is invalid.
        # If it is a valid move, returns a list of spaces that would become the player's if they made a move here.
        if self.board[xstart][ystart] is not EMPTY or not self.isOnBoard(xstart, ystart):
            return False
        self.board[xstart][ystart] = player  # temporarily set the tile on the board.
        enemy = get_enemy(player)
        playersToFlip = []
        for xdirection, ydirection in [[0, 1], [1, 1], [1, 0], [1, -1], [0, -1], [-1, -1], [-1, 0], [-1, 1]]:
            x, y = xstart, ystart
            x += xdirection  # first step in the direction
            y += ydirection  # first step in the direction
            if self.isOnBoard(x, y) and self.board[x][y] == enemy:
                # There is a piece belonging to the other player next to our piece.
                x += xdirection
                y += ydirection
                if not self.isOnBoard(x, y):
                    continue
                while self.board[x][y] == enemy:
                    x += xdirection
                    y += ydirection
                    if not self.isOnBoard(x, y):  # break out of while loop, then continue in for loop
                        break
                if not self.isOnBoard(x, y):
                    continue
                if self.board[x][y] == player:
                    # There are pieces to flip over. Go in the reverse direction until we reach the original space, noting all the players along the way.
                    while True:
                        x -= xdirection
                        y -= ydirection
                        if x == xstart and y == ystart:
                            break
                        playersToFlip.append([x, y])
        self.board[xstart][ystart] = EMPTY  # restore the empty space
        if len(playersToFlip) == 0:  # If no players were flipped, this is not a valid move.
            return False
        return playersToFlip

    def available_moves(self, player):
        validMoves = []
        for x in xrange(self.width):
            for y in xrange(self.height):
                if self.isValidMove(player, x, y) is not False:
                    validMoves.append((x, y))
        return validMoves

    def complete(self):
        for column in self.board:
            if EMPTY in column:
                return False
        return True

    def winner(self):
        if not self.complete():
            return None
        win = self.heuristic('O')
        if win > 0:
            return 'O'
        elif win < 0:
            return 'X'

    def _get_board(self, player):
        """board that belong to a player"""
        return [k for k, v in enumerate(self.board) if v == player]

    def make_move(self, position, player):
        """place on square on the board"""
        enemy = get_enemy(player)
        self.history.append(deepcopy(self.board))
        self.board[position[0]][position[1]] = player
        #endpoints = []
        directions = [(1, 0), (1, 1), (0, 1), (-1, -1), (-1, 0), (-1, -1), (0, -1), (1, -1)]

        for direction in directions:
            current_point = position
            in_between = []
            #print("Checking new direction: " + str(direction))
            while True:
                try:
                    current_point = tuple(map(operator.add, current_point, direction))
                    #print("Attempting to check {0}".format(current_point))
                    square_id = self.board[current_point[0]][current_point[1]]
                    #print(" and found player ID {0}".format(square_id))
                except IndexError:
                    #print("Piece out of bounds, moving on")
                    break
                else:
                    if square_id == player:
                        #print("Endpoint found at {0}".format(current_point))
                        #endpoints.append(current_point)
                        for item in in_between:
                            self.board[item[0]][item[1]] = player
                        break
                    elif square_id == enemy:
                        in_between.append(current_point)
                        #print("Opposing player's piece found, continuing check...")
                        continue
                    else:
                        #print("Empty space reached, trying next direction.")
                        break

    def remove_move(self, position, player):
        self.board = deepcopy(self.history[-1])
        self.history.pop(-1)

    def reset(self):
        self.board = []
        for i in xrange(self.width):
                self.board.append([EMPTY] * self.height)

    def heuristic(self, player):
        value = 0
        enemy = get_enemy(player)
        for column in self.board:
            value += column.count(player)
            value -= column.count(enemy)
        return value

    def hash(self):
        return (hash(repr(self.board)),)

    def __repr__(self):
        return "Reversi(board=%s)" % str(self.board)
