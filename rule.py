from board import Board
import random

# col : 보드판의 각 열을 나타낸다.
# colList : 보드판의 열 중 AI가 착수 가능한 열들의 리스트이다. 
# put(col) : 보드판의 col열에 다음 차례의 플레이어가 돌을 넣는 함수이다.
# undo() : 보드판에 col열에 있는 가장 위쪽 돌을 지우는 함수이다.
# win() : 보드판의 현재 상태를 보고 게임의 승리여부(종료여부)를 확인하는 함수.
# self.posOX : posOX는 현재 보드판의 상태이고 
# self.posReverse() : posReverse()는 보드판의 모든 돌들을 반대로 뒤집는 함수이다. (O -> X, X -> O)
class Rule(Board):
    def __init__(self, player, width = 7, height = 6):
        super().__init__(player, width, height)
        self.colList = [i for i in range(0,width)]
    
    def rule1(self):
        # AI가 착수 했을때 이기는 수
        for col in self.colList:
            # colList의 col마다 돌을 넣어보고 만약 바로 승리하는 경우 그 col을 리턴한다.
            if self.possible(col):
                self.put(col) 
                if self.win():
                    self.undo() # put한 돌을 다시 빼야 하므로 undo한다.
                    return col
                else:
                    self.undo()
        return -1

    def rule2(self):
        # 상대방이 착수 했을때 이기는 경우를 막기 위한 수
        # colList의 col마다 돌을 넣어보고 만약 상대가 바로 다음턴에 이기게 될 경우 먼저 착수해서 패배를 막는다.
        self.posReverse()
        for col in self.colList:
            self.put(col)
            if self.win():
                self.undo()
                self.posReverse() # Reverse시킨 보드판을 다시 원상복구 시킨다.
                return col
            self.undo()
        self.posReverse()
        return -1

    def rule3(self):
        # 상대가 이길 수 있는 착수 점 바로 아래에 돌을 두지 않는 수
        # |   | X | X | X |   |   | O |
        # |   | O | X | O |   | O | X |
        # 위의 보드 상황에서 만약 O가 1열이나 5열에 두게 될 경우 바로 다음턴에 X가 4개를 이을수 있으므로 게임이 끝난다.
        # 그런 경우를 방지하기 위해서 1,5열과 같은 경우를 colList에서 제외시켜버리는 함수이다.
        temp = self.colList.copy()
        for col in temp:
            self.put(col)
            if self.possible(col):
                self.put(col)
                if self.win():
                    self.colList.remove(col)
                self.undo()
            self.undo()

    def rule4(self):
        # 착수했을 때 2가지의 이기는 경우가 나오는 수
        # | | | |X| | | |
        # | | | |O| | | |
        # | | |X|X|X| | |
        # | | |O|O|X| | |
        # |O|X|O|X|O| | |
        # |O|X|O|O|X| | |
        # 위의 상황에서 O가 1열에 둘 경우 1열에 4개로 쌓아서 승리하는 수와 3행의 가로로 4개를 이어서 승리하는 2가지의 경우가 나온다.
        # 이렇게 될 경우 X는 어디를 막아도 다른 하나의 수에 의해서 패배가 확실시 된다. 
        # 이런 경우가 나타날 경우 우선적으로 이 수에 두도록 한다.
        for col in self.colList:
            # 각 col에 두었을 때 승리하는 경우의 수를 count 변수에 담아서 저장한다.
            count = 0
            if self.possible(col):
                self.put(col)
                # 한번 put한뒤 보드를 뒤집음으로써 두번 연속 같은 플레이어가 두는 것 같은 효과를 가진다.
                self.posReverse()
                for col2 in range(self.width):
                    if self.possible(col2):
                        self.put(col2)
                        if self.win():
                            count += 1 # 승리하게 될 경우 count +1
                        self.undo()
                self.posReverse()
                self.undo()
                if count >= 2: # 승리하는 경우의 수가 2가지 이상일 경우 col을 리턴한다.
                    return col
        return -1        

    def rule5(self):
        # 상대방이 착수했을 때 2가지의 이기는 경우가 나오는 것을 막는 수
        # 위의 rule4와 마찬가지로 이번에는 상대방이 2가지의 이기는 경우의 수가 나오는 것을 미리 차단한다.
        self.posReverse()
        for col in self.colList:
            count = 0
            self.put(col)
            for col2 in range(self.width):
                if self.possible(col2):
                    self.put(col2)
                    if self.win():
                        count += 1
                    self.undo()
            self.undo()
            if count >= 2:
                self.posReverse()
                return col
        self.posReverse()
        return -1

    def rule6(self):
        # rule3에 따라 상대방이 뒀을 때 내가 이기는 열에 두지 않는 경우
        # rule3에 의해서 상대방이 두지 못하는 열에 굳이 내가 먼저 수를 둬서 상대방이 수비할 여지를 남기지 않는 수이다.
        # rule3와 마찬가지로 colList에서 해당 col을 삭제해버리는 함수이다.
        temp = self.colList.copy()
        for col in temp:
            self.put(col)
            self.posReverse()
            if self.possible(col):
                self.put(col)
                if self.winWithoutVerticle():
                    self.colList.remove(col)
                self.undo()
            self.posReverse()
            self.undo()
    
    def rule7(self):
        # 양 옆이 막히지 않는 3개의 연속된 돌을 만드는 경우의 수
        # | | | | | | | |
        # | |X|X| | | | | 
        # | |O|O|X|O| | |
        # 위와 같은 경우 X가 3열에 둘 경우 양 옆이 비어있는 연속된 3개의 가로줄이 완성된다.
        # 바로 승리와 직결되지 못하는 수라 할지라도 가로로 3개의 연속되는 돌이 있을 경우
        # 상대방 입장에서 플레이하기 상당히 까다롭다. 이러한 경우가 있을 경우 그 수에 우선적으로 착수한다.
        # 여기서 대각선과 세로로 3개가 연속되는 수는 제외한 이유는 세로로 3개의 연속은 단 1수 만에 막혀버리기 때문에
        # 승리로 이어지기 어렵다고 판단하였고 대각선의 경우는 조건이 워낙 까다로워
        # 실제 게임에서 거의 나타나기 힘들다고 판단했기 때문에 제외하였다.
        # 또 이와 같은 경우의 col이 하나가 아닌 2개 이상이 나타날 수도 있기 때문에 이 경우에는
        # 가운데 열과 가장 가까운 열을 리턴하도록 하였다.
        temp = []
        for col in self.colList:
            if col == 0 or col == 6: 
            # 1열과 7열은 양 옆이 모두 막히지 않는 3개의 가로줄을 만들 수 없으므로 제외한다.
                continue
            if self.possible(col):
                self.put(col)
                dol = self.exists(col, self.getRow(col))
                rowList = [self.exists(i, self.getRow(col)) for i in range(self.width)]
                pattern = [-1, dol, dol, dol, -1]
                # rowList는 직전에 put한 돌의 행의 상태를 나타낸다.
                # pattern은 양옆이 막히지 않는 3개의 돌이 연속된 형태를 나타낸다. 
                # pattern이 rowList에 속할 경우 col을 리턴한다.
                for i in range(self.width - len(pattern) + 1):
                    if pattern == rowList[i:(len(pattern) + i)]:
                        if col >= i+1 and col <= i+3:
                            temp.append(col)
                self.undo()
        if len(temp)==1:
            return temp.pop()
        elif len(temp) >= 2:
            min = 100
            index = -1
            for i in temp:
                i = i-3
                if i < 0:
                    i *= -1
                if i < min:
                    min = i
                    index += 1
            return temp.pop(index)
        else:
            return -1

    def rule7_1(self):
        # 상대방이 양 옆이 막히지 않는 3개의 연속된 돌을 만드는 것을 막는 경우의 수
        # 상대방이 rule7에 의해서 둘 수 있는 경우를 사전에 차단하는 수이다.
        temp = []
        self.posReverse()
        for col in self.colList:
            if col == 0 or col == 6:
                continue
            if self.possible(col):
                self.put(col)
                dol = self.exists(col, self.getRow(col))
                rowList = [self.exists(i, self.getRow(col)) for i in range(self.width)]
                 # 플레이어가 선공이냐 후공이냐에 따라 pattern의 모양이 달라져야 할 것이다.
                pattern = [-1, dol, dol, dol, -1]
                for i in range(self.width - len(pattern) + 1):
                    if pattern == rowList[i:(len(pattern) + i)]: 
                        if col >= i+1 and col <= i+3:
                            temp.append(col)
                self.undo()
        self.posReverse()
        if len(temp)==1:
            return temp.pop()
        elif len(temp) >= 2:
            min = 100
            index = -1
            for i in temp:
                i = i-3
                if i < 0:
                    i *= -1
                if i < min:
                    min = i
                    index += 1
            return temp.pop(index)
        else:
            return -1

    def rule8(self):
        # 내 돌이 가로로 2개가 연속되고 양 옆이 둘 다 비어있을 경우 그 위치에 두는 수
        # 승리하기 위해선 기본적으로 돌이 연속으로 두어져있어야 한다.
        # 특히 4개의 연속된 돌을 만들기 위해서 마지막 한 수를 둘 때 
        # 적어도 보드판에 같은 종류의 돌이 최소 2개는 연속으로 두어져 있어야한다. 그러한 이유로 이러한 룰을 추가하였다.
        # 단 이 경우에는 중복되는 경우가 많아 중복이 있을 경우 가운데에서 가까운 열을 리턴하도록 하였다.
        temp = []
        for col in self.colList:
            self.put(col)
            row = self.getRow(col)
            if col < 6 and col > 0:
                if self.exists(col-1,row) == self.exists(col,row):
                    if col > 1 and self.exists(col-2, row) == -1 and self.exists(col+1,row) == -1:
                        temp.append(col)
                    #return col
                elif self.exists(col,row) == self.exists(col+1,row):
                    if col < 5 and self.exists(col-1,row) == -1 and self.exists(col+2, row) == -1:
                        temp.append(col)
            self.undo()
        # 중복되는 것이 없거나 아예 연속되는 2개의 열을 만들 수 없는 경우 각각 col과 -1을 리턴한다.
        if len(temp) == 1:
            return temp.pop()
        elif len(temp) == 0:
            return -1
        # 그 외 중복이 발생할 경우 가운데에서 가장 가까운 열을 리턴하도록 한다.
        else:
            index = -1
            min = 100
            for col in temp:
                col = col - 3
                if col < 0:
                    col *= -1
                if col < min:
                    min = col
                    index += 1
            return temp.pop(index)
        '''for col in self.colList:
            self.put(col)
            if col < 6 and self.topStone(col+1) == self.topStone(col):
                if (col < 5 and self.topStone(col+2)[0] < self.topStone(col+1)[0]) or (col > 0 and self.topStone(col-1) < self.topStone(col)):
                    self.undo()
                    return col
            self.undo() '''
        #return -1

    def rule8_1(self):
        #rule8에 의해서 상대방이 양 옆이 비어있는 2개의 연속된 돌을 두는 것을 막는 수
        temp = []
        self.posReverse()
        for col in self.colList:
            self.put(col)
            row = self.getRow(col)
            if col < 6 and col > 0:
                if self.exists(col-1,row) == self.exists(col,row):
                    if col > 1 and self.exists(col-2, row) == -1 and self.exists(col+1,row) == -1:
                        temp.append(col)
                    #return col
                elif self.exists(col+1,row) == self.exists(col,row):
                    if col < 5 and self.exists(col-1,row) == -1 and self.exists(col+2, row) == -1:
                        temp.append(col)
            self.undo()
        self.posReverse()
        # 중복되는 것이 없거나 아예 연속되는 2개의 열을 만들 수 없는 경우 각각 col과 -1을 리턴한다.
        if len(temp) == 1:
            return temp.pop()
        elif len(temp) == 0:
            return -1
        # 그 외 중복이 발생할 경우 가운데에서 가장 가까운 열을 리턴하도록 한다.
        else:
            index = -1
            min = 100
            for col in temp:
                col = col - 3
                if col < 0:
                    col *= -1
                if col < min:
                    min = col
                    index += 1
            return temp.pop(index)

    def rule9(self):
        # 선공한 상대방이 가운데 열에 두지 않았을 때 상대방이 둔 열에서 가운데 열 방향으로 한칸 이동해서 두는 수
        # 이 connect4게임에서 선공은 맨 처음에 가운데 열, 즉 4열에 돌을 두지 못한다.
        # 어떻게 보면 Rule 8의 연속이라고 볼 수 있다.
        # 이 경우 이길 확률이 높은 경우는 connect4.solver 사이트에서 참고하였다.
        if len(self.log) == 1:
            if self.log[0] < 3:
                return self.log[0]+1
            else:
                return self.log[0]-1
        return -1

    def rule10(self):
        # 위 룰 중 아무 것도 해당 되지 않는 경우에는 상대방이 착수한 열 위에다 둔다.
        # 1. connect4게임을 AI 사이트와 계속 플레이해보면서 경험한 바로는 수비적으로 플레이할때는
        # 상대방이 두었던 돌 위에 둠으로써 상대방에게 먼저 수를 두도록 강요하는 것이 도움이 된다는 것을 느꼈기 때문이다.
        if len(self.log) != 0:
            col = self.log[-1]
            if self.possible(col) and col in self.colList:
                return col
        return -1
    
    def rule11(self):
        # 만약 상대방이 가장 최근에 둔 열이 가득 차거나 rule3과 rule6로 인해
        # 두지 못할 경우 중앙에서 가장 가까운 열에 둔다.
        # 딱히 둘 곳이 없어 애매한 상황에서는 최대한 가운데에 가까운 열을 먼저 차지하는 것이
        # 유리하다는 생각에서 설정한 룰이다.
        if len(self.log) != 0:
            for col in [3, 2, 4, 1, 5, 0, 6]:
                if col in self.colList:
                    return col
        return -1
    
    def rule12(self):
        # AI가 선공이라서 상대방이 둔 열 위에 두는 것이 불가능할 때 
        # 가운데를 제외한 나머지 3열 또는 5열에 두는 경우
        # 선공인 경우 4열을 제외하고는 3열과 5열이 승률이 가장 높기 때문에 두 곳 중 한 곳에 두도록 설정했다.
        if len(self.log) == 0:
            randint = random.choice([2,4])
            return randint
        return -1

    def rule13(self):
        # 패배가 확정되어서 둘 곳이 없어 colList가 비어있을때 착수 가능한 아무 열이나 출력하는 수
        # colList는 돌을 두어도 패배가 확정되지 않는 열들의 집합인데 colList가 비어있다는 말은
        # 다음턴에 패배하지 않는 경우의 수가 없다는 뜻이 된다.
        # 패배가 확실시 되므로 어느 곳에 두어도 상관이없다. 돌을 두는 것이 가능한 열들 중 한 곳에 둔다.
        if len(self.colList) == 0:
            while True:
                col = random.choice([0,1,2,3,4,5,6])
                if self.possible(col):
                    return col
        return -1
    
    def solver(self):
        # 매 턴마다 colList를 초기화시켜줘야 한다. 그 이유는 rule1,2 등은 colList에 없는 수라 할 지라도
        # 무조건 둬야 하는 우선순위가 더 높은 룰인데, 이전의 룰들에 의해 colList에서 해당 col들이
        # 지워져있을 수도 있기 때문이다.
        self.colList = []
        for col in range(self.width):
            if self.possible(col):
                self.colList.append(col)
        temp = self.colList.copy()
        print()
        col = self.rule1()
        if col >= 0:
            print("Rule1 : AI가 둠으로써 승리하는 수")
            return col

        col = self.rule2()
        if col >= 0:
            print("Rule2 : AI가 두지 않으면 다음 턴에 상대가 승리하는 것을 막는 수")
            return col

        self.rule3()
        if self.colList != temp:
            print('Rule3 : 상대방이 승리하게 되는 착수 점 바로 아래에 착수하지 않도록 열을 제외')
            print("- 현재 착수 가능한 열 목록 : ", end="")
            for col in self.colList:
                # Rule3에 의해서 제외되지 않고 남은 col들을 표시한다.
                print(str(col + 1), end = ' ') 
            print()
            temp = self.colList.copy()
            if len(self.colList) == 1:
                #만약 Rule3에 의해서 제외되고 남은 col이 하나 밖에 없을 경우 그 col을 리턴한다.
                return self.colList[0]
        
        col = self.rule4()
        if col >= 0:
            print("Rule4 : AI가 착수했을 때 다음 턴에 이기는 경우의 수가 2가지가 나와 무조건 승리하게 되는 수")
            return col

        col = self.rule5()
        if col >= 0:
            print("Rule5 : AI가 두지 않을 경우 다음 턴에 상대방이 이기는 경우의 수가 2가지 나오는 것을 막는 수")
            return col

        self.rule6()
        if self.colList != temp:
            print('Rule6 : AI가 이길 수 있는 수 바로 밑에 두지 않음으로써 상대방이 수비를 하지 못하도록 열을 제외')
            print("- 현재 착수 가능한 열 목록 : ", end="")
            for col in self.colList:
                # Rule3에 의해서 제외되지 않고 남은 col들을 표시한다.
                print(str(col + 1), end = ' ') 
            print()
            temp = self.colList.copy()
            if len(self.colList) == 1:
                #만약 Rule3에 의해서 제외되고 남은 col이 하나 밖에 없을 경우 그 col을 리턴한다.
                return self.colList[0]
        
        col = self.rule7()
        if col >= 0:
            print("Rule7 : AI가 3개의 돌을 연속으로 둘 수 있는 수")
            return col
        
        col = self.rule7_1()
        if col >= 0:
            print("Rule7_1 : 상대방이 연속으로 3개의 돌을 둘 수 없게 막는 수")
            return col

        col = self.rule8()
        if col >= 0:
            print("Rule8 : AI의 돌이 2개가 연속되고 양 옆이 둘 다 비어있게 되는 수")
            return col

        col = self.rule8_1()
        if col >= 0:
            print("Rule8_1 : 상대방의 돌이 2개가 연속되고 양 옆이 둘 다 비게되는 것을 막는 수")
            return col

        col = self.rule9()
        if col >= 0:
            print("Rule9 : 선공한 상대방이 4열에 두지 않았을 경우 각 경우마다 가장 이길 확률이 높은 열에 두는 수")
            return col

        col = self.rule10()
        if col >= 0:
            print("Rule10 : 상대방이 직전에 둔 열 위에 따라서 두는 수")
            return col

        col = self.rule11()
        if col >= 0:
            print("Rule11 : 상대방이 직전에 둔 열이 colList에 없어서 두지 못할 경우 가능한 열 중 중앙에서 가까운 열에 두는 수")
            return col

        col = self.rule12()
        if col >= 0:
            print("Rule12 : AI가 선공일 경우 3열 또는 5열에 두는 수")
            return col
        
        col = self.rule13()
        if col >= 0:
            print("Rule13 : colList에 가능한 col이 없어 둘 곳이 없어 착수 가능한 열 중 아무 열이나 두는 수")
            return col

        return random.choice(self.colList)