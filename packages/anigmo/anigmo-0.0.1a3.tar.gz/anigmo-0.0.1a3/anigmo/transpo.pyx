# cython: profile=True
# -*- coding: utf-8 -*-
"""
anigmo.transpo - transposition table stuff for algorithms
"""

HASH_TABLE = {}

LOWERBOUND = -1
EXACT = 0
UPPERBOUND = 1


def storeEntry(hashes, best, typ, depth, player):
    for board in hashes:
        HASH_TABLE[board] = (best, typ, depth, player)


def getEntry(board):
    return HASH_TABLE.get(board[0], None)


def resetTable():
    global HASH_TABLE
    HASH_TABLE = {}
