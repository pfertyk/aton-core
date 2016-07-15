import unittest
from unittest.mock import MagicMock

from main import AtonCore


class AtonCoreTestCase(unittest.TestCase):
    def test_sends_cards_to_users(self):
        notifiers = [MagicMock(), MagicMock()]
        AtonCore(notifiers)

        for notifier in notifiers:
            notifier.assert_called()


if __name__ == '__main__':
    unittest.main()
