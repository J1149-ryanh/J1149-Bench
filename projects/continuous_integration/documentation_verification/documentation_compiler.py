import abc
import collections
from functools import total_ordering
from enum import Enum, auto, unique
from overrides import overrides
import os

# Unix style success; used for syntactic sugar at the moment.
SUCCESS = 0

# Stuff to ignore
# TODO enable this to be modified by the user, a la .gitignore
IGNORE = ['.pytest_cache', 'README.md', 'CODE_OF_CONDUCT.md',
          '_configuration']


class DocCompilerError(Exception):
    """"Base exception for documentation compiler"""
    pass


class IncompleteCmdSeq(DocCompilerError):
    """There was not a complete sequence of commands"""
    pass


class TransitionStateNotFound(DocCompilerError):
    """No transition state was found that matched the conditions in the adjacent
        transition states"""
    def __init__(self, msg, errors=[]):
        super(TransitionStateNotFound, self).__init__(msg, errors)


def should_ignore(root, fname):
    path = os.path.join(root, fname)
    for ig in IGNORE:
        if ig in path:
            return True
    return False


def find_documetation(dirpath, doc_ext):
    for root, _, fnames in os.walk(dirpath):
        for fname in fnames:
            if fname.endswith(doc_ext) and not should_ignore(root, fname):
                yield os.path.join(root, fname)


def is_valid_first_char(transition_state, char):
    if transition_state.is_term_pattern:
        return True
    return transition_state.pattern.startswith(char)


class IsValidExitStatus:

    def __init__(self, requisite_status):
        self.requisite_status = requisite_status

    def __call__(self, status):
        return self.requisite_status == status



@unique
@total_ordering
class TokenIdentifiers(Enum):
    ENVIRONMENT = 0
    IN_CMD = auto()
    EXPECTED_OUT = auto()

    def __lt__(self, other):
        if self.__class__ == other.__class__:
            return self.value < other.value


Token = collections.namedtuple('Token', 'seq_idx value')


class TokenSequence:
    '''
    TODO cleanup; the addition of a new command sequence should happen in one
    place and thus make it unnecessary to check for a default environment or
    if the command set is filled.
    '''

    def __init__(self, default_environment=None, fname=None):
        self.default_environment = default_environment
        self.init()

    def __iter__(self):
        for cmd_set in self.sequence_storage:
            yield cmd_set

    def __str__(self):
        string_sequence = ''
        for cmd_set in self.sequence_storage:
            for token in cmd_set:
                subsequence = '{0}:{1}\n'.format(token.seq_idx, token.value)
                string_sequence += subsequence
        return string_sequence

    def init(self):
        self.sequence_storage = []
        # first command set
        first_cmd_set = []
        if self.default_environment is not None:
            token = Token(seq_idx=TokenIdentifiers.ENVIRONMENT,
                          value=self.default_environment)
            first_cmd_set.append(token)
        self.sequence_storage.append(first_cmd_set)

    def is_complete(self):
        last_cmd_set = self.sequence_storage[-1]
        last_el = last_cmd_set[-1]
        return last_el.seq_idx == TokenIdentifiers.EXPECTED_OUT

    def append(self, token):
        self.verify_sequence(token)
        last_cmd_set = self.sequence_storage[-1]
        # If we've filled the command set
        if len(last_cmd_set) == len(TokenIdentifiers):
            self.sequence_storage.append([])
            last_cmd_set = self.sequence_storage[-1]
        last_cmd_set.append(token)

    def verify_sequence(self, token):
        last_cmd_set = self.sequence_storage[-1]

        filled_cmd_set = len(last_cmd_set) == len(TokenIdentifiers)
        if filled_cmd_set and token.seq_idx == TokenIdentifiers.ENVIRONMENT:
            return SUCCESS

        has_def_envir = self.default_environment is not None
        is_in_cmd_tkn = token.seq_idx == TokenIdentifiers.IN_CMD
        if filled_cmd_set and has_def_envir and is_in_cmd_tkn:
            return SUCCESS

        is_environ = token.seq_idx == TokenIdentifiers.ENVIRONMENT
        if len(last_cmd_set) == 0 and is_environ:
            return SUCCESS

        last_token = last_cmd_set[-1]
        if token.seq_idx <= last_token.seq_idx:
            err = "{0} can't follow {1} in sequence.".format(token.seq_idx,
                                                             last_token.seq_idx)
            raise ValueError(err)

        return SUCCESS


class Lexer:

    def __init__(self, root_state, default_environment=None):
        self.state = root_state
        self.default_environment = default_environment
        self.token_sequence = TokenSequence(self.default_environment)
        self.filepath = None

    def lex(self, filepath):
        self.filepath = filepath
        with open(filepath, 'r') as fyle:
            for line in fyle:
                for char in line:
                    self.next_char(char)

    def next_char(self, char):
        self.state.next_char(char)

    def set_state(self, transition_state):
        self.state = transition_state

    def pop_tok_seq(self):
        if not self.token_sequence.is_complete():
            raise IncompleteCmdSeq("Token Sequence did not"
                                   " complete %s for file %s"
                                   % (self.token_sequence, self.filepath))
        tmp = self.token_sequence
        self.token_sequence = TokenSequence(self.default_environment)
        return tmp


class LexerState(abc.ABC):

    def __init__(self, lexer, pattern, transition_states=[],
                 is_term_pattern=False):
        '''

        Args:
            lexer (Lexer): The lexer from which this state is originating from.

            pattern (str): The token which is the basis of this state

            transition_states (list of LexerStates): Valid states that this state
                can transition to AFTER a success token match or during the
                failure of a token matching sequence. Specifically, this list
                is searched one-by-one for a state that contains a token which
                matches the first character found during a failure to match or
                after a token was successfully matched.

                For example:
                        TODO Fill in example.
            is_term_pattern (bool): Is the pattern one that indicates when the
                state was completed?




        '''
        self.lexer = lexer
        self.pattern = pattern
        self.is_term_pattern = is_term_pattern
        self.transition_map = transition_states
        self.reset()

    def __str__(self):
        return self.__class__.__name__

    def reset(self):
        self.token_idx = 0
        self.accum = []
        self.is_success = False

    def next_char(self, char):

        if self.is_success or len(self.pattern) < 1:
            self.change_state(char, self.is_success)
        # If we've matched the whole token:
        #   1. Indicate to the lexer that this state completed successfully.
        #   2. Change the state based on the dangling char we just received.
        elif (not self.is_term_pattern and
              self.token_idx == len(self.pattern)-1) \
                or (self.is_term_pattern and char == self.pattern):
            self.on_state_success()
            self.accum.append(char)
            self.is_success = True
        elif self.is_term_pattern and char != self.pattern:
            self.accum.append(char)
        # Check if we are still matching the expected token sequence.
        elif not self.is_term_pattern and char == self.pattern[self.token_idx]:
            self.accum.append(char)
            self.token_idx += 1
        # We are no longer matching the token sequence; change to the appropriate
        # state.
        else:
            self.change_state(char, self.is_success)

    def change_state(self, char, status):
        self.reset()
        if len(self.transition_map) < 1:
            raise ValueError('There must be transition states available to this'
                             ' state {0}.'.format(self))
        # Notice that the transition_states are dependent on order!
        for transition_state, condition_met in self.transition_map.items():
            if condition_met(transition_state, char, status):
                self.lexer.set_state(transition_state)
                self.lexer.next_char(char)
                return SUCCESS
        else:
            msg = "{0} can't find a state transition to with the following" \
                  " available states {1}.".format(self, self.transition_map)
            raise TransitionStateNotFound(msg)

    def set_transition_states(self, transition_states):
        self.transition_map = transition_states

    @abc.abstractmethod
    def on_state_success(self):
        pass


# we want to preserve whatever code is written in change_state from LexerState so
# as to prevent bugs by not copying logic and to not duplicate code.
def monkey_patch_change_state(cls):

    cls._change_state = cls.change_state

    def change_state(self, char, status):
        # We don't care if it can't find a state.
        try:
            return cls._change_state(self, char, status)
        except TransitionStateNotFound:
            pass
        return SUCCESS

    cls.change_state = change_state
    return cls

@monkey_patch_change_state
class NullState(LexerState):

    def __init__(self, lexer, transition_states=[]):
        # Note, '' is the empty string and matches just about every string
        # matching function.
        pattern = ''
        super(NullState, self).__init__(lexer, pattern, transition_states,
                                        is_term_pattern=True)

    @overrides
    def on_state_success(self):
        pass


class InputHeaderState(LexerState):

    @overrides
    def on_state_success(self):
        # We only care that this state successfully completes so that we can
        # extract the input command.
        pass


class InputCmdState(LexerState):

    @overrides
    def on_state_success(self):
        seq_idx = TokenIdentifiers.IN_CMD
        value = ''.join(self.accum)
        token = Token(seq_idx, value)
        self.lexer.token_sequence.append(token)


class OutputHeaderState(LexerState):

    @overrides
    def on_state_success(self):
        # We only care that this state successfully completes so that we can
        # extract the input command.
        pass


class ExpectedOutputState(LexerState):

    @overrides
    def on_state_success(self):
        seq_idx = TokenIdentifiers.EXPECTED_OUT
        value = ''.join(self.accum)
        token = Token(seq_idx, value)
        self.lexer.token_sequence.append(token)


if __name__ == '__main__':
    pass