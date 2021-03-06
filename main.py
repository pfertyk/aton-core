from random import randint, shuffle
import json
from enum import Enum


class State(Enum):
    Initialized = 0
    Allocating = 1
    Scoring = 2
    OrderOfPlay = 3
    RemovingTokens = 4


class Player:
    def __init__(self, name=None, notifier=None):
        self.name = name
        self.can_exchange_cards = True
        self.tokens_left = 29
        self.deck = [randint(1, 4) for _ in range(36)]
        self.hand = []
        self.cartouches = []
        self.discard = []
        self.points = 0
        self.notifier = notifier

    def notify(self, message):
        if self.notifier:
            self.notifier(message)

    def draw_cards(self):
        self.discard.extend(self.hand)
        self.hand = []

        while len(self.hand) != 4:
            if self.deck:
                self.hand.append(self.deck[0])
                self.deck = self.deck[1:]
            else:
                self.deck = self.discard
                self.discard = []
                shuffle(self.deck)

        assert len(self.hand) == 4

        message = {}
        message['message'] = 'cards_drawn'
        message['cards'] = self.hand
        self.notify(json.dumps(message))

    def draw_card_and_discard_it(self):
        if not self.deck:
            self.deck = self.discard
            self.discard = []
            shuffle(self.deck)
        card = self.deck[0]
        self.deck = self.deck[1:]
        self.discard.append(card)
        return card

    def __str__(self):
        return self.name


class Temple:
    def __init__(self):
        self.tokens = [''] * 12

    def count_player_tokens(self, player):
        return len([token for token in self.tokens if token == player.name])

    def get_player_tokens(self, player):
        tokens = []
        for i, token in enumerate(self.tokens):
            if token == player.name:
                tokens.append(i)
        return tokens


class AtonCore:
    def __init__(self, notifiers=[None, None]):
        self.finished = False
        self.red = Player('red', notifiers[0])
        self.blue = Player('blue', notifiers[1])
        self.temples = []
        for _ in range(4):
            self.temples.append(Temple())
        self.current_player = None

        self.state = State.Allocating

    def get_other_player(self, player):
        if player is self.red:
            return self.blue
        else:
            return self.red

    def get_player_by_name(self, player_name):
        if player_name == 'red':
            return self.red
        else:
            return self.blue

    def start(self):
        self.switch_to_state(self.state)

    def switch_to_state(self, state):
        self.state = state
        if state == State.Allocating:
            for player in [self.red, self.blue]:
                player.draw_cards()
        elif state == State.Scoring:
            self.score_cartouche1()
        elif state == State.OrderOfPlay:
            self.determine_order_of_play()
        elif state == State.RemovingTokens:
            cartouches = self.current_player.cartouches
            number_of_tokens = cartouches[1] - 2
            max_available_temple = cartouches[2]
            if number_of_tokens != 0:
                if number_of_tokens > 0:
                    if self.current_player is self.red:
                        token_owner = self.blue
                    else:
                        token_owner = self.red
                else:
                    number_of_tokens = -number_of_tokens
                    token_owner = self.current_player
                tokens = [[], [], [], []]
                token_count = 0
                for temple_index in range(max_available_temple):
                    temple = self.temples[temple_index]
                    token_count += temple.count_player_tokens(token_owner)
                    tokens[temple_index] = temple.get_player_tokens(
                        token_owner)
                if token_count > number_of_tokens:
                    self.notify_players(json.dumps({
                        'message': 'remove_tokens',
                        'player': str(self.current_player),
                        'token_owner': str(token_owner),
                        'number_of_tokens': number_of_tokens,
                        'max_available_temple': max_available_temple,
                    }))
                else:
                    for temple_index, token_indices in enumerate(tokens):
                        for token_index in token_indices:
                            self.temples[temple_index].tokens[token_index] = ''
                    self.notify_players(json.dumps({
                        'message': 'tokens_removed',
                        'removing_player': str(self.current_player),
                        'token_owner': str(token_owner),
                        'removed_tokens': tokens,
                    }))

    def notify_players(self, message):
        for player in [self.red, self.blue]:
            player.notify(message)

    def score_cartouche1(self):
        red = self.red
        blue = self.blue
        if red.cartouches[0] != blue.cartouches[0]:
            cartouche_difference = abs(red.cartouches[0] - blue.cartouches[0])
            if red.cartouches[0] > blue.cartouches[0]:
                scoring_player = red
            else:
                scoring_player = blue
            points = cartouche_difference * 2
            scoring_player.points += points
            self.notify_players(json.dumps({
                'message': 'points_scored',
                'player': str(scoring_player),
                'points': points,
            }))

        self.switch_to_state(State.OrderOfPlay)

    def determine_order_of_play(self):
        red = self.red
        blue = self.blue
        red_cards = []
        blue_cards = []
        if red.cartouches[1] < blue.cartouches[1]:
            starting_player = red
        elif blue.cartouches[1] < red.cartouches[1]:
            starting_player = blue
        else:
            if red.cartouches[0] < blue.cartouches[0]:
                starting_player = red
            elif blue.cartouches[0] < red.cartouches[0]:
                starting_player = blue
            else:
                while True:
                    red_card = red.draw_card_and_discard_it()
                    blue_card = blue.draw_card_and_discard_it()
                    red_cards.append(red_card)
                    blue_cards.append(blue_card)
                    if red_card < blue_card:
                        starting_player = red
                        break
                    elif blue_card < red_card:
                        starting_player = blue
                        break

        self.notify_players(json.dumps({
            'message': 'starting_player_selected',
            'player': str(starting_player),
            'cards_used': {
                'red': red_cards,
                'blue': blue_cards,
            }
        }))

        self.current_player = starting_player
        self.switch_to_state(State.RemovingTokens)

    def execute(self, command_json):
        command = json.loads(command_json)

        message = command['message']
        player = self.get_player_by_name(command['player'])
        other_player = self.get_other_player(player)

        if self.state == State.Allocating:
            if message == 'exchange_cards':
                if player.can_exchange_cards:
                    player.can_exchange_cards = False
                    other_player.notify(json.dumps({
                        'message': 'opponent_exchanged_cards'}))
                    player.draw_cards()
            if message == 'allocate_cards':
                cards = command['cards']
                if sorted(player.hand) == sorted(cards):
                    if not player.cartouches:
                        player.cartouches = cards
                        player.hand = []
                        other_player.notify(json.dumps({
                            'message': 'opponent_allocated_cards'
                        }))

                        if other_player.cartouches:
                            self.switch_to_state(State.Scoring)
