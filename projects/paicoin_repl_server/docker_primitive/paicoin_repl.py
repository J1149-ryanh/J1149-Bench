#!/usr/bin/env python
from test_framework.test_framework import BitcoinTestFramework
from test_framework.test_node import TestNode

from enum import Enum, unique, auto
from overrides import overrides
import os
import psutil
import socket
import shutil
import shlex, subprocess
import sys


import argparse


parser = argparse.ArgumentParser()
parser.add_argument('-n', '--num_terminals', help='Number of terminals')
args = parser.parse_args()


class ReplError(Exception):
    """Base exception for people potentially using this as an api"""
    pass


class ParameterNotSupported(ReplError):
    """We don't yet support that parameter"""
    pass


class NetworkNotSupported(ReplError):
    """We don't yet support that parameter"""
    pass


class CommandNotFound(ReplError):
    """We don't yet support anything but paicoin commands"""
    pass


# TODO: Rename; this name is garbage.
class ReplFrameworkWrapper(BitcoinTestFramework):

    @overrides
    def set_test_params(self):
        pass

    @overrides
    def run_test(self):
        pass


@unique
class Status(Enum):
    SUCCESS = auto()
    FAILURE = auto()


def get_free_tcp_port():
    tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp.bind(('', 0))
    addr, port = tcp.getsockname()
    tcp.close()
    return port

D = 'paicoind'
CLI = 'paicoin-cli'

paicoin_copy ='~/.paicoin_copy%s'%str(args.num_terminals) 
# where paicoin.conf exists
MAINNET_DATA_DIR = os.path.expanduser(paicoin_copy)
TESTNET_DATA_DIR = os.path.join(MAINNET_DATA_DIR,'testnet')
REGTEST_DATA_DIR = os.path.join(MAINNET_DATA_DIR, 'regtest')

os.makedirs(MAINNET_DATA_DIR)
os.makedirs(TESTNET_DATA_DIR)
os.makedirs(REGTEST_DATA_DIR)

shutil.copy2(os.path.expanduser(r'~/.paicoin/paicoin.conf'), MAINNET_DATA_DIR)
shutil.copy2(os.path.expanduser(r'~/.paicoin/testnet/paicoin.conf'), TESTNET_DATA_DIR)
shutil.copy2(os.path.expanduser(r'~/.paicoin/regtest/paicoin.conf'), REGTEST_DATA_DIR)


COV_DIR = os.path.expanduser('~/tmp/paicoin/functional/cov_dir')

if not os.path.exists(COV_DIR):
    os.makedirs(COV_DIR)

port = str(get_free_tcp_port())
rpcport = str(get_free_tcp_port())

extra_args = ['-port=%s' % port,'-rpcport=%s' % rpcport]

test_node_idx = 0
mainnet_testnode = TestNode(i=test_node_idx, datadir=MAINNET_DATA_DIR,
                            rpchost='localhost', timewait=60,
                            bitcoind='paicoind', bitcoin_cli='paicoin-cli',
                            coverage_dir=COV_DIR, cwd=MAINNET_DATA_DIR,
                            use_cli=True, extra_args=extra_args )

test_node_idx += 1
testnet_testnode = TestNode(i=test_node_idx, datadir=TESTNET_DATA_DIR,
                            rpchost='localhost', timewait=60,
                            bitcoind='paicoind', bitcoin_cli='paicoin-cli',
                            coverage_dir=COV_DIR,
                            cwd=TESTNET_DATA_DIR, use_cli=True, extra_args=extra_args )
test_node_idx += 1
regtest_testnode = TestNode(i=test_node_idx, datadir=REGTEST_DATA_DIR,
                            rpchost='localhost', timewait=60,
                            bitcoind='paicoind',
                            bitcoin_cli='paicoin-cli', coverage_dir=COV_DIR,
                            cwd=REGTEST_DATA_DIR, use_cli=True,extra_args=extra_args  )

MAINNET = '-mainnet'
TESTNET = '-testnet'
REGTEST = '-regtest'
NETS = {MAINNET: mainnet_testnode, TESTNET: testnet_testnode,
        REGTEST: regtest_testnode}

DATA_DIRS = {MAINNET: MAINNET_DATA_DIR, TESTNET: TESTNET_DATA_DIR, REGTEST: REGTEST_DATA_DIR}

for net in DATA_DIRS:
    data_dir = DATA_DIRS[net]
    path = os.path.join(data_dir, 'paicoin.conf')
    with open(path, 'a') as f:
        for arg in extra_args:
            f.write('\n'+arg.replace('-','')+'\n')

def is_paicoind_running(net=None):
    for pid in psutil.pids():
        p = psutil.Process(pid)
        cmdline = p.cmdline()

        if len(cmdline) < 2:
            continue
        data_dir_cmd_line = cmdline[1]
        data_dir = data_dir_cmd_line.split('=')[-1]
        is_same_data_dir = False
        for known_net in DATA_DIRS:
            if known_net == net and data_dir == DATA_DIRS[known_net]:
                is_same_data_dir = True

        if D in cmdline[0] and is_same_data_dir and p.is_running():
            return True

    return False


def rm_whitespace(fn):
    """Remove trailing whitespace from the command before it reaches the
    sanitization functions."""

    def wrapper(cmd, *args, **kwargs):
        cmd = cmd.strip()
        return fn(cmd, *args, **kwargs)

    return wrapper


@rm_whitespace
def sanitize(cmd):
    if cmd.startswith(D):
        d_rm = cmd.split(D)[-1]
        return sanitize_d(d_rm)
    elif cmd.startswith(CLI):
        cli_rm = cmd.split(CLI)[-1]
        return sanitize_cli(cli_rm)
    elif cmd.startswith('exit'):
        sys.exit(0)
    else:
        first_el = cmd.split(' ')[0]
        raise CommandNotFound("%s: command not found" % first_el)


@rm_whitespace
def sanitize_d(cmd):
    # if it's the mainnet. Added "and MAINNET" to give an error in case the
    # mainnet is disallowed from use
    if len(cmd) == 0 and MAINNET:
        return None, Status.SUCCESS

    net = get_net(cmd)
    test_node = get_testnode(cmd)

    if not is_paicoind_running(net):
        # so this is an odd one... If you look at test_node in bitcoin's master
        # branch (July 14, 2019) TestNode().start() takes in an argument:
        # extra_args, which is concatenated with another list in the TestNode
        # instance. Since subprocess.Popen expects a list of strings, this
        # should be an empty list. However, if you look at
        # feature_block.py extra_args is a list with an empty list inside of
        # it, so something seems to be wrong with their implementation or maybe
        # I'm using a newer version of Python than they are.
        # TODO this has a race condition! if two users grab the same port at the
        #  same time, one user will get an error.
        test_node.start(stdout=sys.stdout,
                        stderr=sys.stderr)
        return None, Status.SUCCESS
    else:
        print('%s is already running!' % cmd)
        return None, Status.SUCCESS


@rm_whitespace
def get_net(cmd):
    for el in NETS:
        if cmd.startswith(el):
            return el
    # if it's an empty string it is obviously the mainnet
    if len(cmd) == 0:
        return MAINNET
    raise NetworkNotSupported('%s: network is not supported.' % cmd)


@rm_whitespace
def get_testnode(cmd):
    for el in NETS:
        if cmd.startswith(el):
            return NETS[el]
    # if it's an empty string it is obviously the mainnet
    if len(cmd) == 0:
        return NETS[MAINNET]
    raise NetworkNotSupported('%s: network is not supported.')


@rm_whitespace
def sanitize_ampersand(cmd):
    """It's okay if the user leaves an ampersand to emulate running paicoind
    as a background process
    """
    # no ampersand
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
    #  insecure...)
    net = cmd.split(' ')[0]
    test_node = get_testnode(net)
    if not is_paicoind_running(net):
        print('paicoind %s is not running' % net)
        return None, Status.SUCCESS

    cli_cmd = ' '.join(cmd.split(' ')[1:])
    return sanitize_cli_cmd(cli_cmd, test_node)


@rm_whitespace
def sanitize_cli_cmd(cli_cmd, test_node):
    cli = getattr(test_node, cli_cmd, None)
    if cli is not None:
        try:
            cli()
            return cli, Status.SUCCESS
        except Exception as e:
            import traceback
            print(traceback.format_exc())
    raise ParameterNotSupported("%s: parameter is not yet supported." % cli_cmd)


def read():
    cmd = input(">> ")

    cli_node, status = sanitize(cmd)
    if status == Status.SUCCESS:
        pass
    else:
        raise ReplError("%s: Something went wrong." % cmd)
    return cli_node


def evaluate(cli_node):
    output = cli_node()
    return output


def prnt(output):
    print(output)


def shutdown():
    for el in NETS:
        test_node = NETS[el]
        test_node.stop_node()
    shutil.rmtree(paicoin_copy)


def run():
    print("Welcome to Paicoin's REPL!")
    # Make sure everything else that needed to print has already printed before
    # we enter the repl
    sys.stdout.flush()
    sys.stderr.flush()
    while True:
        try:
            cli_node = read()
            if cli_node is None:
                continue
            output = evaluate(cli_node)
            prnt(output)
        except Exception as e:
            import traceback
            print(traceback.format_exc())

    shutdown()

run()
