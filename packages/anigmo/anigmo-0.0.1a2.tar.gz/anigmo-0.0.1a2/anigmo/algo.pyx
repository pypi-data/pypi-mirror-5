# cython: profile=True
# -*- coding: utf-8 -*-
"""
anigmo.algo - the central algorithms to the AI
"""

from .util import get_enemy, MAX

from transpo import getEntry, storeEntry, LOWERBOUND, UPPERBOUND, EXACT

"""
Does it have moveOrdering?
Hashing
Quiesce search
activate these things and than check if there are available just skip if not with notification.
"""


def quiesce(self, node, player, alpha, beta, depth):
        stand_pat = node.heuristic()
        if stand_pat >= beta:
            return beta
        elif stand_pat > alpha:
            alpha = stand_pat
        elif depth == 0:
            return stand_pat

        c = self.check_base(node, player)
        if c is not None:
            return c

        opposite = get_enemy(player)
        forced_moves = []
        for move in node.available_moves:
            node.make_move(move, opposite)
            if node.winner() == opposite:
                forced_moves.append(move)
            node.remove_bit_move(move, opposite)

        for move in forced_moves:
            node.make_move(move, player)
            val = -self.quiesce(node, opposite, -beta, -alpha, depth - 1)
            node.remove_move(move, player)

            if val >= beta:
                return beta
            elif val > alpha:
                alpha = val
        return alpha


class AbstractAlgorithm(object):
    def __init__(self, depth=MAX, values=None):
        self.originalPlayer = None
        self.values = values
        self.depth = depth
        #print self.depth
        #print "^^ original"

    def check_base(self, node, player, depth):
        win = node.winner()
        if win == player:
            return MAX - (self.depth - depth)
        elif win:
            return -MAX + (self.depth - depth)
        elif node.complete():
            return 0
        return None

    def check_heurisitc(self, node, player, depth):
        c = self.check_base(node, player, depth)
        if c is None and depth <= 0:
            heuValue = node.heuristic(self.originalPlayer)
            if player == self.originalPlayer:
                return heuValue
            else:
                return -heuValue
        else:
            return c


class Minimax(AbstractAlgorithm):
    def run(self, node, player):
        self.originalPlayer = player
        return self.wrap(node, get_enemy(player), self.depth)

    def check(self, node, player, depth):
        return self.check_heurisitc(node, self.originalPlayer, depth)

    def wrap(self, node, player, depth):
        check = self.check(node, player, depth)
        if check is not None:
            return check
        return self.iterate(node, player, depth)

    def iterate(self, node, player, depth):
        best = None
        enemy = get_enemy(player)
        for move in node.available_moves():
            node.make_move(move, player)
            val = self.wrap(node, enemy, depth - 1)
            node.remove_move(move, player)
            if player == self.originalPlayer:
                if best is None or val > best:
                    best = val
            else:
                if best is None or val < best:
                    best = val
        return best


class Negamax(Minimax):  # cant handle even depth numbers
    def run(self, node, player):
        self.originalPlayer = player
        return -self.wrap(node, get_enemy(player), self.depth)

    def check(self, node, player, depth):
        return self.check_heurisitc(node, player, depth)

    def iterate(self, node, player, depth):
        best = -MAX
        enemy = get_enemy(player)
        for move in node.available_moves():
            node.make_move(move, player)
            best = max(best, -self.wrap(node, enemy, depth - 1))
            node.remove_move(move, player)
        return best


class AlphaBeta(Minimax):
    def wrap(self, node, player, depth, alpha=-MAX, beta=MAX):
        check = self.check(node, player, depth)
        if check is not None:
            return check
        return self.iterate(node, player, depth, alpha, beta)

    def iterate(self, node, player, depth, alpha, beta):
        enemy = get_enemy(player)
        for move in node.moveOrdering(node.available_moves()):
            node.make_move(move, player)
            val = self.wrap(node, enemy, depth - 1, alpha, beta)
            node.remove_move(move, player)
            if player == self.originalPlayer:
                if val > alpha:
                    alpha = val
                if alpha >= beta:
                    return beta
            else:
                if val < beta:
                    beta = val
                if beta <= alpha:
                    return alpha
        if player == self.originalPlayer:
            return alpha
        else:
            return beta


class NegaAlphaBeta(AlphaBeta, Negamax):
    def iterate(self, node, player, depth, alpha, beta):
        enemy = get_enemy(player)
        for move in node.moveOrdering(node.available_moves()):
            node.make_move(move, player)
            val = -self.wrap(node, enemy, depth - 1, -beta, -alpha)
            node.remove_move(move, player)
            if val >= beta:
                return val
            if val >= alpha:
                alpha = val
        return alpha


class NegaAlphaBetaTT(NegaAlphaBeta):
    def wrap(self, node, player, depth, alpha=-MAX, beta=MAX):
        entry = getEntry(node.hash())
        if entry is not None and entry[2] >= depth:
            if player == entry[3]:
                ret = entry[0]
            else:
                ret = -entry[0]
            if entry[1] == EXACT:
                return ret
            if entry[1] == LOWERBOUND and ret >= beta:
                alpha = ret
            elif entry[1] == UPPERBOUND and ret <= alpha:
                beta = ret
            if alpha >= beta:
                return ret
        check = self.check(node, player, depth)
        hsh = node.hash()
        if check is not None:
            if check <= alpha:
                storeEntry(hsh, check, UPPERBOUND, depth, player)
            if check >= beta:
                storeEntry(hsh, check, LOWERBOUND, depth, player)
            if check > alpha and check < beta:
                storeEntry(hsh, check, EXACT, depth, player)
            return check
        best, alpha, beta = self.iterate(node, player, depth, alpha, beta)
        if best <= alpha:  # a lowerbound value
            storeEntry(hsh, best, UPPERBOUND, depth, player)
        if best >= beta:  # an upperbound value
            storeEntry(hsh, best, LOWERBOUND, depth, player)
        if best > alpha and best < beta:  # a true minimax value
            storeEntry(hsh, best, EXACT, depth, player)
        return best

    def iterate(self, node, player, depth, alpha, beta):
        best = -MAX-1
        enemy = get_enemy(player)
        for move in node.moveOrdering(node.available_moves()):
            node.make_move(move, player)
            val = -self.wrap(node, enemy, depth - 1, -beta, -alpha)
            node.remove_move(move, player)
            if val > best:
                best = val
            if best > alpha:
                alpha = best
            if val >= beta:
                break
        return best, alpha, beta
