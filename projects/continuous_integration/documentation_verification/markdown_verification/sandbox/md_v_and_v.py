from projects.continuous_integration.documentation_verification.markdown_verification.sandbox.markdown_compiler import MarkdownCompiler
from projects.continuous_integration.documentation_verification.documentation_compiler import TokenIdentifiers
from projects.continuous_integration.documentation_verification.markdown_verification.sandbox.docker_wrapper import run_cmd

from collections import namedtuple

# shebang for docker to let the sh script know to execute python with sudo
#! docker
ENV = TokenIdentifiers.ENVIRONMENT
IN = TokenIdentifiers.IN_CMD
EXPECTED_OUT = TokenIdentifiers.EXPECTED_OUT

VerificationResult = namedtuple('VerificationResult',
                                'filepath, cmd, expected_out actual_out')


class Verification:

    def __init__(self, image):
        self.image = image
        self.md_compiler = MarkdownCompiler()

    def yield_results(self, dirpath):
        for filepath, token_sequence in self.md_compiler.compile(dirpath):
            for cmd_set in token_sequence:
                expected_out = cmd_set[EXPECTED_OUT.value].value
                actual_out = self.run_cmd_set(cmd_set)
                cmd = cmd_set[IN.value].value
                yield VerificationResult(filepath, cmd, expected_out, actual_out)

    def run_cmd_set(self, cmd_set):
        # TODO: Clean up this value shenanigans.
        env = cmd_set[ENV.value].value
        cmd = cmd_set[IN.value].value
        actual_out = run_cmd(self.image, cmd, env)
        return actual_out


class VerificationException(Exception):
    "The verification sequence did not produce the correct results."
    pass


def gen_message(result):
    import os
    fname = os.path.basename(result.filepath)
    if result.expected_out == result.actual_out:
        conj = 'and'
    else:
        conj = 'but'
    s = "for %s, the command %s had an expected value of,\n\n %s\n" \
        "%s received a value of\n\n %s\n" % (fname,
                                             result.cmd,
                                             result.expected_out,
                                             conj,
                                             result.actual_out)
    return s


if __name__ == '__main__':
    dirpath = r'/home/rxhernandez/PycharmProjects/j1149.github.io/_papi'
    verification = Verification(image='paicoin_repl_server_git_test:v1')
    for verification_result in verification.yield_results(dirpath):
        msg = gen_message(verification_result)
        print(msg)

