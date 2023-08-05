# cython: profile=True
# -*- coding: utf-8 -*-
"""
anigma.games.connect4 - Connect4
"""

from .abstract import AbstractGame
from anigmo.core import MAX
#from anigmo.util import popcount_kernighan, popcount32_table16, popcount_hybrid

import sys
NUMPY = True
try:
    from numpy import *
except ImportError:
    try:
        import numpypy
        from numpy import *
    except ImportError:
        NUMPY = False


#import showme

EMPTY = '-'
EMPTY2 = 0
HEIGHT = 6
WIDTH = 7
"""board = self.xBoard | self.oBoard
        moves = []
        for i, pos in enumerate(COLUMNS):
            if pos & board != pos:
                moves.append(i)
        return moves"""

COLUMNS = (63, 8064, 1032192, 132120576, 16911433728, 2164663517184, 277076930199552)


cdef int popcount_kernighan(v):
    cdef int c = 0
    while v:
        v &= v - 1
        c += 1
    return c


class BaseConnect4(AbstractGame):
    def moveOrdering(self, moves):
        moves = [x - 3 for x in moves]
        moves.sort(key=lambda x: abs(int(x)))
        return [x + 3 for x in moves]


class Connect4(BaseConnect4):
    interface = {
        "normal": True,
        "heuristic": True,
        "transposition": True,
        "initial-board": True,
        "custom board-size": False,
        "move ordering": True,
        "enemy": True,
        "opennig book": False,
    }

    def __init__(self, board=[]):
        self.width = WIDTH
        self.height = HEIGHT
        self.board = board
        self.values = [1, 8, 128, 256, MAX]
        self.combinations = []
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
        # horizontal
        for x in xrange(WIDTH - 3):
            for y in xrange(HEIGHT):
                self.combinations.append(
                    [x, y, x + 1, y, x + 2, y, x + 3, y])
        # vertical
        for x in xrange(WIDTH):
            for y in xrange(HEIGHT - 3):
                self.combinations.append(
                    [x, y, x, y + 1, x, y + 2, x, y + 3])
        # diagonal \
        for x in xrange(WIDTH - 3):
            for y in xrange(3, HEIGHT):
                self.combinations.append(
                    [x, y, x + 1, y - 1, x + 2, y - 2, x + 3, y - 3])
        # diagonal /
        for x in xrange(WIDTH - 3):
            for y in xrange(HEIGHT - 3):
                self.combinations.append(
                    [x, y, x + 1, y + 1, x + 2, y + 2, x + 3, y + 3])

    def init(self):
        count = 0
        for x in xrange(self.width):
            for y in xrange(self.height):
                if self.board[x][y] == 'O':
                    count += 1
                elif self.board[x][y] == 'X':
                    count -= 1
        if count == 0:
            self.startPlayer = 'O'
        else:
            self.startPlayer = 'X'

    def show(self):
        for k in xrange(self.width):
            sys.stdout.write("%d|" % (k + 1))
        print
        for k in xrange(self.width):
            sys.stdout.write('--')
        print
        for i in xrange(self.height):
            for k in xrange(self.width):
                sys.stdout.write("%s|" % self.board[k][i])
            sys.stdout.write("\n")
        #sys.stdout.write("\n")
        #sys.stdout.write("\n")

    def available_moves(self):
        return [k for k in xrange(WIDTH) if EMPTY in self.board[k]]

    def complete(self):
        if len(self.available_moves()) == 0:
            return True
        return False

    def winner(self):
        board = self.board
        #return reduce(
        #    lambda x, y: x + heuValue(game, [board[y[0]][y[1]],
        #    board[y[2]][y[3]], board[y[4]][y[5]], board[y[6]][y[7]]],
        #    [y[1], y[3], y[5], y[7]]), heuristics, 0)
        for group in self.combinations:
            one = board[group[0]][group[1]]
            if one != EMPTY:
                if one == board[group[2]][group[3]] \
                       == board[group[4]][group[5]] \
                       == board[group[6]][group[7]]:
                    return one

        return None

    def getLowest(self, column):
        board = self.board
        for y in xrange(HEIGHT - 1, -1, -1):
            if board[column][y] == EMPTY:
                return y
        return -1

    def make_move(self, column, player):
        lowest = self.getLowest(column)
        if lowest != -1:
            self.board[column][lowest] = player
        return lowest

    def remove_move(self, column, player):
        top = self.getLowest(column) + 1
        self.board[column][top] = EMPTY

    def reset(self):
        self.board = []
        for i in xrange(self.width):
                self.board.append([EMPTY] * self.height)

    def heuristic(self, player):
        board = self.board
        started = self.startPlayer == player
        values = self.values
        value = 0

        for group in self.combinations:
            members = [
                board[group[0]][group[1]],
                board[group[2]][group[3]],
                board[group[4]][group[5]],
                board[group[6]][group[7]]
            ]
            pCount = members.count(player)
            fCount = members.count(EMPTY)
            opponentCount = 4 - (pCount + fCount)

            if (opponentCount > 0 and pCount > 0) or fCount == 4:
                pass
            elif opponentCount > 0:
                if opponentCount == 3:
                    i = members.index(EMPTY)
                    row = group[2 * i + 1]
                    #if row == 0 or board[i][row - 1] == EMPTY:
                    #    pass
                    if started:
                        if row % 2 == 0:
                            value += -values[3]
                        else:
                            value += -values[2]
                    else:
                        if row % 2 == 0:
                            value += -values[2]
                        else:
                            value += -values[3]
                else:
                    value += -values[opponentCount - 1]
            else:
                if pCount == 3:
                    i = members.index(EMPTY)
                    row = group[2 * i + 1]
                    #if row == 0 or board[i][row - 1] != EMPTY:
                    #    pass
                    if started:
                        if row % 2 == 0:
                            value += values[2]
                        else:
                            value += values[3]
                    else:
                        if row % 2 == 0:
                            value += values[3]
                        else:
                            value += values[2]
                else:
                    value += values[pCount - 1]
        return value

    def hash(self):
        return (hash(repr(self.board)),)


if NUMPY:
    # BETA STATUS
    class NumPyConnect4(Connect4):
        def __init__(self, board=[]):
            self.width = WIDTH
            self.height = HEIGHT
            self.board = zeros((6, 7))
            self.values = [1, 8, 128, 256, MAX]
            self.combinations = []
            # horizontal
            for x in xrange(WIDTH - 3):
                for y in xrange(HEIGHT):
                    self.combinations.append([
                        array([[y, y, y, y]]),
                        array([[x, x + 1, x + 2, x + 3]])
                    ])
            # vertical
            for x in xrange(WIDTH):
                for y in xrange(HEIGHT - 3):
                    self.combinations.append([
                        array([[y, y + 1, y + 2, y + 3]]),
                        array([[x, x, x, x]])
                    ])
            # diagonal \
            for x in xrange(WIDTH - 3):
                for y in xrange(3, HEIGHT):
                    self.combinations.append([
                        array([[y, y - 1, y - 2, y - 3]]),
                        array([[x, x + 1, x + 2, x + 3]])
                    ])
            # diagonal /
            for x in xrange(WIDTH - 3):
                for y in xrange(HEIGHT - 3):
                    self.combinations.append([
                        array([[y, y + 1, y + 2, y + 3]]),
                        array([[x, x + 1, x + 2, x + 3]])
                    ])
            print self.combinations
            #self.combinations = array(self.combinations)

        def init(self):
            count = 0
            for x in xrange(self.width):
                for y in xrange(self.height):
                    if self.board[y, x] == 1:
                        count += 1
                    elif self.board[y, x] == -1:
                        count -= 1
            if count == 0:
                self.startPlayer = 1
            else:
                self.startPlayer = -1

        def show(self):
            for k in xrange(self.width):
                sys.stdout.write(" %d |" % (k + 1))
            print
            for k in xrange(self.width):
                sys.stdout.write('----')
            print
            for row in self.board:
                for column in row:
                    sys.stdout.write(" %d |" % column)
                sys.stdout.write("\n")
            #sys.stdout.write("\n")
            #sys.stdout.write("\n")

        def available_moves(self):
            return [k for k in xrange(WIDTH) if EMPTY2 == self.board[0, k]]

        def complete(self):
            if len(self.available_moves()) == 0:
                return True
            return False

        #@profile
        def winner(self):
            board = self.board
            #return reduce(
            #    lambda x, y: x + heuValue(game, [board[y[0]][y[1]],
            #    board[y[2]][y[3]], board[y[4]][y[5]], board[y[6]][y[7]]],
            #    [y[1], y[3], y[5], y[7]]), heuristics, 0)
            for group in self.combinations:
                #print type(board)
                #print type(group)
                g = board[group]
                g = g.tolist()[0]
                #print g
                one = g[0]
                if one != EMPTY2:
                    if one == g[1] \
                           == g[2] \
                           == g[3]:
                        return one

            return None

        def getLowest(self, column):
            board = self.board
            for y in xrange(HEIGHT - 1, -1, -1):
                if board[y, column] == EMPTY2:
                    return y
            return -1

        def make_move(self, column, player):
            lowest = self.getLowest(column)
            if lowest != -1:
                self.board[lowest, column] = player
            return lowest

        def remove_move(self, column, player):
            top = self.getLowest(column) + 1
            self.board[top, column] = EMPTY2

        def reset(self):
            self.board = zeros((6, 7))

        def heuristic(self, player):
            board = self.board
            started = self.startPlayer == player
            values = self.values
            value = 0

            for group in self.combinations:
                members = board[group].tolist()[0]
                pCount = members.count(player)
                fCount = members.count(EMPTY2)
                opponentCount = 4 - (pCount + fCount)

                if (opponentCount > 0 and pCount > 0) or fCount == 4:
                    pass
                elif opponentCount > 0:
                    if opponentCount == 3:
                        i = members.index(EMPTY2)
                        #print repr(group[0][0,i])
                        row = group[0][0, i]
                        #if row == 0 or board[i][row - 1] == EMPTY2:
                        #    pass
                        if started:
                            if row % 2 == 0:
                                value += -values[3]
                            else:
                                value += -values[2]
                        else:
                            if row % 2 == 0:
                                value += -values[2]
                            else:
                                value += -values[3]
                    else:
                        value += -values[opponentCount - 1]
                else:
                    if pCount == 3:
                        i = members.index(EMPTY2)
                        #print repr(group[0][0,i])
                        row = group[0][0, i]
                        #if row == 0 or board[i][row - 1] != EMPTY2:
                        #    pass
                        if started:
                            if row % 2 == 0:
                                value += values[2]
                            else:
                                value += values[3]
                        else:
                            if row % 2 == 0:
                                value += values[3]
                            else:
                                value += values[2]
                    else:
                        value += values[pCount - 1]
            return value


class BitConnect4(BaseConnect4):
    """
    .  .  .  .  .  .  .  TOP
    5 12 19 26 33 40 47
    4 11 18 25 32 39 46
    3 10 17 24 31 38 45
    2  9 16 23 30 37 44
    1  8 15 22 29 36 43
    0  7 14 21 28 35 42  BOTTOM
    BITS:
    47 46 45 44 ... 3 2 1 0
    """
    def __init__(self, board=[]):
        self.width = WIDTH
        self.height = HEIGHT
        self.values = [1, 8, 128, 256, MAX]
        if board != []:
            self.xBoard = 1 << 1
            self.oBoard = 1 << 1
            for i in xrange(WIDTH - 1, -1, -1):
                for k in xrange(HEIGHT - 1, -1, -1):
                    if board[i][k] == 'X':
                        self.xBoard |= 1
                    elif board[i][k] == 'O':
                        self.oBoard |= 1
                    self.xBoard = self.xBoard << 1
                    self.oBoard = self.oBoard << 1
                self.xBoard = self.xBoard << 1
                self.oBoard = self.oBoard << 1
            self.xBoard = self.xBoard >> 2
            self.oBoard = self.oBoard >> 2
            self.xBoard = self.xBoard & 140737488355327
            self.oBoard = self.oBoard & 140737488355327
        else:
            self.xBoard = 0
            self.oBoard = 0
        self.combinations = []
        #horizontal
        for x in xrange(WIDTH - 3):
            for y in xrange(HEIGHT):
                one = (1 << (7 * x)) << y
                two = (1 << (7 * (x + 1))) << y
                three = (1 << (7 * (x + 2))) << y
                four = (1 << (7 * (x + 3))) << y
                self.combinations.append(one | two | three | four)
        # vertical
        for x in xrange(WIDTH):
            for y in xrange(HEIGHT - 3):
                one = (1 << (7 * x)) << y
                two = (1 << (7 * x)) << (y + 1)
                three = (1 << (7 * x)) << (y + 2)
                four = (1 << (7 * x)) << (y + 3)
                self.combinations.append(one | two | three | four)
        # diagonal \
        for x in xrange(WIDTH - 3):
            for y in xrange(3, HEIGHT):
                one = (1 << (7 * x)) << y
                two = (1 << (7 * (x + 1))) << (y - 1)
                three = (1 << (7 * (x + 2))) << (y - 2)
                four = (1 << (7 * (x + 3))) << (y - 3)
                self.combinations.append(one | two | three | four)
        # diagonal /
        for x in xrange(WIDTH - 3):
            for y in xrange(HEIGHT - 3):
                one = (1 << (7 * x)) << y
                two = (1 << (7 * (x + 1))) << (y + 1)
                three = (1 << (7 * (x + 2))) << (y + 2)
                four = (1 << (7 * (x + 3))) << (y + 3)
                self.combinations.append(one | two | three | four)

    def show(self):
        def chunks(l, n):
            """ Yield successive n-sized chunks from l.
            """
            for i in xrange(0, len(l), n):
                yield l[i:i + n]

        import pprint
        stri = bin(self.xBoard).lstrip('0b')
        stri = "0" * (49 - len(stri)) + stri
        b = list(chunks(list(stri), 7))
        xb = zip(*b[::-1])

        stri = bin(self.oBoard).lstrip('0b')
        stri = "0" * (49 - len(stri)) + stri
        b = list(chunks(list(stri), 7))
        ob = zip(*b[::-1])

        board = []
        for x, o in zip(xb, ob):
            column = []
            for xi, oi in zip(x, o):
                if xi == '1':
                    column.append('X')
                elif oi == '1':
                    column.append('O')
                else:
                    column.append('-')
            board.append(column)
        print "   1    2    3    4    5    6    7"
        pprint.pprint(board)

    @property
    def board(self):
        return self.xBoard | self.oBoard

    def currentDepth(self):
        return popcount_kernighan(self.board)

    def available_moves(self):
        board = self.xBoard | self.oBoard
        moves = []
        for i, pos in enumerate(COLUMNS):
            if pos & board != pos:
                moves.append(i)
        return moves

    def complete(self):
        # 283691315109952 top row full, since not needed
        return 279258638311359 == self.xBoard | self.oBoard

    def winner(self):
        xBoard = self.xBoard
        x = xBoard & (xBoard >> 6)
        if (x & (x >> 2 * 6)):
            return 'X'
        x = xBoard & (xBoard >> 7)
        if (x & (x >> 2 * 7)):
            return 'X'
        x = xBoard & (xBoard >> 8)
        if (x & (x >> 2 * 8)):
            return 'X'
        x = xBoard & (xBoard >> 1)
        if (x & (x >> 2)):
            return 'X'

        oBoard = self.oBoard
        o = oBoard & (oBoard >> 6)
        if (o & (o >> 2 * 6)):
            return 'O'
        o = oBoard & (oBoard >> 7)
        if (o & (o >> 2 * 7)):
            return 'O'
        o = oBoard & (oBoard >> 8)
        if (o & (o >> 2 * 8)):
            return 'O'
        o = oBoard & (oBoard >> 1)
        if (o & (o >> 2)):
            return 'O'

        return None

    def make_move(self, column, player):
        board = self.xBoard | self.oBoard
        pos = 1 << column * 7  # move to right column
        for i in xrange(HEIGHT):
            if pos & board == 0:
                if player == 'O':
                    self.oBoard |= pos
                else:
                    self.xBoard |= pos
                return pos
            else:
                pos = pos << 1
        return -1

    def remove_move(self, column, player):
        if player == 'X':
            cBoard = self.xBoard
        else:
            cBoard = self.oBoard
        pos = (1 << (column + 1) * 7) >> 1
        for i in xrange(HEIGHT - 1, -1, -1):
            if pos & cBoard != 0:
                if player == 'O':
                    self.oBoard ^= pos
                else:
                    self.xBoard ^= pos
                return pos
            else:
                pos = pos >> 1

        if player == 'X':
            self.xBoard ^= pos
        else:
            self.oBoard ^= pos

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
        return (
            hash(
                repr(self._mirrorBoard(self.oBoard)) + 'x' +
                repr(self._mirrorBoard(self.xBoard))),
            hash(repr(self.oBoard) + 'x' + repr(self.xBoard))
        )

    def fliphash(self):
        return (
            hash(
                repr(self._mirrorBoard(self.xBoard)) + 'x' +
                repr(self._mirrorBoard(self.oBoard))
            ),
            hash(repr(self.xBoard) + 'x' + repr(self.oBoard)),
        )

    def _mirrorBoard(self, board):
        one = (board & 127) << 42
        two = (board & (127 << 7)) << 28
        three = (board & (127 << 14)) << 14
        four = (board & (127 << 21))
        five = (board & (127 << 28)) >> 14
        six = (board & (127 << 35)) >> 28
        seven = (board & (127 << 42)) >> 42
        return one | two | three | four | five | six | seven
