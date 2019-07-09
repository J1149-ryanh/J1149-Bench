from projects.continuous_integration.documentation_verification.markdown_verification.sandbox import md_v_and_v
import pytest


def pytest_generate_tests(metafunc):
    results = []
    verification = md_v_and_v.Verification(image='paicoin_server:v2')
    for result in verification.yield_results(r'/home/rxhernandez/PycharmProjects/j1149.github.io/_papi'):
        results.append(result)
    metafunc.parametrize('result', results)


def test_result(result):
    if result.actual_out != result.expected_out:
        msg = md_v_and_v.gen_message(result)
        raise md_v_and_v.VerificationException(msg)
