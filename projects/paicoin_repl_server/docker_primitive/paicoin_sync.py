import json
import subprocess
import time


def start_processes():
    subprocess.Popen(['paicoind', '-mainnet'])
    subprocess.Popen(['paicoind', '-testnet'])
    # need to sleep some to give the processes time to start.
    # TODO: on a slower machine this may not be nearly enough time. It would
    #  probably be prudent to wrap sync_fin with an exception handler and error
    #  out when way too much time has passed.
    time.sleep(10)


def sync_fin(network):
    cmd = ['paicoin-cli', network, 'getblockchaininfo']
    output = subprocess.check_output(cmd)
    j = json.loads(output)
    try:
        perc_blocks_retrieved = float(j["blocks"]) / float(j["headers"])
    except ZeroDivisionError:
        perc_blocks_retrieved = 0
    verf_prog = float(j["verificationprogress"])
    print("network=%s\n "
          "perc. retrieved = %s%%\n "
          "perc. verified = %s%%\n "
          "best block hash=%s\n" % (network,
                                    perc_blocks_retrieved*100,
                                    verf_prog*100,
                                    j["bestblockhash"]))
    return not (perc_blocks_retrieved < 1) and not (verf_prog < .99)


def synchronize():
    start_processes()
    both_sync_fin = lambda net1, net2: sync_fin(net1) and sync_fin(net2)

    while not both_sync_fin('-mainnet', '-testnet'):
        time.sleep(1)
    return 0


synchronize()
