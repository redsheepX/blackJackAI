import random
from AIAgent import Agent
import time
from helper import plot
# 定義全局變量
suits = ['梅花', '方塊', '愛心', '黑桃']
ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
values = {'A': 11, '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9, '10': 10, 'J': 10, 'Q': 10, 'K': 10}
agent=Agent()
agent.initData()
players=[]
num_games = 1
plt_score = []
plt_average_score=[]
total_score=0
flag = False


# 定義卡片類別
class Card:
    def __init__(self, num):
        self.num = num

        if num <= 13:
            self.suit = suits[0]
        elif num <= 26:
            self.suit = suits[1]
        elif num <= 39:
            self.suit = suits[2]
        elif num <= 52:
            self.suit = suits[3]

        while num > 13:
            num -= 13
        self.rank = ranks[num - 1]

    def __str__(self):
        return f'{self.suit}{self.rank}'

# 定義牌組類別
class Deck:
    def __init__(self):
        self.deck = []
        for i in range(8):
            for j in range(52):
                self.deck.append(Card(j + 1))

    def shuffle(self):
        random.shuffle(self.deck)

    def deal_card(self):
        return self.deck.pop()

# 定義玩家類別
class Player:
    def __init__(self, name):
        self.name = name
        self.hand:list[Card] = []
        self.handDouble=False
        self.handDone=False
        self.splitHand:list[Card] = []
        self.split_handDouble=False
        self.split_handDone=True
        
    def add_card(self, card: Card , addSplitHand=False):
        if addSplitHand:
            self.splitHand.append(card)
        else:
            self.hand.append(card)

    def get_hand_value(self):
        hand_value = sum(values[card.rank] for card in self.hand)
        # 處理A的特殊情況
        num_aces = sum(1 for card in self.hand if card.rank == 'A')
        while hand_value > 21 and num_aces > 0:
            hand_value -= 10
            num_aces -= 1
        return hand_value
    
    def get_split_hand_value(self):
        hand_value = sum(values[card.rank] for card in self.splitHand)
        # 處理A的特殊情況
        num_aces = sum(1 for card in self.splitHand if card.rank == 'A')
        while hand_value > 21 and num_aces > 0:
            hand_value -= 10
            num_aces -= 1
        return hand_value

    def display_hand(self, hide_second_card=False):
        if hide_second_card:
            dealer_show=self.hand
            dealer_show.pop(1)
            hand_str = ', '.join(str(card) for card in dealer_show)
        else:
            hand_str = ', '.join(str(card) for card in self.hand)
        print(f'{self.name}的手牌: {hand_str}')
        
    def display_split_hand(self):
        hand_str = ', '.join(str(card) for card in self.splitHand)
        print(f'{self.name}的手牌: {hand_str}')

    def get_handNumber(self):
        handNumber = []
        for card in self.hand:
            handNumber.append(card.num)

# 初始化遊戲
def initialize_game(num_computers):
    global players
    players = [Player('莊家')]
    for i in range(num_computers):
        players.append(Player(f'電腦{i + 1}'))
    players.append(Player('玩家'))
    random.shuffle(players)
    if players[0].name != '莊家':
        # 如果第一個玩家不是莊家，則將莊家移動到列表的開始位置
        for i, player in enumerate(players):
            if player.name == '莊家':
                players[0], players[i] = players[i], players[0]
                break
    deck = Deck()
    deck.shuffle()
    return players, deck


# 發牌
def deal_initial_cards(players: list[Player], deck: Deck):
    for _ in range(2):
        for player in players:
            card = deck.deal_card()
            player.add_card(card)
    players[0].display_hand(hide_second_card=True)

# 玩家輪流進行選擇
def player_turn(player: Player, deck: Deck):
   
    global players,agent, flag
    if player.name == '玩家':
        while not player.handDone:
            player.display_hand()
            agent.state_old1  = agent.get_state(StateDict=toState(players))
            agent.final_move1 = agent.get_action(agent.state_old1,num_games)
            choice = str(agent.final_move1)
            if choice == str(0): #Hit
                print(f"玩家選擇: Hit")
                player.add_card(deck.deal_card())
                if player.get_hand_value() > 21:
                    player.display_hand()
                    print(f'{player.name}爆牌！')
                    player.handDone=True
                    
            elif choice == str(1): #Stand
                print(f"玩家選擇: Stand")
                player.handDone=True
                
            elif choice == str(2): #Double
                print(f"玩家選擇: Double")
                if not player.handDouble:
                    player.add_card(deck.deal_card())
                    player.handDouble=True
                    player.handDone=True
                    
            elif choice == str(3): #Split
                print(f"玩家選擇: Split")
                if (values[player.hand[0].rank] == values[player.hand[1].rank]) and (len(player.hand)==2):
                    player.splitHand.append(player.hand.pop())
                    player.add_card(deck.deal_card())
                    player.add_card(deck.deal_card(),addSplitHand=True)
                    player.split_handDone=False
                else:
                    print("無法分牌")
                    break
            else:
                print('請輸入有效選項（0或1或2或3）！')
                break
            if player.get_hand_value()>21:
                agent.reward= -10
            else:
                agent.reward= player.get_hand_value()
            
            agent.state_new1=agent.get_state(StateDict=toState(players))
            agent.train_short_memory(agent.state_old1,agent.final_move1,agent.reward,agent.state_new1,0)
            agent.remember(agent.state_old1,agent.final_move1,agent.reward,agent.state_new1,0)   
                
        while not player.split_handDone:
            player.display_split_hand()
            agent.state_old2  = agent.get_state(StateDict=toState(players,splitHand=True))
            agent.final_move2 = agent.get_action(agent.state_old2,num_games)
            choice = agent.final_move2
            if choice == 0: #Hit
                player.add_card(deck.deal_card(),addSplitHand=True)
                if player.get_split_hand_value() > 21:
                    player.display_split_hand()
                    print(f'{player.name}爆牌！')
                    player.split_handDone=True
                    break
            elif choice == 1: #Stand
                player.split_handDone=True
                break
            elif choice == 2: #Double
                if not player.split_handDouble:
                    player.add_card(deck.deal_card(),addSplitHand=True)
                    player.split_handDouble=True
                    break
            elif choice==3:
                print("無法分牌")
                break
            else:
                print(choice)
                print('請輸入有效選項（0或1或2或3）！')
                exit()
            if player.get_split_hand_value()>21:
                agent.reward= -10
            else:
                agent.reward= player.get_split_hand_value()
            
            agent.state_new2=agent.get_state(StateDict=toState(players,splitHand=True))
            agent.train_short_memory(agent.state_old2,agent.final_move2,agent.reward,agent.state_new2,0)   
            agent.remember(agent.state_old2,agent.final_move2,agent.reward,agent.state_new2,0)   
            flag=True
    else:
        player.display_hand()
        

        

# 莊家的回合
def dealer_turn(dealer: Player, deck: Deck):
    dealer.display_hand(hide_second_card=False)
    while dealer.get_hand_value() < 17:
        dealer.add_card(deck.deal_card())
        dealer.display_hand(hide_second_card=False)
        if dealer.get_hand_value() > 21:
            print(f'{dealer.name}爆牌！')
            break

# 顯示最終結果
def show_results(part_players: list[Player], dealer: Player):
    global num_games,agent,players,total_score
    dealer_value = dealer.get_hand_value()
    dealer_len = len(dealer.hand)
    print(f'\n莊家的手牌：{", ".join(str(card) for card in dealer.hand)}')
    print(f'莊家的點數：{dealer_value}\n')
    score=0
    score2=0
    
    for player in part_players:
        if player != dealer:
            player_value = player.get_hand_value()
            
            if player.handDouble:
                winPoint=60
            else:
                winPoint=30
                
            if player_value > 21:
                print(f'{player.name}爆牌！，點數:{player_value}')
                if player.name=="玩家":
                    score+= -10 - winPoint
            elif len(player.hand)>=5 and dealer_len<5:
                print(f'{player.name}五小龍！，點數:{player_value}')
                if player.name=="玩家":
                    score += 30 +(winPoint*1.5)
            elif len(player.hand)>=5 and dealer_len>=5 and dealer_value < 21:
                print(f'{player.name}五小龍！，點數:{player_value}')
                if player.name=="玩家":
                    score += 30
            elif player_value > dealer_value or dealer_value > 21:
                print(f'{player.name}贏了！，點數:{player_value}')
                if player.name=="玩家":
                    score += player_value+winPoint
            elif player_value == dealer_value:
                print(f'{player.name}與莊家平手！，點數:{player_value}')
                if player.name=="玩家":
                    score += player_value
            else:
                print(f'{player.name}輸了！，點數:{player_value}')
                if player.name=="玩家":
                    score += player_value-winPoint
                    
            if player.name=="玩家":
                print(f"玩家牌1 得分{score}")
            if len(player.splitHand)>0:
                if player.split_handDouble:
                    winPoint=60
                else:
                    winPoint=30
                player_value = player.get_split_hand_value()
                if player_value > 21:
                    print(f'{player.name}爆牌！，點數:{player_value}')
                    if player.name=="玩家":
                        score2 += -10 - winPoint
                elif len(player.splitHand)>=5 and dealer_len<5:
                    print(f'{player.name}五小龍！，點數:{player_value}')
                    if player.name=="玩家":
                        score2 += 30 +(winPoint*1.5)
                elif len(player.splitHand)>=5 and dealer_len>=5 and dealer_value < 21:
                    print(f'{player.name}五小龍！，點數:{player_value}')
                    if player.name=="玩家":
                        score2 += 30
                elif player_value > dealer_value or dealer_value > 21:
                    print(f'{player.name}贏了！，點數:{player_value}')
                    if player.name=="玩家":
                        score2 += player_value+winPoint
                elif player_value == dealer_value:
                    print(f'{player.name}與莊家平手！，點數:{player_value}')
                    if player.name=="玩家":
                        score2 += player_value

                else:
                    print(f'{player.name}輸了！，點數:{player_value}')
                    if player.name=="玩家":
                        score2 += player_value - winPoint
                if player.name=="玩家":
                    print(f"玩家牌2 得分{score2}")
    totalScore=score+score2
    plt_score.append(totalScore)
    total_score += totalScore
    plt_average_score.append(sum(plt_score)/num_games)
    
    agent.state_new1=agent.get_state(toState(players))
    print('3')
    agent.train_short_memory(agent.state_old1,agent.final_move1,totalScore,agent.state_new1,1)
    agent.remember(agent.state_old1,agent.final_move1,totalScore,agent.state_new1,1)
    
    if len(player.splitHand)>0:
        agent.state_new2=agent.get_state(toState(players,True))
        print('4')
        agent.train_short_memory(agent.state_old2,agent.final_move2,totalScore,agent.state_new2,1)
        agent.remember(agent.state_old2,agent.final_move2,totalScore,agent.state_new2,1)
    if totalScore >0:
        agent.model.save()

    plot(plt_score, plt_average_score)
        
        
        
    return totalScore


def toState(players:list[Player],splitHand=False):
    state={}
    state["usedCard"]={}
    state["player_hand"]={}
    state["player_splitHand"]={}
    state["dealer_deck"]={}
    for i in range(52):
        state["usedCard"][i+1]=0
        state["player_hand"][i+1]=0
        state["player_splitHand"][i+1]=0
        state["dealer_deck"][i+1]=0
    for player in players:
        if player == players[0]:
            state["dealer_deck"][player.hand[0].num] += 1
            state["dealer_value"]={"value":values[player.hand[0].rank]}
            state["usedCard"][player.hand[0].num] += 1
        else:
            for card in player.hand:
                state["usedCard"][card.num] += 1
                if player.name == "玩家":
                    state["player_hand"][card.num] += 1
                    state["player_value"]={"value":player.get_hand_value()}
                    state["player_boom"]={"boom":player.get_hand_value()>21}
            if len(player.splitHand)>0:
                for card in player.hand:
                    state["usedCard"][card.num] += 1
                    state["player_splitHand"][card.num] += 1
                    state["split_value"]={"value":player.get_split_hand_value()}
                    state["split_boom"]={"boom":player.get_split_hand_value()>21}
            else:
                state["split_value"]={"value":0}
                state["split_boom"]={"boom":False}
    if not splitHand:
        sortList=["player_hand","player_value","player_boom","player_splitHand","split_value","split_boom","dealer_deck","dealer_value","usedCard"]
    
    if splitHand:
        sortList=["player_splitHand","split_value","split_boom","player_hand","player_value","player_boom","dealer_deck","dealer_value","usedCard"]
    sortDict={}
    for i in sortList:
        sortDict[i]=state[i]

    return sortDict
            
        
        
    


# 主要遊戲邏輯
def play_game():
    global num_games,agent,total_score, flag
    while True:
        print('-----start-----')
        flag=False
        num_computers = random.randint(0, 4)
        players, deck = initialize_game(num_computers)
        deal_initial_cards(players, deck)

        for player in players:
            if player != players[0]:  # 不是莊家的回合
                player_turn(player, deck)

        dealer_turn(players[0], deck)
        show_results(players[1:], players[0])
        agent.train_long_memory()
        
        print(f"你你已經進行{num_games}場遊戲")
        print(f"累積輸贏:{total_score}")
        if num_games%100 ==0:
            input("123")
        num_games += 1
        print('-----finish-----')
        

# 遊戲開始
play_game()

    


