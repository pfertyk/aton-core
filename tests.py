import unittest
from unittest.mock import MagicMock
import json

from main import AtonCore, Player


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


if __name__ == '__main__':
    unittest.main()
