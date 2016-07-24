import json
from unittest import TestCase
from unittest.mock import Mock

from main import AtonCore


class AtonCoreTestCase(TestCase):
    def test_cartouches_are_empty_by_default(self):
        aton = AtonCore()

        self.assertEqual(aton.red.cartouches, [])
        self.assertEqual(aton.blue.cartouches, [])

    def test_allocates_cards(self):
        aton = AtonCore()
        red = aton.red
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
        red = aton.red
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
        notifier = Mock()
        aton = AtonCore()
        aton.blue.deck = [1, 2, 3, 4]

        aton.start()
        aton.red.notifier = notifier
        aton.execute(json.dumps({
            'player': 'blue',
            'message': 'allocate_cards',
            'cards': [1, 2, 3, 4]
        }))

        notifier.assert_called_with(json.dumps({
            'message': 'opponent_allocated_cards'
        }))
