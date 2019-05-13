Connect four AI algoritm
========================


## 프로젝트 설명
- connect four 게임을 플레이하는 프로그램입니다.
- Game tree search algorithm와 Rule based을 이용한 AI를 구현하였습니다.
    * 사용한 기법    
  - Mini-Max algorithm
  - Alpha-Beta pruning
  - Partial tree
  - Heuristic function
  - Iterative deepening
  - Dynamic programming




## 이용 방법
1. 사용자가 번갈아가며 진행합니다. 선공은 'O', 후공은 'X'로 표시됩니다.
2. 원하는 column number를 고르면 board에 표시가 됩니다.



## 개발 환경
1. 언어 : Python 3.7.3
2. OS : Mac OS, Windows 10 등



## 파일 설명
- **play.py** : connect four 게임을 플레이하기 위해 기본적으로 실행하는 파일입니다.
- **board.py** : connect four 게임을 하기 위해 board에서 이루어지는 기능들을 구현한 파일입니다.
- **heuristic.py** : heuristic value를 계산하는 파일입니다.
- **gameTree.py** : connect four에서 최적의 수를 두기 위한 game tree를 구현한 파일입니다.
- **rule.py** : rule based 방식에 사용되는 rule들을 구현한 파일입니다.  
  
  
## 프로젝트 개발자, 참고 사이트
- 개발자 : 윤영일, 문승연
- 참고 사이트 : https://everycoding.net/code/ai/127

