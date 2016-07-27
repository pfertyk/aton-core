import json
from unittest import TestCase
from unittest.mock import Mock, patch

from main import AtonCore, State


class TestOrderOfPlay(TestCase):
    def setUp(self):
        self.notifiers = [Mock(), Mock()]
        self.aton = AtonCore(self.notifiers)
        self.aton.state = State.OrderOfPlay

    def test_selects_starting_player_using_cartouche2(self):
        self.aton.red.cartouches = [1, 2, 1, 1]
        self.aton.blue.cartouches = [1, 1, 1, 1]

        self.aton.start()

        for notifier in self.notifiers:
            notifier.assert_any_call(json.dumps({
                'message': 'starting_player_selected',
                'player': 'blue',
                'cards_used': {
                    'red': [],
                    'blue': [],
                }
            }))

    def test_selects_starting_player_using_cartouche1(self):
        self.aton.red.cartouches = [1, 1, 1, 1]
        self.aton.blue.cartouches = [2, 1, 1, 1]

        self.aton.start()

        for notifier in self.notifiers:
            notifier.assert_any_call(json.dumps({
                'message': 'starting_player_selected',
                'player': 'red',
                'cards_used': {
                    'red': [],
                    'blue': [],
                }
            }))

    def test_selects_starting_player_using_decks(self):
        self.aton.red.cartouches = [1, 1, 1, 1]
        self.aton.red.deck = [1, 1, 3]
        self.aton.blue.cartouches = [1, 1, 1, 1]
        self.aton.blue.deck = [1, 2, 4]

        self.aton.start()

        for notifier in self.notifiers:
            notifier.assert_any_call(json.dumps({
                'message': 'starting_player_selected',
                'player': 'red',
                'cards_used': {
                    'red': [1, 1],
                    'blue': [1, 2],
                }
            }))

        self.assertEqual(self.aton.red.deck, [3])
        self.assertEqual(self.aton.red.discard, [1, 1])

        self.assertEqual(self.aton.blue.deck, [4])
        self.assertEqual(self.aton.blue.discard, [1, 2])

    @patch('main.shuffle')
    def test_selects_starting_player_using_shuffled_discards(self, mock):
        red = self.aton.red
        blue = self.aton.blue

        red.deck = [2]
        red.cartouches = [1, 1, 1, 1]
        red.discard = [1, 3]
        blue.deck = [2]
        blue.cartouches = [1, 1, 1, 1]
        blue.discard = [1, 2]

        self.aton.start()

        for notifier in self.notifiers:
            notifier.assert_any_call(json.dumps({
                'message': 'starting_player_selected',
                'player': 'blue',
                'cards_used': {
                    'red': [2, 1, 3],
                    'blue': [2, 1, 2],
                }
            }))

        self.assertEqual(red.deck, [2])
        self.assertEqual(red.discard, [1, 3])

        self.assertEqual(blue.deck, [2])
        self.assertEqual(blue.discard, [1, 2])
