### Search tree에서 사용할 heuristic value를 계산하는 역할을 하는 class ###

## heuristic value를 결정하는 우선순위
# 1순위 : 게임에서 이기거나 진 경우 (게임의 결과를 확실히 아는 경우)
# 2순위 : 비긴 경우 (질수도 있는 상황 보다는 최소한 비길 수 있는 상황을 선택하는 것이 안전하기 때문)
# 3순위 : heuristic function을 이용하여 board의 상태에 대한 heuristic value를 계산 (게임의 결과를 확실히 예측하진 못한다)
# 동점일 경우 : 1. column의 높이가 높은 순서 (2순위와 3순위에만 해당)
#            2. 먼저 탐색한 column 순서 (탐색하는 column의 순서가 가운대를 중심으로 탐색하기 때문에 가장 가운데이 있는 것이라고 봐도 무방)
# 이 중, Heuristic class는 3순위 값을 계산한다
 
## Heuristic vale 계산 방법 ##
# 현재 position에서 아래와 같은 pattern이 나타나면 해당하는 점수를 부여한다.
# ('O'가 선공, 'X'가 후공을 의미하며, '.'은 반칸을 나타낸다)
# 1. O가 1개 : 2점 (O... .O.. ..O. ...O)
# 2. O가 2개 : AI가 선공이면 15점, 후공이면 14점 (OO.. O.O. O..O .OO. .O.O ..OO)
# 3. O가 3개 : AI가 선공이면 32점, 후공이면 30점 (OOO. OO.O O.OO .OOO)
# 4. X가 1개 : 2점 (X... .X.. ..X. ...X)
# 2. X가 2개 : AI가 선공이면 15점, 후공이면 16점 (XX.. X.X. X..X .XX. .X.X ..XX)
# 3. X가 3개 : AI가 선공이면 32점, 후공이면 35점 (XXX. XX.X X.XX .XXX)

from board import Board
from itertools import combinations

class Heuristic(Board):

    # Initialization
    def __init__(self, player, width = None, height = None):
        # Board class에서 initialization
        super().__init__(player, width, height)

        # 가로, 세로, 대각선에 들어갈 패턴들의 목록
        self.patH = [(1 << (i * (self.height + 1))) for i in range(4)]
        self.patV = [(1 << i) for i in range(4)]
        self.patD1 = [(1 << (i * (self.height + 2))) for i in range(4)]
        self.patD2 = [(1 << (i * self.height + 3)) for i in range(4)]
        
        # 각 패턴들에 부여할 점수
        self.scoreO = (player == 0) and [0, 2, 15, 32, 100000] or [0, 2, 16, 35, 100000]
        self.scoreX = (player == 0) and [0, 2, 15, 32, 100000] or [0, 2, 14, 30, 100000]

        # 각 패턴들에 대한 점수가 들어있는 dictionary
        self.patMatchO = dict()
        self.patMatchX = dict()
        self.patternSetting()   # patMatchO, patMatch setting

    # patMatchO와 patMatchX에 값을 집어 넣는다
    # ex. O___
    #     _.__
    #     __O_
    #     ___. (대각선(\))
    # posOX = 0b 00000 00010 00000 01000 이면 15점
    def patternSetting(self):
        for pat in [self.patH, self.patV, self.patD1, self.patD2]:
            for r in [1, 2, 3]:
                for comb in combinations(pat, r):
                    self.patMatchO[sum(comb)] = self.scoreO[r]
                    self.patMatchX[sum(comb)] = self.scoreX[r]

    # output : 현재 상태에 대한 heuristic value
    # (col, row) = (2, 1)라면,
    # _______  _______  _______  _______
    # _______  _?_____  ____?__  _?_____
    # _______  _?_____  ___?___  __?____
    # _______  _?_____  __?____  ___?___
    # _????__  _?_____  _?_____  ____?__
    # _______  _______  _______  _______ -> ?에 표시된 부분을 확인한다
    def evaluate(self):
        posA = sum(self.posAll)
        posO = (self.moves % 2 != self.player) and (self.posOX) or (posA - self.posOX)
        posX = posA - posO
        score = 0

        for pat in [self.patH, self.patV, self.patD1, self.patD2]:
            mask = sum(pat)
            shift = 0
            for _ in range((pat == self.patV) and (self.width) or (self.width - 3)):
                for _ in range((pat == self.patH) and (self.height) or (self.height - 3)):
                    # 1. (posA & mask) == (posO/X & mask)를 확인
                    #    빈칸인지 상대 stone인지 확인하기 위해 (ex. O..O는 True, O.XO는 False)
                    # 2. 해당 pattern이 patMatchO/X에 존재하는지 확인
                    # -> 해당 pattenr에 대한 score를 반영한다. (O의 score는 plus, X의 score는 minus)
                    if (posA & mask) == (posO & mask) and ((posO & mask) >> shift) in self.patMatchO:
                        score += self.patMatchO[(posO & mask) >> shift]
                    elif (posA & mask) == (posX & mask) and ((posX & mask) >> shift) in self.patMatchX:
                        score -= self.patMatchX[(posX & mask) >> shift]
                    mask <<= 1
                    shift += 1
                mask <<= (pat == self.patH) and 1 or 4
                shift += (pat == self.patH) and 1 or 4

        return score