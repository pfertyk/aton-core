import unittest
from unittest.mock import MagicMock

from main import AtonCore, Player


class PlayerTestCase(unittest.TestCase):
    def test_draw_cards(self):
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
        AtonCore(notifiers)

        for notifier in notifiers:
            notifier.assert_called()


if __name__ == '__main__':
    unittest.main()
