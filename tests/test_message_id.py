from pylint import message
from pylint.testutils import CheckerTestCase
from pylint.testutils import Message
from pylint.testutils import UnittestLinter
from pylint.testutils import _tokenize_str

from pylint_message_id import NumericalMessageIdChecker


class TestNumericalMessageId(CheckerTestCase):
    CHECKER_CLASS = NumericalMessageIdChecker

    def setup_method(self):
        self.linter = UnittestLinter()
        self.linter.msgs_store = message.MessageDefinitionStore()
        self.checker = self.CHECKER_CLASS(self.linter)  # pylint: disable=not-callable
        for key, value in self.CONFIG.items():
            setattr(self.checker.config, key, value)
        self.checker.open()
        # Sanity check that the mapping is empty as expected
        # since our check was not registered
        assert self.checker.msg_id_to_symbol == {}

        # Add dummy mapping
        self.checker.msg_id_to_symbol["W1234"] = "some-nice-symbol"
        self.checker.msg_id_to_symbol["E4321"] = "that-other-symbol"

    def test_check_numerical_id(self):
        with self.assertAddsMessages(
            Message(
                "numerical-message-id", line=1, args=("W1234", "some-nice-symbol",),
            )
        ):
            self.checker.process_tokens(_tokenize_str("# pylint: disable=W1234"))

    def test_no_numerical_id(self):
        with self.assertNoMessages():
            self.checker.process_tokens(
                _tokenize_str("# pylint: disable=some-nice-symbol")
            )

    def test_mixed_ids(self):
        with self.assertAddsMessages(
            Message(
                "numerical-message-id", line=1, args=("E4321", "that-other-symbol",),
            )
        ):
            self.checker.process_tokens(
                _tokenize_str("# pylint: disable=some-nice-symbol,foobar,E4321")
            )
