import unittest
from unittest.mock import MagicMock, Mock, patch
import json

from main import AtonCore, State


class AtonCoreTestCase(unittest.TestCase):
    def test_scores_points_using_cartouche1(self):
        aton = AtonCore()
        red = aton.red
        blue = aton.blue
        red.deck = [1, 2, 3, 4]
        blue.deck = [4, 4, 4, 4]

        aton.start()
        aton.execute(json.dumps({
            'player': 'blue',
            'message': 'allocate_cards',
            'cards': [4, 4, 4, 4]
        }))
        aton.execute(json.dumps({
            'player': 'red',
            'message': 'allocate_cards',
            'cards': [1, 2, 3, 4]
        }))

        self.assertEqual(red.points, 0)
        self.assertEqual(blue.points, 6)

    def test_no_scoring_if_both_cartouches1_are_equal(self):
        aton = AtonCore()
        red = aton.red
        blue = aton.blue
        red.deck = [1, 2, 1, 1]
        blue.deck = [1, 1, 1, 1]

        aton.start()
        aton.execute(json.dumps({
            'player': 'blue',
            'message': 'allocate_cards',
            'cards': [1, 1, 1, 1]
        }))
        aton.execute(json.dumps({
            'player': 'red',
            'message': 'allocate_cards',
            'cards': [1, 2, 1, 1]
        }))

        self.assertEqual(red.points, 0)
        self.assertEqual(blue.points, 0)

    def test_notifies_about_scoring_point_from_cartouche1(self):
        aton = AtonCore()
        red = aton.red
        blue = aton.blue
        red.deck = [3, 1, 1, 1]
        blue.deck = [1, 1, 1, 1]

        aton.start()
        red.notifier = MagicMock()
        blue.notifier = MagicMock()
        aton.execute(json.dumps({
            'player': 'blue',
            'message': 'allocate_cards',
            'cards': [1, 1, 1, 1]
        }))
        aton.execute(json.dumps({
            'player': 'red',
            'message': 'allocate_cards',
            'cards': [3, 1, 1, 1]
        }))

        red.notifier.assert_any_call(json.dumps({
            'message': 'points_scored',
            'player': 'red',
            'points': 4,
        }))
        blue.notifier.assert_any_call(json.dumps({
            'message': 'points_scored',
            'player': 'red',
            'points': 4,
        }))

    def test_no_notification_if_cartouches1_are_equal(self):
        aton = AtonCore()
        red = aton.red
        blue = aton.blue

        def notifier(message):
            self.assertNotIn('points_scored', message)
        red.notifier = notifier
        blue.notifier = notifier

        red.deck = [1, 2, 1, 1]
        blue.deck = [1, 1, 1, 1]

        aton.start()
        aton.execute(json.dumps({
            'player': 'blue',
            'message': 'allocate_cards',
            'cards': [1, 1, 1, 1]
        }))
        aton.execute(json.dumps({
            'player': 'red',
            'message': 'allocate_cards',
            'cards': [1, 2, 1, 1]
        }))

    def test_selects_starting_player_using_cartouche2(self):
        notifiers = [MagicMock(), MagicMock()]
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
        notifiers = [MagicMock(), MagicMock()]
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
        notifiers = [MagicMock(), MagicMock()]
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
        notifiers = [MagicMock(), MagicMock()]
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

    def test_orders_player_to_remove_opponents_tokens(self):
        notifiers = [MagicMock(), MagicMock()]
        aton = AtonCore(notifiers)
        red = aton.red
        red.cartouches = [1, 4, 3, 4]
        for i in range(4):
            aton.temples[i].tokens[0] = 'blue'
        aton.current_player = aton.red
        aton.state = State.RemovingTokens

        aton.start()

        for notifier in notifiers:
            notifier.assert_called_with(json.dumps({
                'message': 'remove_tokens',
                'player': 'red',
                'token_owner': 'blue',
                'number_of_tokens': 2,
                'max_available_temple': 3,
            }))

    def test_orders_player_to_remove_own_tokens(self):
        notifiers = [MagicMock(), MagicMock()]
        aton = AtonCore(notifiers)
        red = aton.red
        red.cartouches = [1, 1, 3, 4]
        for i in range(4):
            aton.temples[i].tokens[0] = 'red'
        aton.current_player = aton.red
        aton.state = State.RemovingTokens

        aton.start()

        for notifier in notifiers:
            notifier.assert_called_with(json.dumps({
                'message': 'remove_tokens',
                'player': 'red',
                'token_owner': 'red',
                'number_of_tokens': 1,
                'max_available_temple': 3,
            }))

    def test_no_notification_when_no_tokens_should_be_removed(self):
        def notifier(message):
            self.assertNotIn('remove_tokens', message)
        notifiers = [notifier, notifier]
        aton = AtonCore(notifiers)
        red = aton.red
        red.cartouches = [1, 2, 3, 4]
        for i in range(4):
            aton.temples[i].tokens[0] = 'red'
        aton.current_player = aton.red
        aton.state = State.RemovingTokens

        aton.start()

    def test_no_notification_when_no_opponents_tokens_available(self):
        def notifier(message):
            self.assertNotIn('remove_tokens', message)
        notifiers = [notifier, notifier]
        aton = AtonCore(notifiers)
        red = aton.red
        red.cartouches = [1, 4, 3, 4]
        aton.current_player = aton.red
        aton.state = State.RemovingTokens

        aton.start()

    def test_no_notification_when_no_own_tokens_available(self):
        def notifier(message):
            self.assertNotIn('remove_tokens', message)
        notifiers = [notifier, notifier]
        aton = AtonCore(notifiers)
        red = aton.red
        red.cartouches = [1, 1, 3, 4]
        aton.current_player = aton.red
        aton.state = State.RemovingTokens

        aton.start()

    def test_no_notification_when_opponents_tokens_in_unavailable_temple(self):
        def notifier(message):
            self.assertNotIn('remove_tokens', message)
        notifiers = [notifier, notifier]
        aton = AtonCore(notifiers)
        red = aton.red
        red.cartouches = [1, 4, 3, 4]
        for i in range(4):
            aton.temples[3].tokens[i] = 'blue'
        aton.current_player = aton.red
        aton.state = State.RemovingTokens

        aton.start()

    def test_no_notification_when_own_tokens_in_unavailable_temple(self):
        def notifier(message):
            self.assertNotIn('remove_tokens', message)
        notifiers = [notifier, notifier]
        aton = AtonCore(notifiers)
        red = aton.red
        red.cartouches = [1, 1, 3, 4]
        for i in range(4):
            aton.temples[3].tokens[i] = 'red'
        aton.current_player = aton.red
        aton.state = State.RemovingTokens

        aton.start()

    def test_automatically_remove_opponents_tokens_when_possible(self):
        notifiers = [Mock(), Mock()]
        aton = AtonCore(notifiers)
        red = aton.red
        red.cartouches = [1, 4, 4, 4]
        for i in range(2):
            aton.temples[i].tokens[i] = 'blue'
        aton.current_player = aton.red
        aton.state = State.RemovingTokens

        aton.start()

        for notifier in notifiers:
            notifier.assert_called_with(json.dumps({
                'message': 'tokens_removed',
                'removing_player': 'red',
                'token_owner': 'blue',
                'removed_tokens': [[0], [1], [], []]
            }))

        for temple_index, temple in enumerate(aton.temples):
            for token in temple.tokens:
                self.assertNotEqual(token, 'blue', 'Temple {}: {}'.format(
                    temple_index, temple.tokens))

    def test_automatically_remove_own_tokens_when_possible(self):
        notifiers = [Mock(), Mock()]
        aton = AtonCore(notifiers)
        red = aton.red
        red.cartouches = [1, 1, 1, 4]
        for i in range(4):
            aton.temples[i].tokens[5] = 'red'
        aton.current_player = aton.red
        aton.state = State.RemovingTokens

        aton.start()

        for notifier in notifiers:
            notifier.assert_called_with(json.dumps({
                'message': 'tokens_removed',
                'removing_player': 'red',
                'token_owner': 'red',
                'removed_tokens': [[5], [], [], []]
            }))

        temple = aton.temples[0]
        for token in temple.tokens:
            self.assertNotEqual(token, 'red', 'Temple {}: {}'.format(
                0, temple.tokens))

if __name__ == '__main__':
    unittest.main()
