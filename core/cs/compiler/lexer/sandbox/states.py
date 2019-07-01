
class State:

    def __init__(self, token_values):
        self.token_values = token_values


class IdentifierState(State):
    pass


class KeywordState:
    pass


class SeparatorState:
    pass


class OperatorState:
    pass


class LiteralState:
    pass


class CommentState:
    pass

