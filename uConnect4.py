"""
Authored by Randy Graham Jr.
"""
from collections import namedtuple
from math import inf

WFILTERS = (
    16843009, 15, 2113665, 33686018, 30, 4227330,
    67372036, 60, 8454660, 134744072, 120, 16909320,
    33818640, 67637280, 135274560, 2155905152, 1920,
    270549120, 4311810304, 3840, 541098240, 8623620608,
    7680, 1082196480, 17247241216, 15360, 2164392960,
    4328785920, 8657571840, 17315143680, 275955859456,
    245760, 34630287360, 551911718912, 491520, 69260574720,
    1103823437824, 983040, 138521149440, 2207646875648,
    1966080, 277042298880, 554084597760, 1108169195520,
    2216338391040, 2130440, 31457280, 4260880, 62914560,
    8521760, 125829120, 17043520, 251658240, 272696320,
    4026531840, 545392640, 8053063680, 1090785280, 16106127360,
    2181570560, 32212254720, 34905128960, 515396075520,
    69810257920, 1030792151040, 139620515840, 2061584302080,
    279241031680, 4123168604160
)

EVAL_TABLE = (
    (3, 4, 5,  7,  5,  4, 3),
    (4, 6, 8,  10, 8,  6, 4),
    (5, 8, 11, 13, 11, 8, 5),
    (5, 8, 11, 13, 11, 8, 5),
    (4, 6, 8,  10, 8,  6, 4),
    (3, 4, 5,  7,  5,  4, 3)
)

State = namedtuple("State", ["playerboard", "aiboard"])

WCACHE = {}

def check(state): return state in WCACHE
def get(state): return WCACHE[state]
def put(state, value):
    global WCACHE
    WCACHE[state] = value
def kfunc(e): return e[0]
def bitmask(x,y): return 1 << ((y*7)+x)
def is_valid(state, move): return ((state.playerboard | state.aiboard) & bitmask(move, 0)) == 0

def getwin(state):
    for f in WFILTERS:
        if f & state.playerboard == f: return -10
        if f & state.aiboard == f: return 1
    if state.playerboard | state.aiboard == 4398046511103: return 0.25
    return 0

def win(state): #Cache win checks
    if check(state): return get(state)
    value = getwin(state)
    put(state, value)
    return value

def term(state): return win(state) != 0

def mkmove(state, move, player):
    ob = state.playerboard | state.aiboard
    for y in range(1,6):
        if ob & bitmask(move, y) != 0:
            if player:
                return State(state.playerboard | bitmask(move, y-1), state.aiboard)
            else:
                return State(state.playerboard, state.aiboard | bitmask(move, y-1))
    if player:
        return State(state.playerboard | bitmask(move, 5), state.aiboard)
    else:
        return State(state.playerboard, state.aiboard | bitmask(move, 5))

def heuristic(state):
    score = 0
    for y in range(6):
        for x in range(7):
            if state.playerboard & bitmask(x,y) != 0: score -= EVAL_TABLE[y][x]
            if state.aiboard & bitmask(x,y) != 0: score += EVAL_TABLE[y][x]
    return score + (win(state)*100)

def ab(state, depth=0, player=True, a=-inf, b=inf):
    if depth >= 5 or win(state) != 0: return heuristic(state)
    bval = inf if player else -inf
    for move in range(7):
        if not is_valid(state, move): continue
        val = ab(mkmove(state, move, player), depth+1, not(player), a, b)
        bval = min(bval, val) if player else max(bval, val)
        b = min(min(bval, val), b) if player else b
        a = max(max(bval, val), a) if not player else a
        if a >= b: break
    return bval
        
def search(state):
    scores = []
    for ai_move in range(7):
        if not is_valid(state, ai_move): continue
        scores.append((ab(mkmove(state, ai_move, False)), ai_move))
    scores.sort(key=kfunc, reverse=True)
    print("Playing",scores[0][1])
    return scores[0][1]

def show(state):
    print("0 1 2 3 4 5 6")
    for y in range(6):
        tp = ""
        for x in range(7):
            if state.playerboard & bitmask(x, y) != 0: tp += "0 "
            elif state.aiboard & bitmask(x, y) != 0: tp += "O "
            else: tp += "_ "
        print(tp)

def main():
    print("NEW GAME")
    root = State(0,0)
    show(root)
    while True:
        pmove = int(input("Your move? "))
        if not is_valid(root, pmove): continue
        root = mkmove(root, pmove, True)
        show(root)
        if win(root) == -10: print("WIN")
        if win(root) == 1: print("LOSE")
        if win(root) == 0.25: print("DRAW")
        if win(root) != 0: main()
        print("Thinking...")
        root = mkmove(root, search(root), False)
        show(root)
        if win(root) == -10: print("WIN")
        if win(root) == 1: print("LOSE")
        if win(root) == 0.25: print("DRAW")
        if win(root) != 0: main()
main()
