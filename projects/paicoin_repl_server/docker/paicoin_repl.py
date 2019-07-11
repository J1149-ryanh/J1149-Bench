
from test_framework.test_framework import BitcoinTestFramework
from test_framework.test_node import TestNode

from enum import Enum, unique, auto

class ReplError(Exception):
    """Base exception for people potentially using this as an api"""
    pass


class ParameterNotSupported(ReplError):
    """We don't yet support that parameter"""
    pass


class CommandNotFound(ReplError):
    """We don't yet support anything but paicoin commands"""
    pass

# TODO: Rename; this name is garbage.
class ReplFrameworkWrapper(BitcoinTestFramework):
    pass

@unique
class Status(Enum):
    SUCCESS = auto()
    FAILURE = auto()

D = 'paicoind'
CLI = 'paicoin-cli'

# TODO: look into whether allowing users to access the mainnet is a worthy idea;
#  maybe our paicoin repl server could be monetized by storing their wallets in
#  a docker containe??? Maybe that's ridiculous; I'm way too tired to analyze
#  this properly.
import warnings
warnings.warn("Why did Ryan leave the mainnet avaiable???")
MAINNET = '-mainnet'
TESTNET = '-testnet'
REGTEST = '-regtest'
NETS = [MAINNET, TESTNET, REGTEST]

sanitizer_tn = TestNode()


def rm_whitespace(fn):
    """Remove trailing whitespace from the command before it reaches the
    sanitization functions."""

    def wrapper(cmd):
        cmd = cmd.strip()
        return fn(cmd)

    return wrapper

@rm_whitespace
def sanitize(cmd):
    if cmd.startswith(D) :
        d_rm = cmd.split(D)[-1]
        return sanitize_d(d_rm)
    elif cmd.startswith(CLI):
        cli_rm = cmd.split(CLI)[-1]
        return sanitize_cli(cli_rm)
    else:
        first_el = cmd.split(' ')[0]
        raise CommandNotFound("%s: command not found" % first_el)

@rm_whitespace
def sanitize_d(cmd):
    # if it's the mainnet. Added "and MAINNET" to give an error in case the
    # mainnet is disallowed from use
    if len(cmd) == 0 and MAINNET:
        return Status.SUCCESS

    if santitize_net(cmd) == Status.SUCCESS:
        return Status.SUCCESS

    param = cmd.split(' ')[0]
    raise ParameterNotSupported("%s: parameter is not yet supported." % param)

@rm_whitespace
def santitize_net(cmd):
    for el in NETS:
        if cmd.startswith(el):
            return Status.SUCCESS
    return Status.FAILURE

@rm_whitespace
def sanitize_ampersand(cmd):
    """It's okay if the user leaves an ampersand to emulate running paicoind
    as a background process
    """
    #
    # no ampersand. Boooooooo
    if len(cmd) == 0:
        return Status.SUCCESS
    if cmd.startswith('&'):
        return Status.SUCCESS
    param = cmd.split(' ')[0]
    raise ParameterNotSupported("%s: parameter is not yet supported." % param)

@rm_whitespace
def sanitize_cli(cmd):
    # TODO complete for all possible parameters. It might be sufficient to pass
    #  the parameters straight to the TestNode (that also might be quite
    #  insecure...
    cli_cmd = cmd.split(' ')[0]
    if getattr(sanitizer_tn, cli_cmd, None) is not None:
        return Status.SUCCESS
    raise NotImplementedError("IMPLEMENT!")



def run():

    while True:
        cmd = None
        try:
            cmd = input(">> ")
            if sanitize(cmd) == Status.SUCCESS:
                print("%s: passes" % cmd)
            else:
                raise ReplError("Something went wrong.")
        except Exception as e:
            if cmd is not None:
                print(e.args[0])
            else:
                print("Something went wrong.")


run()
