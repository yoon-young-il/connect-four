### Connect4 게임을 하기 위해 board에서 이루어지는 기능들을 구현하는 class ###

## board는 bit 형식으로 이루어져있다 ##
## 이유 : 1. board를 하나의 정수값으로 나타내 DP에 쓰일 참조용 데이터로 사용하기 위해
##          (각각의 state가 w*(h+1)bit의 값으로 나타난다.)
##       2. win() 함수의 속도를 빠르게 구현

# ex. 4x4
#              0 1 0 1     0 0 0 0     0 1 0 1     0 0 0 0     0 0 0 0     0 0 0 0
#   X   O      0 0 1 1     0 0 0 1     0 0 0 0     0 0 0 1     0 1 0 1     0 0 0 0
#   X X O  ->  1 0 1 1  =  0 0 0 1  +  1 0 1 0  =  0 0 0 1  +  0 1 0 1  +  0 0 0 0
# X O O O      0 1 1 1     0 1 1 1     0 0 0 0     0 1 1 1     1 1 1 1     0 0 0 0     
# O X X O      1 0 0 1     1 0 0 1     0 0 0 0     1 0 0 1     1 1 1 1     1 1 1 1
#   game       current      posOX       posTop      posOX       posAll    posBottom
# => current = posOX + posAll + posBottom
# bit를 읽는 순서는 왼쪽 아래부터 위로 올라간다. (ex. current = 0b 10100 01001 01110 11111)

class Board:

    # Initialization
    def __init__(self, player, width = None, height = None):
        # game rule setting
        self.width  = width  if (width  is not None) else 7     # width와 height는 기본적으로는 입력받는 형식이나,
        self.height = height if (height is not None) else 6     # (7, 6)이라는 가정 하에 만들어진 함수들도 일부 존재한다.
        self.player = player                                    # AI 기준으로 선공 = 0, 후공 = 1
        
        # board를 나타내기 위한 position
        self.posOX = 0
        self.posAll = [0] * self.width
        self.posBottom = [1 << (i * (self.height + 1)) for i in range(self.width)]

        # 게임 진행 기록
        self.moves = 0                  # game에서 움직인 횟수
        self.log = []                   # 현재까지 둔 stone의 기록
        self.neverSymmetry = False      # 현재 board가 대칭이 불가능한 상황인지 판단.
                                        # ex. 4x4
                                        #                 O               O
                                        #   X X           X X             X X     
                                        #   O O           O O X         O O O X     
                                        # O X X O       O X X O         O X X O   
                                        #   대칭       대칭은 아니지만,     대칭도 아니고,
                                        #             다른 수에 의해     어떤 수를 두더라도
                                        #            대칭이 될 수 있다  대칭이 될 가능성이 없다
                                        # (참고로, undo 함수를 이용한 경우는 고려하지 않았음.)

    # Board를 출력
    def printBoard(self):
        posO = (self.posOX) if (self.moves % 2) else (sum(self.posAll) - self.posOX)
        posX = (sum(self.posAll) - self.posOX) if (self.moves % 2) else (self.posOX)
        
        board4print = []
        for w in range(self.width):
            board4print.append([])
            for _ in range(self.height):
                board4print[w].append((posO & 1) and 'O' or ((posX & 1) and 'X' or ' '))
                posO >>= 1
                posX >>= 1
            posO >>= 1
            posX >>= 1
        
        for h in range(self.height, 0, -1):
            print(' ' + ('+-' * self.width) + '+')
            print(str(h) + '|' + '|'.join(board4print[w][h-1] for w in range(self.width)), end = '|\n')
        print(' ' + ('+-' * self.width) + '+')
        print('  ' + ' '.join(str(i+1) for i in range(self.width)))

    # output : 현재 position
    # posCurrent = posOX + posAll + posBottom
    def posCurrent(self):
        return self.posOX + sum(self.posAll) + sum(self.posBottom)

    # posOX에서 O와 X를 reverse
    # 현재 turn을 상대 turn으로 바꾸기 위해 사용한다.
    def posReverse(self):
        self.posOX = sum(self.posAll) - self.posOX

    # output : 현재 board가 대칭이면 True, 아니면 False
    # 만약 앞으로의 board에서 대칭이 절대 나오지 않는 상황이라면 self.neverSymmetry = False
    def symmetry(self):
        if self.neverSymmetry:
            return False

        posO = self.posOX
        posX = sum(self.posAll) - posO

        colO = []
        colX = []

        mask = self.posBottom[1] - 1
        
        for _ in range(self.width):
            colO.append(posO & mask)
            colX.append(posX & mask)
            posO >>= (self.height + 1)
            posX >>= (self.height + 1)

        for i in range(self.width // 2):
            if colO[i] != colO[-i-1] or colX[i] != colX[-i-1]:
                if colO[i] & colX[-i-1] > 0 or colO[-i-1] & colX[i] > 0:
                    self.neverSymmetry = True
                return False
        return True

    # 입력 받은 column에 stone을 놓을 수 있는지 판단한다
    # input : column number
    # output : stone을 놓을 수 있으면 True, 아니면 False
    def possible(self, col):
        return self.posAll[col] < (self.posBottom[col] << (self.height - 1))

    # board에 stone을 놓는다
    # input : stone을 놓을 column number
    def put(self, col):
        # 1. moves = moves + 1
        self.moves += 1
        # 2. posAll의 제일 위칸에 stone(1) 추가
        self.posAll[col] = (self.posAll[col] << 1) + self.posBottom[col]
        # 3. turn(O, X)이 바뀌었으므로 position reverse
        self.posReverse()
        # 4. log에 둔 stone 추가
        self.log.append(col)
    
    # 한 번에 여러 stone을 두기 위해 사용한다(test용도)
    # input : 둘 stone들의 column number list
    def puts(self, cols):
        for col in cols:
            self.put(col)
            
    # 마지막에 놓았던 stone을 없앤다
    # put 함수에서의 실행 방법을 역으로 실행
    def undo(self):
        # 4. log에서 stone을 뺀다
        col = self.log.pop()
        # 3. position reverse
        self.posOX = sum(self.posAll) - self.posOX
        # 2. posAll의 제일 위칸 stone 제거
        self.posAll[col] &= (self.posAll[col] >> 1)
        # 1. moves = moves - 1
        self.moves -= 1
    
    # 현재 connect four가 완성되었는지 확인
    # output : 4줄 이상 연속으로 존재하면 True, 아니면 False
    def win(self):
        # 1. moves < 7 인 경우 4줄 연속인 상황을 만드는 것이 불가능하므로 False를 return
        # Rule class의 Rule1, Rule2 함수를 이용했을 때의 오류 방지를 위해 7을 6으로 수정
        #if self.moves < 7:
        if self.moves < 6:
            return False
        
        # 2. 가로(-), 세로(|), 대각선(\, /)을 검사

        # 현재 player는 1, 상대는 0             : posOX  =  0000 0001 0010 0011 0100 0101 0110 0111 1000 1001 1010 1011 1100 1101 1110 1111
        # 인접하는 값이 둘 다 1이면 1, 아니면 0  : check1  =  000  000  000  001  000  000  010  011  000  000  000  001  100  100  110  111
        # 첫 번재 자리와 두 번째 자리가 1인가?   : check2 =    0    0    0    0    0    0    0    0    0    0    0    0    0    0    0    1

        # 가로줄(-) : (dx, dy) = (1, 0)
        # 세로줄(|) : (dx, dy) = (0, 1)
        # 대각선(/) : (dx, dy) = (1, 1)
        # 대각선(\) : (dx, dy) = (1, -1)

        for (dx, dy) in [(1, 0), (0, 1), (1, 1), (1, -1)]:
            check1 = self.posOX & (self.posOX >> (dx * (self.height + 1) + dy))
            check2 = check1 & (check1 >> (2 * (dx * (self.height + 1) + dy)))
            if check2:
                return True
        
        # 3. 해당사항 없으면 False를 return
        return False

    # win 함수와 거의 동일하되, 세로열이 이어진 경우는 확인하지 않는다.
    # input : 가장 마지막에 놓은 stone의 column number
    # output : 4줄 이상 연속으로 존재하면 True, 아니면 False
    def winWithoutVerticle(self):
        # 1. moves < 7 인 경우 4줄 연속인 상황을 만드는 것이 불가능하므로 False를 return
        #if self.moves < 7:
        if self.moves < 6:
            return False

        # 2. 가로(-), 대각선(/, \)을 검사
        for (dx, dy) in [(1, 0), (1, 1), (1, -1)]:
            check = self.posOX & (self.posOX >> (dx * (self.height + 1) + dy))
            if check & (check >> (2 * (dx * (self.height + 1) + dy))):
                return True
        
        # 3. 해당사항 없으면 False를 return
        return False
    
    # 입력받은 column의 가장 위에 있는 stone의 row number
    # input : column number
    # output : row number
    def getRow(self, col):
        for row in range(-1, self.height):
            if (self.posAll[col] >> (col * (self.height + 1) + row + 1)) == 0:
                return row

    # 입력받은 (col, row)에 놓인 stone의 종류
    # input : 찾으려는 칸의 column number와 row number
    # output : 해당 col, row에 놓인 stone이 'O'이면 0, 'X'이면 1, 없으면 -1 
    def exists(self, col, row):
        # mask : 찾으려는 위치를 표시하는 역할
        mask = self.posBottom[col] << row

        posO = (self.posOX) if (self.moves % 2 != self.player) else (sum(self.posAll) - self.posOX)
        if (posO & mask) > 0:
            return 0
        
        posX = sum(self.posAll) - posO
        if (posX & mask) > 0:
            return 1

        return -1

    # 입력받은 column의 가장 위에 있는 stone의 종류
    # input : 찾으려는 칸의 column number
    # output : 해당 column에 놓인 top stone이 'O'이면 0, 'X'이면 1, 없으면 -1
    def topStone(self, col):        
        return self.exists(col, self.getRow(col))