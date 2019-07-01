from projects.continuous_integration.documentation_verification import documentation_compiler as dc

import sys

if sys.platform.startswith('linux'):
    DEFAULT_ENVIRONMENT = 'paicoind -regtest &'
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
        pattern = "`"
        super(MdInputCmdState, self).__init__(lexer, pattern,
                                                 is_term_pattern=True)


class MdOutputHeaderState(dc.OutputHeaderState):

    def __init__(self, lexer):
        pattern = "Result:\n```\n"
        super(MdOutputHeaderState, self).__init__(lexer, pattern)


class MdExpectedOutputState(dc.ExpectedOutputState):

    def __init__(self, lexer):
        pattern = "`"
        super(MdExpectedOutputState, self).__init__(lexer, pattern,
                                                 is_term_pattern=True)





class MarkdownLexer(dc.Lexer):

    def __init__(self):
        root = self.get_state_transition_tree()
        super(MarkdownLexer, self).__init__(root, DEFAULT_ENVIRONMENT)

    def get_state_transition_tree(self):
        null_intro = dc.NullState(self)
        input_header = MdInputHeaderState(self)
        input_cmd = MdInputCmdState(self)
        null_wait_output = dc.NullState(self)
        output_header = MdOutputHeaderState(self)
        expected_output = MdExpectedOutputState(self)

        null_intro.set_transition_states([input_header])

        input_header.set_transition_states([input_cmd, null_intro])
        input_cmd.set_transition_states([output_header, null_wait_output])

        null_wait_output.set_transition_states([output_header])
        output_header.set_transition_states([expected_output, null_intro])
        expected_output.set_transition_states([input_header, null_intro])
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
        mkdn_parser = MarkdownParser()
        mkdn_analyzer = MarkdownSemanticAnalyzer()

        for mkdn_filepath in find_markdown(dirpath):
            mkdn_lexer.lex(mkdn_filepath)
            print(mkdn_lexer.token_sequence)
            mkdn_parser.parse(mkdn_filepath)
            mkdn_analyzer.analyze(mkdn_filepath)


if __name__ == '__main__':
    md_compiler = MarkdownCompiler()
    md_compiler.compile('.')

