### Connect four 게임에서 최적의 수를 두기 위한 game tree를 구현하는 class ###

## Game tree search에 사용한 전략
# 1. Mini-Max algorithm
# 2. Alpha-Beta pruning
# 3. Partial tree
# 4. Heuristic function
# 5. Iterative deepening (기존의 개념에서 변형하여 사용)
# 6. Dynamic Programming

## heuristic value를 결정하는 우선순위
# 1순위 : 게임에서 이기거나 진 경우 (게임의 결과를 확실히 아는 경우)
# 2순위 : 비긴 경우 (질수도 있는 상황 보다는 최소한 비길 수 있는 상황을 선택하는 것이 안전하기 때문)
# 3순위 : heuristic function을 이용하여 board의 상태에 대한 heuristic value를 계산 (게임의 결과를 확실히 예측하진 못한다)
# 동점일 경우 : 1. column의 높이가 높은 순서 (2순위와 3순위에만 해당)
#            2. column을 탐색한 순서 (탐색하는 column의 순서가 가운대를 중심으로 탐색하기 때문에 가장 가운데이 있는 것이라고 봐도 무방)
# 이 중, GameTree class는 1순위, 2순위, 동점일 경우를 계산한다.

# 아쉬운 부분 : 대칭인 경우 탐색 속도가 많이 줄어드는데, 시간 계산에 적용하지 못한 점

from heuristic import Heuristic
from copy import deepcopy
from time import time

class GameTree(Heuristic):

    # Initialization
    def __init__(self, player, width = None, height = None, timeLimit = 120):
        # Heuristic class에서 initialization
        super().__init__(player, width, height)
        
        # 탐색 제한 시간 설정
        self.timeLimit = timeLimit

        # board들에 대한 heuristic value들을 저장
        # 1. data[position] = 1순위, 2순위 heuristic value (abs(score) >= 1000)
        # 2. heuData[depth][position] = 3순위 heuristic value
        self.data = dict()
        self.heuData = dict(dict())

        # 탐색할 column number의 순서
        self.colOrder = self.getColOrder()

        # 몇 수 앞까지 search할 것인지 판단
        # AI가 선공일 경우에는 절반의 column(width가 7일 때 3, 2, 1번 column)만 탐색하기 때문에 초기값이 더 크다 
        self.ply = (self.player == 0) and 12 or 11

        # 현재까지 구한 score 중 가장 높은 score를 저장
        # 1순위 heuristic value에 한한다.
        self.maxScore = None

        # ply가 이미 커졌거나 작아졌던 적이 있는지를 나타낸다
        self.alreadyIncreased = False
        self.alreadyDecreased = False

        print('\nHeuristic value는 아래 기준에 의해 결정됩니다.')
        print('- 1순위 : 게임에서 확실히 이기거나 지는 경우')
        print('- 2순위 : 게임에서 비긴 경우')
        print('- 3순위 : 가로, 세로, 대각선 각각에 대해 나올 수 있는 모든 4개의 돌의 패턴에 대해')
        print('\tHuman의 돌 없이 AI의 돌이 1개 있는 경우는 ' + str(self.player == 0 and self.scoreO[1] or self.scoreX[1]) + '점,')
        print('\tHuman의 돌 없이 AI의 돌이 2개 있는 경우는 ' + str(self.player == 0 and self.scoreO[2] or self.scoreX[2]) + '점,')
        print('\tHuman의 돌 없이 AI의 돌이 3개 있는 경우는 ' + str(self.player == 0 and self.scoreO[3] or self.scoreX[3]) + '점,')
        print('\tAI의 돌 없이 Human의 돌이 1개 있는 경우는 ' + str(self.player == 1 and -self.scoreO[1] or -self.scoreX[1]) + '점,')
        print('\tAI의 돌 없이 Human의 돌이 2개 있는 경우는 ' + str(self.player == 1 and -self.scoreO[2] or -self.scoreX[2]) + '점,')
        print('\tAI의 돌 없이 Human의 돌이 2개 있는 경우는 ' + str(self.player == 1 and -self.scoreO[3] or -self.scoreX[3]) + '점으로 계산하여 모든 값을 더한 값')
    
    # 탐색할 column number의 순서를 계산한다
    # 가운데 column을 먼저 탐색하도록 설정하는데,
    # 그 이유는 alpha-beta pruning이 많이 일어나게 해서 탐색 시간을 줄이기 위함이다
    # ex. width = 7 일 때 colOrder = [3, 2, 4, 1, 5, 0, 6]
    # 현재 board가 대칭인 경우에는 절반의 column만 탐색한다
    # ex. 현재 board가 대칭이라면 width = 7 일 때 colOrder = [3, 2, 1, 0]
    # output : 탐색할 column number의 순서
    def getColOrder(self):
        # 1. 첫 turn이고 width = 7인 경우
        if self.moves == 0 and self.width == 7:
            return [2, 1, 0]
        # 2. 대칭인 경우
        if self.symmetry():
            #return [i for i in range(self.width // 2, -1, -1)]
            return [3, 2, 1, 0]
        # 2. 대칭이 아닌 경우
        #colOrder = []
        #col = self.width // 2
        #sign = 1
        #for i in range(self.width):
        #    col += sign * i
        #    sign *= -1
        #    colOrder.append(col)
        #return colOrder
        return [3, 2, 4, 1, 5, 0, 6]
    
    # 현재 turn이 max's turn인지 min's turn인지 확인
    # output : 현재 turn이 max's turn이면 True, min's turn이면 False
    def maxTurn(self):
        return self.moves % 2 == self.player

    # Mini-Max algorithm을 이용하여 최적의 score를 계산
    # input : alpha-beta pruning을 위한 alpha, beta값, partial tree를 위한 depth limit
    # output : 현재 상태에서 선택할 수 있는 가장 높은 score
    def miniMax(self, parentAlpha, parentBeta, depthLimit):
        ## 1. 현재 상태에서 바로 score를 return 할 수 있는 경우
        pos = self.posCurrent()
        
        # 1-1. 현재 상태에 대한 1순위 heuristic value가 self.data에 존재하는 경우
        if pos in self.data:
            return self.data[pos]
        
        # 1-2. 현재 게임이 이겼거나 진 상태로 끝이 난 경우 (1순위)
        elif self.win():
            score = 1000 + self.width * self.height - self.moves + 1   # Heuristic class에서 구현한 score와의 우선순위 구분을 주기 위해 값에 1000을 더한다. 더 빨리 이길 수록 점수가 크다
            score *= self.maxTurn() and -1 or +1                       # 내가 이긴 경우는 양수, 상태가 이긴 경우는 음수로 score을 설정
            self.data[pos] = score                                     # 구한 score를 self.data에 저장한다
            return score
        
        # 1-3. 게임이 비긴 경우 (42턴이 넘어갔는데, 이겼거나 지지 않은 경우. 1순위)
        # Heuristic class에서 구한 score는 설령 점수가 높다 하더라도 결과적으로 게임에서 질 수도 있기 때문에 비겼을 때의 우선순위(점수)를 더 높게 책정하였다.
        elif self.moves >= self.width * self.height:
            self.data[pos] = 1000      # 비긴 경우의 score = 1000
            return 1000
        
        # 1-4. 현재 상태에 2순위 heuristic value가 self.heuData에 존재하는 경우
        elif depthLimit in self.heuData and pos in self.heuData[depthLimit]:
            return self.heuData[depthLimit][pos]
        
        # 1-5. 설정한 depth limit 값만큼 search를 한 경우 (2순위)
        elif self.moves >= depthLimit:
            score = self.evaluate()                 # score = Heuristic class에서 나온 score
            if depthLimit not in self.heuData:      # 구한 score를 self.heuData에 저장한다
                self.heuData[depthLimit] = dict()
            self.heuData[depthLimit][pos] = score
            return self.evaluate()
        

        ## 2. Mini-Max algorithm과 Alpha-Beta pruning을 이용하여 탐색

        # 2-1. 탐색할 column number의 순서를 설정
        self.colOrder = self.getColOrder()
        for col in deepcopy(self.colOrder):
            if not self.possible(col):
                self.colOrder.remove(col)

        alpha, beta = parentAlpha, parentBeta
        score = None

        # 2-2. child node를 탐색하여 score 계산
        for col in self.colOrder:
            # child node의 score 계산
            self.put(col)
            childScore = self.miniMax(alpha, beta, depthLimit)
            self.undo()

            # child score와 현재까지 구한 score 비교
            # MAX turn
            if (self.maxTurn()) and (score is None or score < childScore):
                score = childScore
                if beta <= score:
                    return score        # pruning!
                elif alpha < score:
                    alpha = score       # alpha값 설정
            # MIN turn
            elif (not self.maxTurn()) and (score is None or childScore < score):
                score = childScore
                if score <= alpha:
                    return score        # pruning!
                elif score < beta:
                    beta = score      
        
        # 1순위 heuristic value를 저장
        if abs(score) >= 1000:
            self.data[pos] = score
        # 2순위 heuristic value를 저장
        else:
            if depthLimit not in self.heuData:
                self.heuData[depthLimit] = dict()
            self.heuData[depthLimit][pos] = score

        return score

    # miniMax 함수를 통해 구한 score를 이용하여 다음에 둘 column nuber를 정한다
    # 이때, 제한 시간 내에 탐색을 마쳐야 하므로, 각각의 node를 탐색한 시간을 통해 ply값을 증가시킬지, 감소시킬지, 그대로 유지할지를 정한다
    # input : 초기 시간
    # output : 선택할 column number
    def search(self, initTime):
        # 1. 만약 찾고자 하는 depth의 값이 이미 데이터 상에 존재한다면 다음 한 단계 아래의 depth를 탐색한다.
        #    이때, 만약 현재 상황이 기존에 탐색하다 시간이 오래 걸려 depth를 낮춰서 탐색하게 된 경우라면 그대로 진행한다.
        if not self.alreadyDecreased and self.ply + self.moves in self.heuData:
            self.ply += 1
            self.alreadyIncreased += 1
            return self.search(initTime)

        # 2. 탐색할 column number의 순서를 설정
        possibleColLength = 7       # 현재 둘 수 있는 column의 수
        sym = self.symmetry()       # 현재 상태가 대칭 상황인지 확인

        if self.moves == 0 and self.width == 7:
            print('\nboard가 대칭입니다.')
            colOrder = [2, 1, 0]
        elif sym:
            print('\nboard가 대칭입니다.')
            colOrder = []
            #for col in deepcopy(self.getColOrder()):
            for col in [3, 2, 1, 0]:
                if self.possible(col):
                    colOrder.append(col)
                #elif self.width % 2 == 1 and col == self.width // 2:
                elif col == 3:
                    possibleColLength -= 1
                else:
                    possibleColLength -= 2
        else:
            colOrder = []
            #for col in deepcopy(self.getColOrder()):
            for col in [3, 2, 4, 1, 5, 0, 6]:
                if self.possible(col):
                    colOrder.append(col)
                else:
                    possibleColLength -= 1

        # 3. 탐색하여 score를 구하고, ply를 조정
        print('\n' + str(self.ply if (self.ply + self.moves <= self.width * self.height) else (self.width * self.height - self.moves)) + '수 앞을 계산중...')
        
        score, bestCol = None, None     # 가장 높은 점수와 return할 column number
        colSearchTime = []              # column마다 탐색하는데 걸린 시간을 저장하는 list
        heuristicChanged = 0            # 탐색 중간에 ply를 바꾼 경우, 다음 turn의 탐색시 ply값을 조정하기 위해 사용

        for col in colOrder:
            # 1. miniMax 함수를 이용하여 child score를 계산
            startTime = time()
            self.put(col)
            childScore = self.miniMax(-10000, 10000, self.ply + self.moves - 1)
            self.undo()

            # 2. 탐색 시간을 이용하여 변수 값들 설정
            # - initTime : play.py에서 search 함수를 부른 시간 (가장 초기 시간)
            # - startTime : 현재 column 탐색을 시작한 시간
            # - endTime : 현재 column 탐색이 끝난 시간
            # - initFunctionCallTime : search 함수를 부른 이후 현재까지 걸린 시간
            # - avgColSearchSpeed : column을 탐색하는데 걸린 평균 시간
            # - maxColSearchSpeed : column을 탐색하는데 걸린 최대 시간
            endTime = time()
            initFunctionCallTime = endTime - initTime 
            if None in colSearchTime:
                colSearchTime = [(endTime - startTime) for _ in range(len(colSearchTime))]
            colSearchTime.append(endTime - startTime)
            avgColSearchSpeed = sum(colSearchTime) / len(colSearchTime)
            maxColSearchSpeed = max(colSearchTime)
                
            # 3. 탐색을 통해 구한 정보를 출력
            self.printHeuristic(col, childScore, colSearchTime[-1])
            if sym:
                self.printHeuristic(self.width - col - 1, childScore, 0)
            # 3-1. 만약 바로 이기는 경우에는 더이상의 탐색을 하지 않고 해당 column을 return
            if childScore > 1000 and (self.maxScore is None or self.maxScore < childScore):
                self.maxScore = childScore
                maxPly = (self.width * self.height - (childScore - 1000) + 1) - self.moves
                self.ply = maxPly if (self.ply >= maxPly) else self.ply
                return col
            
            # 4. 탐색하는데 걸린 시간을 계산하여 ply를 조정
            # 기본적으로 탐색한 시간을 통해 ply를 -2 ~ +2 만큼 조정하는데,
            # 만약 이미 ply가 줄어들었는데 다시 올리려는 경우는 제외한다
            # 또한, ply가 짝수일 때는 상대방이 공격한 이후 나온 값들을 이용하여 계산하기 때문에 비교적 score가 낮고,
            #      ply가 홀수일 때는 내가 공격한 이후 나온 값들을 이용하여 계산하기 때문에 비교적 score가 높게 나오므로
            #      첫 turn 이후 ply를 조정해야 하는 경우에는 ply를 -2 또는 +2 한다
            # search 함수를 다시 부르지 않고 탐색 시간을 조정하는 경우에는 다음 탐색 때 탐색 시간 설정을 다시 하기 위해 colSearchTime을 None으로 채운다

            # 4-1. 첫 탐색 때 걸린 시간을 이용하여 계산
            #      ply를 +2, +1, -1 하는 경우에는 search 함수를 다시 불러서 계산하고,
            #      ply를 -2 하거나 변동이 없는 경우에는 현재 상태에서 그대로 계산한다
            if col == colOrder[0] and self.maxScore is None and self.ply + self.moves < self.width * self.height:
                if not self.alreadyDecreased and not childScore <= -1000 and not (self.alreadyIncreased and self.moves < 20) and initFunctionCallTime + len(colOrder) * pow(possibleColLength, 2) * colSearchTime[0] < self.timeLimit * 0.95:
                    self.ply += 2
                    self.alreadyIncreased = True
                    return self.search(initTime)
                elif not self.alreadyDecreased and not childScore <= -1000 and not (self.alreadyIncreased and self.moves < 20) and initFunctionCallTime + len(colOrder) * possibleColLength * colSearchTime[0] < self.timeLimit * 0.95:
                    self.ply += 1
                    self.alreadyIncreased = True
                    return self.search(initTime)
                elif initFunctionCallTime + (len(colOrder) - 1) * colSearchTime[0] < self.timeLimit:
                    pass
                elif initFunctionCallTime + len(colOrder) * colSearchTime[0] / possibleColLength < self.timeLimit:
                    self.ply -= 1
                    self.alreadyDecreased = True
                    return self.search(initTime)
                else:
                    self.ply -= 2
                    self.alreadyDecreased = True
                    colSearchTime = [None for _ in range(len(colSearchTime))]
                    print(str(self.ply if (self.ply + self.moves <= self.width * self.height) else (self.width * self.height - self.moves)) + '수 앞을 계산중...')
            
            # 4-2. 첫 탐색 이후에 걸린 시간을 이용하여 계산
            #      탐색 시간이 빠른 경우에는 다음 탐색부터는 ply에 +2하여 탐색한다
            #      단, 시간이 제한 내에 탐색하는 것이 중요하므로 2/3 이상 탐색한 경우에는 적용하지 않는다
            #      탐색 시간이 느린 경우에는 ply에 -2를 하여 탐색한다
            elif col != colOrder[0] and self.maxScore is None:
                if not self.alreadyDecreased and len(colSearchTime) <= len(colOrder) * (2/3) and self.ply + self.moves < self.width * self.height and len(colSearchTime) < len(colOrder) and initFunctionCallTime + (len(colOrder) - len(colSearchTime)) * (avgColSearchSpeed * pow(possibleColLength, 2)) < self.timeLimit * 0.95:
                    self.ply += 2
                    self.alreadyIncreased = True
                    colSearchTime = [None for _ in range(len(colSearchTime))]
                    heuristicChanged += 1
                    print(str(self.ply if (self.ply + self.moves <= self.width * self.height) else (self.width * self.height - self.moves)) + '수 앞을 계산중...')
                elif len(colSearchTime) < len(colOrder) and initFunctionCallTime + maxColSearchSpeed + (len(colOrder) - len(colSearchTime) - 1) * (maxColSearchSpeed / possibleColLength) > self.timeLimit * 0.95:
                    self.ply -= 2
                    colSearchTime = [None for _ in range(len(colSearchTime))]
                    heuristicChanged -= 1
                    print(str(self.ply if (self.ply + self.moves <= self.width * self.height) else (self.width * self.height - self.moves)) + '수 앞을 계산중...')
            
            # 5. child score와 현재 score를 비교
            # 만약 child score와 현재 score가 같다면 해당 column의 높이를 통해 결정(3순위)
            # 높이도 같다면 먼저 탐색한 순서대로 결정(4순위)
            if score is None or childScore > score:
                score, bestCol = childScore, col
            elif childScore == score and self.getRow(col) > self.getRow(bestCol):
                bestCol = col
        print()

        # 4. 다음 turn에 탐색할 ply를 조정
        # 4-1. moves = 0 일때는 3개의 column만 탐색하기 때문에 초기값을 높게 설정하였으므로 그 값이 중간에 줄어들지 않았다면 1만큼 낮춰준다
        #if self.width == 7 and self.moves == 0 and self.ply > 11:
        if self.moves == 0 and self.ply > 11:
            self.ply -= 1
        # 4-2. 탐색 중간에 ply값이 바뀐 경우에는 초기값과 바뀐 값의 중간값으로 ply를 조정한다
        elif self.moves > 0:
            self.ply -= heuristicChanged
        
        # 5. 필요 없어진 heuData값을 메모리에서 지운다
        for key in range(self.moves + self.ply):
            if key in self.heuData:
                self.heuData[key].clear()

        # 6. 기타 값 초기화
        self.alreadyIncreased = False
        self.alreadyDecreased = False

        # 7. 최적의 column number를 return
        return bestCol

    # 현재 상태에서 입력받은 column에 stone을 놓았을 때의 heuristic value와 탐색하는데 걸린 시간을 출력
    # input : 탐색한 column number, 탐색 결과 나온 score, 탐색하는데 걸린 시간
    def printHeuristic(self, col, score, searchTime):
        if score > 1000:
            print('- 1순위 : ' + str(col + 1) + '열에 둘 경우 AI가 ' + str(self.width * self.height - self.moves - (score - 1001)) + '수 안에 이깁니다.' + '\t(걸린 시간 : ' + str(searchTime) + ')')
        elif score < -1000:
            print('- 1순위 : ' + str(col + 1) + '열에 둘 경우 AI가 ' + str(self.width * self.height - self.moves + (score + 1001)) + '수 안에 집니다.' + '\t(걸린 시간 : ' + str(searchTime) + ')')
        elif score == 1000:
            print('- 2순위 : ' + str(col + 1) + '열에 둘 경우 비깁니다.' + '\t(걸린 시간 : ' + str(searchTime) + ')')
        else:
            print('- 3순위 : heuristic(' + str(col + 1) + ') = ' + str(score) + '\t(걸린 시간 : ' + str(searchTime) + ')')