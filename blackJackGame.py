import random

# 定義全局變量
suits = ['梅花', '方塊', '愛心', '黑桃']
ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
values = {'A': 11, '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9, '10': 10, 'J': 10, 'Q': 10, 'K': 10}

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
        self.hand = []
        self.splitHand = []

    def add_card(self, card: Card):
        self.hand.append(card)

    def get_hand_value(self):
        hand_value = sum(values[card.rank] for card in self.hand)
        # 處理A的特殊情況
        num_aces = sum(1 for card in self.hand if card.rank == 'A')
        while hand_value > 21 and num_aces > 0:
            hand_value -= 10
            num_aces -= 1
        return hand_value

    def display_hand(self, hide_second_card=False):
        hand_str = ', '.join(str(card) for card in self.hand[:1] + [self.hand[1]] * hide_second_card + self.hand[1:])
        print(f'{self.name}的手牌: {hand_str}')

    def get_handNumber(self):
        handNumber = []
        for card in self.hand:
            handNumber.append(card.num)

# 初始化遊戲
def initialize_game(num_computers):
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
            print(f'{player.name}拿到一張{card}')
    players[0].display_hand(hide_second_card=True)

# 玩家輪流進行選擇
def player_turn(player: Player, deck: Deck):
    while True:
        player.display_hand()
        if player.name == '玩家':
            choice = input('請選擇加牌（0）還是停牌（1）：')
            if choice == str(0):
                player.add_card(deck.deal_card())
                if player.get_hand_value() > 21:
                    player.display_hand()
                    print(f'{player.name}爆牌！')
                    break
            elif choice == str(1):
                break
            else:
                print('請輸入有效選項（0或1）！')

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
def show_results(players: list[Player], dealer: Player):
    dealer_value = dealer.get_hand_value()
    print(f'\n莊家的手牌：{", ".join(str(card) for card in dealer.hand)}')
    print(f'莊家的點數：{dealer_value}\n')

    for player in players:
        if player != dealer:
            player_value = player.get_hand_value()
            if player_value > 21:
                print(f'{player.name}爆牌！，點數:{player_value}')
                if player.name=="玩家":
                    score=-10-30
            elif player_value > dealer_value or dealer_value > 21:
                print(f'{player.name}贏了！，點數:{player_value}')
                score=player_value+30
            elif player_value == dealer_value:
                print(f'{player.name}與莊家平手！，點數:{player_value}')
                score=player_value
            else:
                print(f'{player.name}輸了！，點數:{player_value}')
                score=player_value-30
    return score

# 主要遊戲邏輯
def play_game():
    num_games = 1

    while True:
        num_computers = random.randint(0, 4)
        players, deck = initialize_game(num_computers)
        deal_initial_cards(players, deck)

        for player in players:
            if player != players[0]:  # 不是莊家的回合
                player_turn(player, deck)

        dealer_turn(players[0], deck)
        show_results(players[1:], players[0])
        x = input("按A停止，任意鍵繼續")
        if x.lower() == 'a':
            break
        print(f"你你已經進行{num_games}場遊戲")
        num_games += 1

# 遊戲開始
play_game()
