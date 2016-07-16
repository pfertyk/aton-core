from random import randint, shuffle
import json
from enum import Enum


State = Enum('State', 'Initialized Cartouches')


class Player:
    def __init__(self, notifier=None):
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


class AtonCore:
    def __init__(self, notifiers=[None, None]):
        self.finished = False
        self.players = {
            'red': Player(notifiers[0]),
            'blue': Player(notifiers[1]),
        }
        self.state = State.Initialized

    def get_other_player(self, player):
        if player == self.players['red']:
            return self.players['blue']
        else:
            return self.players['red']

    def start(self):
        for player in self.players.values():
            player.draw_cards()

        self.state = State.Cartouches

    def execute(self, command_json):
        command = json.loads(command_json)

        message = command['message']
        player = self.players[command['player']]
        other_player = self.get_other_player(player)

        if self.state == State.Cartouches:
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
