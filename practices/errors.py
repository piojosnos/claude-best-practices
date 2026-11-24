# --------------------------------------------------------------------------------
# The errors every practices module can raise
# --------------------------------------------------------------------------------
# A command turns them into a message and an exit code (see practices.cli).
# --------------------------------------------------------------------------------


class PracticesError(Exception):
    pass


# --------------------------------------------------------------------------------

class UsageError(Exception):
    def __init__(self, args_text: str) -> None:
        super().__init__(args_text)
        self.args_text = args_text
