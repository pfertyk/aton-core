import json
from unittest import TestCase
from unittest.mock import Mock, patch

from main import AtonCore, State


class TestOrderOfPlay(TestCase):
    def test_selects_starting_player_using_cartouche2(self):
        notifiers = [Mock(), Mock()]
        aton = AtonCore(notifiers)
        red = aton.red
        blue = aton.blue

        red.deck = [1, 2, 1, 1]
        blue.deck = [1, 1, 1, 1]

        aton.start()
        aton.execute(json.dumps({
            'player': 'red',
            'message': 'allocate_cards',
            'cards': [1, 2, 1, 1]
        }))
        aton.execute(json.dumps({
            'player': 'blue',
            'message': 'allocate_cards',
            'cards': [1, 1, 1, 1]
        }))

        for notifier in notifiers:
            notifier.assert_any_call(json.dumps({
                'message': 'starting_player_selected',
                'player': 'blue',
                'cards_used': {
                    'red': [],
                    'blue': [],
                }
            }))

    def test_selects_starting_player_using_cartouche1(self):
        notifiers = [Mock(), Mock()]
        aton = AtonCore(notifiers)
        red = aton.red
        blue = aton.blue

        red.deck = [1, 1, 1, 1]
        blue.deck = [2, 1, 1, 1]

        aton.start()
        aton.execute(json.dumps({
            'player': 'red',
            'message': 'allocate_cards',
            'cards': [1, 1, 1, 1]
        }))
        aton.execute(json.dumps({
            'player': 'blue',
            'message': 'allocate_cards',
            'cards': [2, 1, 1, 1]
        }))

        for notifier in notifiers:
            notifier.assert_any_call(json.dumps({
                'message': 'starting_player_selected',
                'player': 'red',
                'cards_used': {
                    'red': [],
                    'blue': [],
                }
            }))

    def test_selects_starting_player_using_decks(self):
        notifiers = [Mock(), Mock()]
        aton = AtonCore(notifiers)
        red = aton.red
        blue = aton.blue

        red.deck = [1, 1, 1, 1, 1, 1, 3]
        blue.deck = [1, 1, 1, 1, 1, 2, 4]

        aton.start()
        aton.execute(json.dumps({
            'player': 'red',
            'message': 'allocate_cards',
            'cards': [1, 1, 1, 1]
        }))
        aton.execute(json.dumps({
            'player': 'blue',
            'message': 'allocate_cards',
            'cards': [1, 1, 1, 1]
        }))

        for notifier in notifiers:
            notifier.assert_any_call(json.dumps({
                'message': 'starting_player_selected',
                'player': 'red',
                'cards_used': {
                    'red': [1, 1],
                    'blue': [1, 2],
                }
            }))

        self.assertEqual(red.deck, [3])
        self.assertEqual(red.discard, [1, 1])

        self.assertEqual(blue.deck, [4])
        self.assertEqual(blue.discard, [1, 2])

    @patch('main.shuffle')
    def test_selects_starting_player_using_shuffled_discards(self, mock):
        notifiers = [Mock(), Mock()]
        aton = AtonCore(notifiers)
        red = aton.red
        blue = aton.blue

        red.deck = [2]
        red.cartouches = [1, 1, 1, 1]
        red.discard = [1, 3]
        blue.deck = [2]
        blue.cartouches = [1, 1, 1, 1]
        blue.discard = [1, 2]

        aton.state = State.OrderOfPlay

        aton.start()

        for notifier in notifiers:
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
