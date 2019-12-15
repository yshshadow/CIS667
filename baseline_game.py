from player import MCST, Dummy
import random
import os
import pandas as pd

BASE_DECK = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13] * 4


baseline_data = []
stats_2_2 = [0] * 6
stats_2_4 = [0] * 6
stats_3_3 = [0] * 6
stats_1_2 = [0] * 6
stats_3_4 = [0] * 6


def stats(id, deck_size, player_size):
    if (player_size == 2 and deck_size == 2):
        stats_2_2[id] += 1
    elif (player_size == 4 and deck_size == 2):
        stats_2_4[id] += 1
    elif (player_size == 3 and deck_size == 3):
        stats_3_3[id] += 1
    elif (player_size == 2 and deck_size == 1):
        stats_1_2[id] += 1
    elif (player_size == 4 and deck_size == 3):
        stats_3_4[id] += 1
    else:
        print("error")


class Game(object):

    def __init__(self, deck_size, player_size):
        self.deck_size = deck_size  # how many decks will be used
        self.player_size = player_size  # how many players will join the game, at least 1
        self.deck = BASE_DECK * 4  # generate deck list
        random.shuffle(self.deck)
        self.used_deck = []
        self.players = []
        self.stopped_count = []
        self.dealer_hand = self.deal()  # get two cards for dealer
        # generate players, the player 0 is AI, others are dummy
        for i in range(self.player_size):
            player = Dummy(i)
            self.players.append(player)
            self.stopped_count.append(False)
            player.hand = self.deal()
            if self.total(player.hand) == 21:
                print("Player {} is black jack".format(i))

    def total(self, hand):  # cal the total of a hand
        total = 0
        for card in hand:
            if card == "J" or card == "Q" or card == "K":
                total += 10
            elif card == "A":
                if total >= 11:
                    total += 1
                else:
                    total += 11
            else:
                total += card
        return total

    def deal(self):  # deal first 2 cards
        hand = []
        for i in range(2):
            card = self.deck.pop()
            if card == 11:
                card = "J"
            if card == 12:
                card = "Q"
            if card == 13:
                card = "K"
            if card == 1:
                card = "A"
            hand.append(card)
            self.used_deck.append(card)
        return hand

    def hit(self, hand):  # draw a card from deck
        card = self.deck.pop()
        if card == 11:
            card = "J"
        if card == 12:
            card = "Q"
        if card == 13:
            card = "K"
        if card == 1:
            card = "A"
        hand.append(card)
        self.used_deck.append(card)
        return hand

    def swap_card(self, hand, hand_target, other_hand, other_hand_target):
        hand.remove(hand_target)
        hand.append(other_hand_target)
        other_hand.remove(other_hand_target)
        other_hand.append(hand_target)

    def swap(self, player):  # swap with a random player
        hand = player.hand
        swap_player = random.choice(self.players)
        while swap_player.id == player.id:
            swap_player = random.choice(self.players)
        other_hand = swap_player.hand
        hand_target = random.choice(hand)
        other_hand_target = random.choice(other_hand)
        self.swap_card(hand, hand_target, other_hand, other_hand_target)

    def print_results(self, dealer_hand, player_hand):
        print("The dealer has a " + str(dealer_hand) +
              " for a total of " + str(self.total(dealer_hand)))
        print("You have a " + str(player_hand) +
              " for a total of " + str(self.total(player_hand)))

    def score(self, id, dealer_hand, player_hand):
        if self.total(player_hand) == 21:
            self.print_results(dealer_hand, player_hand)
            stats(0, self.deck_size, self.player_size)
            print("Congratulations! Player {} got a Blackjack!\n".format(id))
        elif self.total(dealer_hand) == 21:
            self.print_results(dealer_hand, player_hand)
            stats(1, self.deck_size, self.player_size)
            print("Sorry, Player {} lose. The dealer got a blackjack.\n".format(id))
        elif self.total(player_hand) > 21:
            self.print_results(dealer_hand, player_hand)
            stats(2, self.deck_size, self.player_size)
            print("Sorry. Player {} busted. You lose.\n".format(id))
        elif self.total(dealer_hand) > 21:
            self.print_results(dealer_hand, player_hand)
            stats(3, self.deck_size, self.player_size)
            print("Dealer busts. Player {} win!\n".format(id))
        elif self.total(player_hand) < self.total(dealer_hand):
            self.print_results(dealer_hand, player_hand)
            stats(4, self.deck_size, self.player_size)
            print(
                "Sorry. Player {}'s score isn't higher than the dealer. Player {} lose.\n".format(id, id))
        elif self.total(player_hand) > self.total(dealer_hand):
            self.print_results(dealer_hand, player_hand)
            stats(5, self.deck_size, self.player_size)
            print(
                "Congratulations. Player {}'s score is higher than the dealer. Player {} win\n".format(id, id))

    def card_to_index(self, card):
        if card == "J":
            card = 11
        if card == "Q":
            card = 12
        if card == "K":
            card = 13
        if card == "A":
            card = 1
        return card

    def to_card_vector(self):
        vector = [0] * 13
        for card in self.used_deck:
            vector[self.card_to_index(card)-1] += 1
        return vector

    def game(self):
        choice = 0
        print("WELCOME TO BLACKJACK!\n")
        if self.total(self.dealer_hand) == 21:
            print("Dealer is black jack, all players lose")
            self.stopped_count = [True] * self.player_size
            return
        play_turn = 1
        while not all(self.stopped_count):  # stop loop until all players stop

            current_player = self.players.pop(0)
            self.players.append(current_player)

            if(self.stopped_count[current_player.id]):
                continue

            print("Turn: {}".format(play_turn))
            print("The dealer is showing a " +
                  str(self.dealer_hand))

            print("Player {} has a ".format(current_player.id) + str(current_player.hand) +
                  " for a total of " + str(self.total(current_player.hand)))

            print("Player {}'s turn [H]it, s[W]ap, [S]top: ".format(
                current_player.id))
            action, _ = current_player.get_action()  # get action
            # For AI player, the action is generated by model.
            # For dummy player, the action is chosen randomly
            data = []
            if action == 1:  # Hit
                data += [1, 0, 0]  # add action
                print("Player {} choose [H]it".format(current_player.id))
                self.hit(current_player.hand)
                total_score = self.total(current_player.hand)
                print("After hit, Player {}'s hand is {}, score is {}".format(
                    current_player.id, current_player.hand, total_score))
                if (total_score > 21):
                    self.stopped_count[current_player.id] = True
                    print("Sorry. Player {} busted.".format(current_player.id))
            elif action == 2:  # Swap
                data += [0, 1, 0]  # add action
                print("Player {} choose s[W]ap".format(current_player.id))
                self.swap(current_player)
                total_score = self.total(current_player.hand)
                print("After swap, Player {}'s hand is {}, score is {}".format(
                    current_player.id, current_player.hand, self.total(current_player.hand)))
                for i in range(self.player_size):
                    if (not self.stopped_count[self.players[i].id] and self.total(self.players[i].hand) > 21):
                        self.stopped_count[self.players[i].id] = True
                        print("Sorry. Player {} busted.".format(
                            self.players[i].id))
            elif action == 3:  # Stop
                data += [0, 0, 1]  # add action
                print("Player {} choose [S]top".format(current_player.id))
                self.stopped_count[current_player.id] = True
                print("Player {} stop.".format(current_player.id))
            data += self.to_card_vector()  # card info
            data += [self.total(current_player.hand)]  # total after action
            baseline_data.append(data)
            play_turn += 1  # move to next turn
        print("All players stop, dealer's turn")
        while self.total(self.dealer_hand) < 17:  # hit until greater than 17
            self.hit(self.dealer_hand)
        for player in self.players:
            # compare dealer and each player
            self.score(player.id, self.dealer_hand, player.hand)


if __name__ == "__main__":
    for i in range(100):
        Game(2, 2).game()
    for i in range(100):
        Game(2, 4).game()
    for i in range(100):
        Game(3, 3).game()
    for i in range(100):
        Game(1, 2).game()
    for i in range(100):
        Game(3, 4).game()
    pd.DataFrame(baseline_data).to_csv("./data/baseline_data.csv", header=None)
    s12 = pd.DataFrame(stats_1_2).transpose()
    s22 = pd.DataFrame(stats_2_2).transpose()
    s24 = pd.DataFrame(stats_2_4).transpose()
    s33 = pd.DataFrame(stats_3_3).transpose()
    s34 = pd.DataFrame(stats_3_4).transpose()

    statistic = pd.concat([s12, s22, s24, s33, s34], axis=0)
    statistic.columns = ['1','2','3','4','5','6']
    statistic.reset_index(drop = True, inplace = True)
    statistic.index = ['1-2','2-2','2-4','3-3','3-4']
    print(statistic)
    statistic.to_csv("./data/base_stats.csv")
