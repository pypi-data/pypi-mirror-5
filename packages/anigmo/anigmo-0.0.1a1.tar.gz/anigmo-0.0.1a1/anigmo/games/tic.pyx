# cython: profile=True
# -*- coding: utf-8 -*-
"""
anigma.games.tic - Tic Tac Toe
"""

from .abstract import AbstractGame


cdef int popcount_kernighan(v):
    cdef int c = 0
    while v:
        v &= v - 1
        c += 1
    return c


class BitTic(AbstractGame):
    def __init__(self, board=[]):
        self.xBoard = 0
        self.oBoard = 0

        self.combinations = [
            0b111, 0b111000, 0b111000000,  # horizontal
            0b100100100, 0b10010010, 0b1001001,  # vertical
            0b100010001,  # h\
            0b1010100,  # h/
        ]

        self.values = [1, 4, 0]

    def show(self):
        def chunks(l, n):
            """ Yield successive n-sized chunks from l.
            """
            for i in xrange(0, len(l), n):
                yield l[i:i + n]
        printBoard = []
        for i in range(9):
            if (self.xBoard & 2**i) != 0:
                printBoard.append('X')
            elif (self.oBoard & 2**i) != 0:
                printBoard.append('O')
            else:
                printBoard.append('-')
        for c in chunks(printBoard, 3):
            print c

    @property
    def board(self):
        return self.xBoard | self.oBoard

    def available_moves(self):
        board = self.xBoard | self.oBoard
        moves = []
        for i in range(9):
            if (board & 2**i) == 0:
                moves.append(i)
        return moves

    def complete(self):
        return 511 == self.xBoard | self.oBoard

    def winner(self):
        for c in self.combinations:
            if c & self.xBoard == c:
                return 'X'
        for c in self.combinations:
            if c & self.oBoard == c:
                return 'O'
        return None

    def make_move(self, move, player):
        board = self.xBoard | self.oBoard
        pos = 1 << move
        if pos & board == 0:
            if player == 'O':
                self.oBoard |= pos
            else:
                self.xBoard |= pos
            return pos
        return -1

    def remove_move(self, move, player):
        if player == 'X':
            cBoard = self.xBoard
        else:
            cBoard = self.oBoard
        pos = 1 << move
        if pos & cBoard != 0:
            if player == 'O':
                self.oBoard ^= pos
            else:
                self.xBoard ^= pos
            return pos
        return -1

    def reset(self):
        self.xBoard = 0
        self.oBoard = 0

    def heuristic(self, player):
        value = 0
        xBoard = self.xBoard
        oBoard = self.oBoard
        values = self.values
        board = xBoard | oBoard
        for item in self.combinations:
            if board & item != 0:
                if item & xBoard == 0:
                    value += values[popcount_kernighan(item & oBoard) - 1]
                elif item & oBoard == 0:
                    value -= values[popcount_kernighan(item & xBoard) - 1]
        if player == 'O':
            return value
        else:
            return -value

    def hash(self):
        return hash(str(self.oBoard) + str(self.xBoard))


class Tic(AbstractGame):
    def __init__(self, board=[]):
        self.winning_combos = (
            [0, 1, 2], [3, 4, 5], [6, 7, 8],
            [0, 3, 6], [1, 4, 7], [2, 5, 8],
            [0, 4, 8], [2, 4, 6])

        self.values = [1, 4, 0]
        if len(board) == 0:
            self.board = [None for i in range(9)]
        elif len(board) == 2:
            pass
        elif len(board) == 9:
            self.board = board

    def show(self):
        for element in [self.board[i:i + 3]
                        for i in range(0, len(self.board), 3)]:
            print ['-' if e is None else e for e in element]

    def available_moves(self):
        """what spots are left empty?"""
        return [k for k, v in enumerate(self.board) if v is None]

    def available_combos(self, player):
        """what combos are available?"""
        return self.available_moves() + self._get_board(player)

    def complete(self):
        """is the game over?"""
        return None not in self.board

    def winner(self):
        for player in ('X', 'O'):
            board = self._get_board(player)
            for combo in self.winning_combos:
                win = True
                for pos in combo:
                    if pos not in board:
                        win = False
                if win:
                    return player
        return None

    def _get_board(self, player):
        """board that belong to a player"""
        return [k for k, v in enumerate(self.board) if v == player]

    def make_move(self, position, player):
        """place on square on the board"""
        self.board[position] = player

    def remove_move(self, position, player):
        self.board[position] = None

    def reset(self):
        self.board = [None for i in range(9)]

    def heuristic(self, player):
        value = 0
        for combo in self.winning_combos:
            members = [
                self.board[combo[0]],
                self.board[combo[1]],
                self.board[combo[2]]
            ]
            pCount = members.count(player)
            freeCount = members.count(None)
            opponenetCount = 3 - (pCount + freeCount)
            if opponenetCount == 0:
                value += self.values[pCount - 1]
            elif pCount == 0:
                value -= self.values[opponenetCount - 1]
        return value

    def hash(self):
        return (hash(frozenset(self.board)),)
