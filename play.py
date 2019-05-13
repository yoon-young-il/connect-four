from gameTree import GameTree
from rule import Rule
from time import time

# 1. 기본 정보 입력
# 1-1. Rule based와 Game tree search 선택
mode = "mode"
while mode not in ["S", "s", "R", "r"]:
    mode = input("1. 룰 베이스 기반을 원한다면 'R', 서치 기반을 원한다면 'S'를 입력해 주십시오. : ")
# 1-2. 선공/후공 선택
player = 'input'
while player not in ['Y', 'y', 'Yes', 'YES', 'yes', 'O', 'o', 'N', 'n', 'No', 'no', 'X', 'x']:
    player = input('2. 먼저 하시겠습니까? (Y/N) - ')
player = (player in ['Y', 'y', 'Yes', 'YES', 'yes', 'O', 'o']) and 1 or 0        # AI 기준으로 선공 = 0, 후공 = 1
# 1-3. 기본 정보를 바탕으로 GameTree/Rule class 선언
connect4 = (mode == 'S' or mode == 's') and GameTree(player) or Rule(player)

for i in range(connect4.width * connect4.height):
    # 2. board 출력
    print()
    connect4.printBoard()

    # 3. AI's turn
    if i % 2 == player:
        # 3-1. Game tree search 일때는 걸린 시간을 체크하여 출력
        if mode == 'S' or mode == 's':
            startTime = time()
            col = connect4.search(startTime)
            print('걸린 시간 : ' + str(time() - startTime))
        # 3-2. Rule based
        else:
            col = connect4.solver()
        # 3-3. 결과론 나온 column에 착수한다
        connect4.put(col)
        print("\nAI가 " + str(col+1) + "열에 착수하였습니다.")

    # 4. Human's turn
    else:
        while True:
            try:
                # 4-1. 두고 싶은 stone의 column number를 입력받는다
                print()
                col = int(input(str(i+1) + '. ' + (connect4.moves % 2 == player and 'AI' or 'Human') + '\'s turn(' + (connect4.moves % 2 == 0 and 'O' or 'X') + ') : ')) - 1                
                # 4-2. 첫 턴에 가운데에 둘 경우 error
                if connect4.width == 7 and connect4.moves == 0 and col == 3:
                    raise WrongInput
                # 4-3. 잘못된 범위에 둘 경우 error
                if col < 0 or col >= connect4.width:
                    raise WrongInput
                # 4-4. 해당 column에 이미 stone이 가득 찼다면 error
                if not connect4.possible(col):
                    raise WrongInput
                # 4-5. 문제가 없다면 stone을 착수
                connect4.put(col)
                break
            # error가 발생한 경우에는 error message와 함께 다시 진행한다
            except:
                print('Wrong input! Try again.')

    # 5. 게임에서 이긴 경우
    if connect4.win():
        print()
        connect4.printBoard()
        print('\n' + (connect4.moves % 2 != player and 'AI' or 'Human') + '\'s win!')
        break
# 6. 게임에서 비긴 경우
else:
    print()
    connect4.printBoard()
    print('\nDraw!')