import random
import math
import sys
import copy
from filter import *
import filter
import pandas as pd
import torch as tr
MAX_COMPUTATION = 1000
AVAILABLE_CHOICES = [1, 2, 3]
AVAILABLE_CHOICE_NUMBER = len(AVAILABLE_CHOICES)
MAX_ROUND_NUMBER = 20
NN_CONFIG = 4

if (NN_CONFIG == 1):
    nn_filter = NumericNet1(16)
    nn_filter.load_state_dict(tr.load("./nn1"))
elif (NN_CONFIG == 2):
    nn_filter = NumericNet2(16)
    nn_filter.load_state_dict(tr.load("./nn2"))
elif (NN_CONFIG == 3):
    nn_filter = NumericNet3(16)
    nn_filter.load_state_dict(tr.load("./nn3"))
elif (NN_CONFIG == 4):
    nn_filter = NumericNet4(16)
    nn_filter.load_state_dict(tr.load("./nn4"))
else:
    nn_filter = None


class Node(object):
    def __init__(self):
        self.parent = None
        self.children = []
        self.visit_times = 0
        self.quality_value = 0.0
        self.state = None

    def is_all_expand(self):
        if len(self.children) == AVAILABLE_CHOICE_NUMBER:
            return True
        else:
            return False

    def add_child(self, sub_node):
        sub_node.parent = self
        self.children.append(sub_node)


class State(object):  # State of game
    def __init__(self, deck, used_deck, hand):
        self.current_value = 0.0  # current total of hand
        self.current_round_index = 0  # the iteration round / depth in the tree
        self.cumulative_choices = []
        self.deck = deck
        self.used_deck = used_deck
        self.hand = hand
        self.stopped = False
        self.filtered = False
        self.choice = -1

    def is_terminal(self):  # game terminate when: 1.bust, 2.reach 21, 3.reach max round
        if self.current_round_index == MAX_ROUND_NUMBER-1 or self.current_value == 21 or self.stopped:
            return True
        else:
            return False

    def to_value(self, card):
        if card == "J" or card == "Q" or card == "K":
            value = 10
        elif card == "A":
            if self.current_value >= 11:
                value = 1
            else:
                value = 11
        else:
            value = card
        return value

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

    def compute_reward(self):
        return 21-self.current_value

    def get_next_state_with_random_choice(self):  # get next state
        choice = random.choice([choice for choice in AVAILABLE_CHOICES])
        self.choice = choice
        next_deck = copy.deepcopy(self.deck)
        next_used_deck = copy.deepcopy(self.used_deck)
        next_hand = copy.deepcopy(self.hand)
        if choice == 1:  # hit
            # process deck
            random_throw = random.choice(next_deck)
            next_used_deck.append(random_throw)
            next_hand.append(random_throw)
            next_deck.remove(random_throw)
            next_state = State(next_deck, next_used_deck, next_hand)
            next_state.current_value = self.current_value + \
                self.to_value(random_throw)
            next_state.stopped = (next_state.current_value > 21)
        elif choice == 2:  # swap
            random_swap = random.choice(next_used_deck)
            random_throw = random.choice(next_hand)
            next_hand.remove(random_throw)
            next_hand.append(random_swap)
            next_state = State(next_deck, next_used_deck, next_hand)
            next_state.current_value = self.current_value + \
                self.to_value(random_swap) - self.to_value(random_throw)
            next_state.stopped = (next_state.current_value > 21)
        else:  # stop
            next_state = State(next_deck, next_used_deck, next_hand)
            next_state.current_value = self.current_value + 0
        next_state.current_round_index = self.current_round_index+1
        next_state.cumulative_choices = self.cumulative_choices+[choice]
        return next_state


class MCST(object):
    def __init__(self, id, deck, used_deck, player_size):
        self.id = id
        self.deck = deck
        self.used_deck = used_deck
        self.player_size = player_size
        self.max_computation = MAX_COMPUTATION
        self.hand = []
        self.stopped = False
        self.node_visted = 0

    def get_action(self):
        # each time generate a new node
        self.node_visted = 0
        node = Node()
        state = State(copy.deepcopy(self.deck), copy.deepcopy(
            self.used_deck), copy.deepcopy(self.hand))
        node.state = state
        best_next = self.monte_carlo_tree_search(node)

        return (best_next.state.choice, self.node_visted)

    def monte_carlo_tree_search(self, node):
        computation_budget = self.max_computation
        for i in range(computation_budget):
            # print("iter: {}".format(i))
            expand_node = self.tree_policy(node)
            reward = self.defaut_policy(expand_node)
            self.backup(expand_node, reward)
        best_next_node = self.best_child(node, True)
        return best_next_node

    def best_child(self, node, is_exploration):  # find best child by UCB
        best_score = -sys.maxsize
        best_sub_node = None
        for sub_node in node.children:
            if is_exploration:
                C = 1/math.sqrt(2.0)
            else:
                C = 0.0
            left = sub_node.quality_value/sub_node.visit_times
            right = 2.0*math.log(node.visit_times) / \
                sub_node.visit_times
            score = left+C*math.sqrt(right)
            if score > best_score:
                best_sub_node = sub_node
        return best_sub_node

    def expand(self, node):  # expand an unexpanded node
        tried_sub_node_states = [sub_node.state
                                 for sub_node in node.children]
        new_state = node.state.get_next_state_with_random_choice()
        while new_state in tried_sub_node_states:
            new_state = node.state.get_next_state_with_random_choice()
        sub_node = Node()
        sub_node.state = new_state
        node.add_child(sub_node)
        return sub_node

    def tree_policy(self, node):
        while node.state.is_terminal() == False:
            self.node_visted += 1
            if node.is_all_expand():
                node = self.best_child(node, True)
            else:
                if NN_CONFIG != 0 and node.state.current_round_index > 5:  # only filter 5 steps futher
                    choice = node.state.choice
                    data = []
                    if choice == 1:
                        data += [1, 0, 0]
                    elif choice == 2:
                        data += [0, 1, 0]
                    elif choice == 3:
                        data += [0, 0, 1]
                    else:
                        data += [0, 0, 0]
                    data += node.state.to_card_vector()
                    tensor = tr.FloatTensor(data)
                    predict_value = nn_filter(tensor)
                    if (predict_value > 21):  # if the predict value bust, stop expand
                        node.stopped = True
                    else:
                        sub_node = self.expand(node)
                else:
                    sub_node = self.expand(node)
                return sub_node
        return node

    def defaut_policy(self, node):
        current_state = node.state
        while current_state.is_terminal == False:
            current_state = current_state.get_next_state_with_random_choice()
        final_state_reward = current_state.compute_reward()
        return final_state_reward

    def backup(self, node, reward):
        while node != None:
            node.visit_times += 1
            node.quality_value += reward
            node = node.parent


class Dummy(object):
    def __init__(self, id):
        self.id = id
        self.hand = []
        self.stopped = False

    def get_action(self):
        return (random.choice([1, 2, 3]), -1)
