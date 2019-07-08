from projects.continuous_integration.documentation_verification import documentation_compiler as dc

import os
import sys

if sys.platform.startswith('linux'):
    DEFAULT_ENVIRONMENT = "paicoind -regtest"
elif sys.platform.startswith('win'):
    DEFAULT_ENVIRONMENT = 'start /B paicoind -regtest &'
else:
    raise SystemError('%s is not a supported operating system.'%sys.platform)


def find_markdown(dirpath):
    for mkdn_filepath in dc.find_documetation(dirpath, doc_ext='.md'):
        yield mkdn_filepath


class MdInputHeaderState(dc.InputHeaderState):

    def __init__(self, lexer):
        pattern = "Input:\n```\n"
        super(MdInputHeaderState, self).__init__(lexer, pattern)


class MdInputCmdState(dc.InputCmdState):

    def __init__(self, lexer):
        pattern = "\n"
        super(MdInputCmdState, self).__init__(lexer, pattern,
                                              is_term_pattern=True)


class MdExitHeaderState(dc.InputHeaderState):

    def __init__(self, lexer):
        pattern = "```\n"
        super(MdExitHeaderState, self).__init__(lexer, pattern)


class MdOutputHeaderState(dc.OutputHeaderState):

    def __init__(self, lexer):
        pattern = "Result:\n```\n"
        super(MdOutputHeaderState, self).__init__(lexer, pattern)


class MdExpectedOutputState(dc.ExpectedOutputState):

    def __init__(self, lexer):
        pattern = "`"
        super(MdExpectedOutputState, self).__init__(lexer, pattern,
                                                    is_term_pattern=True)


successful_exit_status = dc.IsValidExitStatus(requisite_status=True)
failed_exit_status = dc.IsValidExitStatus(requisite_status=False)


def successful_match(transition_state, char, status):
    valid_first_char = dc.is_valid_first_char(transition_state, char)
    return successful_exit_status(status) and valid_first_char


def failed_match(transition_state, char, status):
    valid_first_char = dc.is_valid_first_char(transition_state, char)
    return failed_exit_status(status) and valid_first_char


class MarkdownLexer(dc.Lexer):

    def __init__(self):
        root = self.get_state_transition_tree()
        super(MarkdownLexer, self).__init__(root, DEFAULT_ENVIRONMENT)

    def get_state_transition_tree(self):
        null_intro = dc.NullState(self)
        input_header = MdInputHeaderState(self)
        input_cmd = MdInputCmdState(self)
        input_exit_header = MdExitHeaderState(self)
        null_wait_output = dc.NullState(self)
        output_header = MdOutputHeaderState(self)
        expected_output = MdExpectedOutputState(self)

        null_intro.set_transition_states({input_header: failed_match})

        input_header.set_transition_states({input_cmd: successful_match,
                                            null_intro: failed_match})

        input_cmd.set_transition_states({input_exit_header: successful_match})

        input_exit_header.set_transition_states({null_wait_output:
                                                     successful_match})

        null_wait_output.set_transition_states({output_header: failed_match})
        output_header.set_transition_states({expected_output: successful_match,
                                             null_intro: failed_match})
        expected_output.set_transition_states({input_header: successful_match,
                                               null_intro: successful_match})
        return null_intro


class MarkdownParser:

    def parse(self, markdown_filepath):
        pass


class MarkdownSemanticAnalyzer:

    def analyze(self, markdown_filepath):
        pass


class MarkdownCompiler:


    def compile(self, dirpath):
        mkdn_lexer = MarkdownLexer()
        tokens = []

        for mkdn_filepath in find_markdown(dirpath):
            mkdn_lexer.lex(mkdn_filepath)
            tokens.append(mkdn_lexer.token_sequence)
            yield mkdn_filepath, mkdn_lexer.pop_tok_seq()


if __name__ == '__main__':
    md_compiler = MarkdownCompiler()
    for filepath, token_sequence in md_compiler.compile('.'):
        print(filepath)
        print(token_sequence)

