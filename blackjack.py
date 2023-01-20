import random

def game_settings():
    while True:
        try:
            max_players = abs(int(input('PLAYERS (1-7): ')))
            start_money = abs(int(input('STARTING MONEY: ')))
            min_bet = abs(int(input('MINIMUM BET: ')))

            if not max_players or max_players > 7:
                print('Invalid number of players.')
                continue
            elif not start_money or not min_bet:
                print('Your selection cannot be zero.')
                continue
            elif start_money < min_bet:
                print('Minimum bet cannot be higher than starting money.')
                continue
            else:
                break

        except:
            print('Wrong input, try again.')

    return max_players, start_money, min_bet

def register_players(start_money, max_players):

    player_num = 1
    players = []

    while len(players) < max_players:
        player_name = input('Enter name of player {}: '.format(player_num)).upper()
        if player_name:
            players.append([player_name, start_money])
        else:
            print('No input, try again.')
        player_num += 1

    players.append(['house', 1000])

    return players

def create_deck():
    TYPES = ['♠', '♥', '♣', '♦']
    VALUES = ['A', 2, 3, 4, 5, 6, 7, 8, 9, 10, 'J', 'Q', 'K']

    deck = [type+str(value) for type in TYPES for value in VALUES]

    return deck

def shuffle_deck(deck):
    random.shuffle(deck)

    return deck

def place_bets(players, min_bet):
    print('='*50)
    in_game = []

    for i, (player, money) in enumerate(players[:-1]):
        if money >= min_bet:
            while True:
                bet = input('Player {} place your bet (${}): '.format(player, str(money)))
                if bet.isnumeric() and min_bet <= int(bet) <= money:
                    players[i][1] -= int(bet)
                    in_game.append([player, int(bet), []])
                    break
                else:
                    print('Wrong input, try again.')
        else:
            print('Sorry, player', player, 'is out of money.')
            players.pop(i)

    in_game.append(['house', '-', []])

    return in_game

def serve_players(in_game, deck):
    for i in range(2):
        p = in_game if i == 0 else in_game[:-1]
        for player in p:
            player[-1].append(deck.pop())

def check_hand(hand):
    values = 0
    aces = 0
    for card in hand:
        if card[1:] in "JQK":
            values += 10
        elif card[1:] == 'A':
            values += 11
            aces += 1
        else:
            values += int(card[1:])

    if values > 21 and aces > 0:
        values -= 10*aces
    return values

def draw(deck, player, hand):
    while 'y' == input('Press "y" if you want to pick another card? '):
        hand.append(deck.pop())
        on_hand = check_hand(hand)

        print(player + ' has ' + str(on_hand) + ': ' + ' '.join(hand))

        if on_hand > 21:
            print(player, 'bust!')
            break
        elif on_hand == 21:
            break

def show_table(game):
    col = len(max((players[0] for players in game), key=len))
    table_template = '{:>'+str(col)+'} | {:<3} {:<3} | {:<2} | ${}'

    for player, bet, hand in game[:-1]:
        print(table_template.format(player, hand[0], hand[1], check_hand(hand), bet))
    print('\nHouse has ' + str(check_hand(game[-1][-1])) + ': ' + ' '.join(game[-1][-1]))

def show_results(real_player, string):
    print(real_player[0] + string)
    print('Current bank: $' + str(real_player[1]))

def evaluate(game, players):
    house = game.pop()
    house_on_hand = check_hand(house[-1])
    print('House has ' + str(house_on_hand) + ': ' + ' '.join(house[-1]))

    print('='*25)

    num_splitted = 0

    for i,(player, bet, hand) in enumerate(game):
        on_hand = check_hand(hand)

        if player[-3:] == '(2)':
            num_splitted += 1

        real_player = players[i-num_splitted]

        if (on_hand == 21 and len(hand) == 2) and \
            not(house_on_hand == 21 and len(house[-1])==2): # blackjack 1.5x
            real_player[1] += bet + bet*1.5
            show_results(real_player, ' got blackjack!')

        elif on_hand > 21 or on_hand < house_on_hand <= 21: # loss
            show_results(real_player, ' lost!')

        elif on_hand > house_on_hand or on_hand <= 21 < house_on_hand: # win 2x
            real_player[1] += bet + bet
            show_results(real_player, ' wins!')

        elif on_hand == house_on_hand:
            real_player[1] += bet
            show_results(real_player, ' ties!')

        print('-'*25)

    return players

def play(players, min_bet):
    deck = shuffle_deck(create_deck())
    game = place_bets(players, min_bet)
    serve_players(game, deck)

    print('-'*50)
    show_table(game)

    for i,(player, bet, hand) in enumerate(game):
        print('-'*50)
        on_hand = check_hand(hand)

        if player == 'house': #aby si house dobral karty, ale uz se neresilo ostatni
            while check_hand(hand) < 17:
                hand.append(deck.pop())
            continue

        elif len(hand) == 1: # vyresit nejak jinak!
            hand.append(deck.pop()) # potreba pri splitu, aby to nehodilo indexerror
            print(player + ' has ' + str(on_hand) + ': ' + ' '.join(hand))
            if check_hand(hand) < 21:
                draw(deck, player, hand)
            continue

        print(player + ' has ' + str(on_hand) + ': ' + ' '.join(hand))

        if on_hand == 21: #blackjack
            pass # nebo continue?

        elif hand[0][1:] == hand[1][1:] and players[i][1] >= bet and \
            'y' == input(player + ', enter "y" if you want to split. '):
            game.insert(i+1,[player+'(2)',bet,[hand.pop()]])
            players[i][1] -= bet
            hand.append(deck.pop()) #co kdyz splitnu a hned doberu na 21?
            print(player + ' has ' + str(on_hand) + ': ' + ' '.join(hand))
            if check_hand(hand) < 21:
                draw(deck, player, hand) #vyresit nejak jinak!

        elif on_hand <= 11 and players[i][1] >= bet and \
            'y' == input(player + ', enter "y" if you want to double down. '):
            game[i][1] *= 2 #zjistit, jestli by to slo udelat i pres bet*=2
            players[i][1] -= bet
            hand.append(deck.pop())
            print(player + ' has ' + str(check_hand(hand)) + ': ' + ' '.join(hand))

        elif on_hand < 21:
            draw(deck, player, hand)

    evaluate(game, players)


def main():
    print('='*50)
    print('Welcome to my simple blackjack game!')
    print('-'*50)
    print('PLAYERS: 6\nSTARTING MONEY: $50\nMINIMUM BET: $5')

    max_players = 6
    start_money = 50
    min_bet = 5

    if 'y' == input('Enter "y" to change default settings or any key to continue: '):
        max_players, start_money, min_bet = game_settings()
    print('-'*50)

    players = register_players(start_money, max_players)

    while len(players) > 1:
        play(players, min_bet)

        if 'q' == input('Enter any key to start another game or "q" to quit: '):
            print('Thanks for playing!')
            break
        
if __name__ == '__main__':
    main()