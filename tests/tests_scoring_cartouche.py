import json
from unittest import TestCase
from unittest.mock import Mock

from main import AtonCore, State


class TestScoringCartouche(TestCase):
    def setUp(self):
        self.aton = AtonCore([Mock(), Mock()])
        self.aton.state = State.Scoring

    def test_scores_points_using_cartouche1(self):
        self.aton.red.cartouches = [1, 2, 3, 4]
        self.aton.blue.cartouches = [4, 4, 4, 4]

        self.aton.start()

        self.assertEqual(self.aton.red.points, 0)
        self.assertEqual(self.aton.blue.points, 6)

    def test_no_scoring_if_both_cartouches1_are_equal(self):
        self.aton.red.cartouches = [1, 2, 1, 1]
        self.aton.blue.cartouches = [1, 1, 1, 1]

        self.aton.start()

        self.assertEqual(self.aton.red.points, 0)
        self.assertEqual(self.aton.blue.points, 0)

    def test_notifies_about_scoring_point_from_cartouche1(self):
        self.aton.red.cartouches = [3, 1, 1, 1]
        self.aton.blue.cartouches = [1, 1, 1, 1]

        self.aton.start()

        self.aton.red.notifier.assert_any_call(json.dumps({
            'message': 'points_scored',
            'player': 'red',
            'points': 4,
        }))
        self.aton.blue.notifier.assert_any_call(json.dumps({
            'message': 'points_scored',
            'player': 'red',
            'points': 4,
        }))

    def test_no_notification_if_cartouches1_are_equal(self):
        def notifier(message):
            self.assertNotIn('points_scored', message)
        self.aton.red.notifier = notifier
        self.aton.blue.notifier = notifier

        self.aton.red.cartouches = [1, 2, 1, 1]
        self.aton.blue.cartouches = [1, 1, 1, 1]

        self.aton.start()
