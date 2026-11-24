# --------------------------------------------------------------------------------
# The usage error: a command was called with arguments it does not take
# --------------------------------------------------------------------------------
# The command runner prints one "Usage:" line and exits 2.
# --------------------------------------------------------------------------------


class UsageError(Exception):
    def __init__(self, args_text: str) -> None:
        super().__init__(args_text)
        self.args_text = args_text
