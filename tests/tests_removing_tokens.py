import json
from unittest import TestCase
from unittest.mock import Mock

from main import AtonCore, State


class TestRemovingTokens(TestCase):
    def test_orders_player_to_remove_opponents_tokens(self):
        notifiers = [Mock(), Mock()]
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
        notifiers = [Mock(), Mock()]
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
