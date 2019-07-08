from projects.continuous_integration.markdown_verification.sandbox.markdown_compiler import MarkdownCompiler
from projects.continuous_integration.documentation_verification.documentation_compiler import TokenIdentifiers
from projects.continuous_integration.markdown_verification.sandbox.docker_wrapper import run_cmd

# shebang for docker to let the sh script know to execute python with sudo
#! docker
ENV = TokenIdentifiers.ENVIRONMENT
IN = TokenIdentifiers.IN_CMD
EXPECTED_OUT = TokenIdentifiers.EXPECTED_OUT

class Verification:

    def __init__(self, image):
        self.image = image
        self.md_compiler = MarkdownCompiler()

    def verify(self, dirpath):
        for filepath, token_sequence in self.md_compiler.compile(dirpath):
            for cmd_set in token_sequence:
                if self.run_cmd_set(cmd_set):
                    print("They match!")
                else:
                    print("They don't match!")

    def run_cmd_set(self, cmd_set):
        # TODO: Clean up this value shenanigans.
        env = cmd_set[ENV.value].value
        cmd = cmd_set[IN.value].value
        expected_out = cmd_set[EXPECTED_OUT.value].value
        print(cmd)
        actual_out = run_cmd(self.image, cmd, env)
        print('expected_out', expected_out)
        print('actual out', actual_out)
        return expected_out == actual_out


if __name__ == '__main__':
    '''
    import argparse

    parser = argparse.ArgumentParser()

    parser.add_argument('input_dir')
    parser.add_argument('-o', 'output_dir')
    '''
    verification = Verification(image='paicoin_server:v2')
    verification.verify('.')

