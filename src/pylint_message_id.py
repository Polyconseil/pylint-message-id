import re
import tokenize

from pylint.checkers import BaseTokenChecker
from pylint.interfaces import ITokenChecker


KEYWORDS = ("disable-msg", "enable-msg", "disable", "enable")
MESSAGE_NUMBER = re.compile(r"[CREIWF]{1}\d*")
PRAGMA_REGEX = re.compile(r"#.*?\bpylint:\s*([^;#\n]+)")


class NumericalMessageIdChecker(BaseTokenChecker):
    __implements__ = ITokenChecker

    name = "numerical-message-id"
    priority = -1
    msgs = {
        "C9001": (
            "Numerical message identifier used: %s - use %s instead",
            "numerical-message-id",
            "Only textual message symbols should be used",
        ),
    }
    options = ()

    def process_tokens(self, tokens):

        # Process tokens and look for comments.
        for (tok_type, token, (start_row, _), _, _) in tokens:
            if tok_type == tokenize.COMMENT:
                if start_row == 1 and token.startswith("#!/"):
                    # Skip shebang lines
                    continue
                match = PRAGMA_REGEX.match(token)
                if match:
                    self._check_pragma(match.group(1), start_row)

    def open(self):
        self.msg_id_to_symbol = {
            message.msgid: message.symbol for message in self.linter.msgs_store.messages
        }

    def _check_pragma(self, pragma, start_row):
        for keyword in KEYWORDS:
            if pragma.startswith(keyword):
                pragma = pragma[len(keyword) :].strip()
                break
        else:
            # No keyword matched
            return
        if not pragma or pragma[0] != "=":
            # Ignore, bad-option-value should catch it
            return
        message_ids = [msg_id.strip() for msg_id in pragma[1:].split(",")]
        for message_id in message_ids:
            if MESSAGE_NUMBER.match(message_id):
                if message_id not in self.msg_id_to_symbol:
                    # Ignore, bad-option-value should catch it
                    continue
                msg_symbol = self.msg_id_to_symbol[message_id]
                self.add_message(
                    "numerical-message-id", start_row, args=(message_id, msg_symbol)
                )


def register(linter):
    linter.register_checker(NumericalMessageIdChecker(linter))
