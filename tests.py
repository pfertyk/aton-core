import unittest
from unittest.mock import MagicMock
import json

from main import AtonCore, Player, State


class PlayerTestCase(unittest.TestCase):
    def test_draw_cards_from_deck(self):
        player = Player()
        player.deck = [1, 2, 3, 4, 4, 3, 2, 1]

        player.draw_cards()

        self.assertEqual(player.hand, [1, 2, 3, 4])
        self.assertEqual(player.deck, [4, 3, 2, 1])

    def test_use_discard_as_deck_if_deck_is_too_small(self):
        player = Player()
        player.deck = [2, 3, 4]
        player.discard = [1, 1, 1, 1, 1]

        player.draw_cards()

        self.assertEqual(player.hand, [2, 3, 4, 1])
        self.assertEqual(player.discard, [])
        self.assertEqual(player.deck, [1, 1, 1, 1])


class AtonCoreTestCase(unittest.TestCase):
    def test_sends_cards_to_users(self):
        notifiers = [MagicMock(), MagicMock()]
        aton = AtonCore(notifiers)
        aton.players['red'].deck = [1, 1, 4, 3]
        aton.players['blue'].deck = [4, 2, 3, 4]

        aton.start()

        notifiers[0].assert_called_with(json.dumps({
            'message': 'cards_drawn',
            'cards': [1, 1, 4, 3]
        }))
        notifiers[1].assert_called_with(json.dumps({
            'message': 'cards_drawn',
            'cards': [4, 2, 3, 4]
        }))

    def test_player_can_exchange_cards_by_default(self):
        aton = AtonCore()

        for player in aton.players.values():
            self.assertTrue(player.can_exchange_cards)

    def test_exchanges_cards(self):
        aton = AtonCore()
        red = aton.players['red']
        red.deck = [1, 3, 2, 2, 4, 1, 3, 1, 2, 2, 4, 4]

        aton.start()
        aton.execute(json.dumps({
            'player': 'red',
            'message': 'exchange_cards',
        }))

        self.assertFalse(red.can_exchange_cards)
        self.assertEqual(red.discard, [1, 3, 2, 2])
        self.assertEqual(red.hand, [4, 1, 3, 1])
        self.assertEqual(red.deck, [2, 2, 4, 4])

    def test_player_can_exchange_cards_only_once(self):
        aton = AtonCore()
        red = aton.players['red']
        red.deck = [1, 2, 3, 4, 4, 3, 1, 2, 1, 1, 1, 1]

        aton.start()
        aton.execute(json.dumps({
            'player': 'red',
            'message': 'exchange_cards',
        }))
        aton.execute(json.dumps({
            'player': 'red',
            'message': 'exchange_cards',
        }))

        self.assertEqual(red.discard, [1, 2, 3, 4])
        self.assertEqual(red.hand, [4, 3, 1, 2])
        self.assertEqual(red.deck, [1, 1, 1, 1])

    def test_notifies_when_opponent_exchanges_cards(self):
        notifier = MagicMock()
        aton = AtonCore([notifier, None])

        aton.start()
        aton.execute(json.dumps({
            'player': 'blue',
            'message': 'exchange_cards',
        }))

        notifier.assert_called_with(json.dumps({
            'message': 'opponent_exchanged_cards',
        }))

    def test_cartouches_are_empty_by_default(self):
        aton = AtonCore()

        for player in aton.players.values():
            self.assertEqual(player.cartouches, [])

    def test_allocates_cards(self):
        aton = AtonCore()
        red = aton.players['red']
        red.deck = [1, 2, 3, 4]

        aton.start()
        aton.execute(json.dumps({
            'player': 'red',
            'message': 'allocate_cards',
            'cards': [4, 2, 3, 1]
        }))

        self.assertEqual(red.hand, [])
        self.assertEqual(red.cartouches, [4, 2, 3, 1])

    def test_validates_allocated_cards(self):
        aton = AtonCore()
        red = aton.players['red']
        red.deck = [1, 2, 3, 4]

        aton.start()
        aton.execute(json.dumps({
            'player': 'red',
            'message': 'allocate_cards',
            'cards': [4, 4, 4, 4]
        }))

        self.assertEqual(red.hand, [1, 2, 3, 4])
        self.assertEqual(red.cartouches, [])

    def test_notifies_when_opponent_allocates_cards(self):
        notifier = MagicMock()
        aton = AtonCore()
        aton.players['blue'].deck = [1, 2, 3, 4]

        aton.start()
        aton.players['red'].notifier = notifier
        aton.execute(json.dumps({
            'player': 'blue',
            'message': 'allocate_cards',
            'cards': [1, 2, 3, 4]
        }))

        notifier.assert_called_with(json.dumps({
            'message': 'opponent_allocated_cards'
        }))

    def test_scores_points_using_cartouche1(self):
        aton = AtonCore()
        red = aton.players['red']
        blue = aton.players['blue']
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
        red = aton.players['red']
        blue = aton.players['blue']
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
        red = aton.players['red']
        blue = aton.players['blue']
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
        red = aton.players['red']
        blue = aton.players['blue']

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
        red = aton.players['red']
        blue = aton.players['blue']

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
            notifier.assert_called_with(json.dumps({
                'message': 'starting_player_selected',
                'player': 'blue',
            }))

    def test_selects_starting_player_using_cartouche1(self):
        notifiers = [MagicMock(), MagicMock()]
        aton = AtonCore(notifiers)
        red = aton.players['red']
        blue = aton.players['blue']

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
            notifier.assert_called_with(json.dumps({
                'message': 'starting_player_selected',
                'player': 'red',
            }))

    def test_selects_starting_player_using_decks(self):
        notifiers = [MagicMock(), MagicMock()]
        aton = AtonCore(notifiers)
        red = aton.players['red']
        blue = aton.players['blue']

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
            notifier.assert_called_with(json.dumps({
                'message': 'starting_player_selected',
                'player': 'red',
            }))

        self.assertEqual(red.deck, [3])
        self.assertEqual(red.discard, [1, 1])

        self.assertEqual(blue.deck, [4])
        self.assertEqual(blue.discard, [1, 2])

    def test_selects_starting_player_using_shuffled_discards(self):
        notifiers = [MagicMock(), MagicMock()]
        aton = AtonCore(notifiers)
        red = aton.players['red']
        blue = aton.players['blue']

        red.deck = [1, 1, 1, 1]
        red.discard = [2, 2]
        blue.deck = [1, 1, 1, 1]
        blue.discard = [1, 1]

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
            notifier.assert_called_with(json.dumps({
                'message': 'starting_player_selected',
                'player': 'blue',
            }))

        self.assertEqual(red.deck, [2])
        self.assertEqual(red.discard, [2])

        self.assertEqual(blue.deck, [1])
        self.assertEqual(blue.discard, [1])

    def test_orders_player_to_remove_opponents_tokens(self):
        notifiers = [MagicMock(), MagicMock()]
        aton = AtonCore(notifiers)
        red = aton.players['red']
        red.cartouches = [1, 4, 3, 4]
        for i in range(4):
            aton.temples[i].tokens[0] = 'blue'
        aton.current_player = 'red'
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

if __name__ == '__main__':
    unittest.main()
