import json
from unittest import TestCase
from unittest.mock import Mock

from main import AtonCore


class TestScoringCartouche(TestCase):
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
        red.notifier = Mock()
        blue.notifier = Mock()
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
