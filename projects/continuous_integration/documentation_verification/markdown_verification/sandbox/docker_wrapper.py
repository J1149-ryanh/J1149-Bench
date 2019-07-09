import docker
import time


def run_cmd(image, cmd, env=''):
    client = docker.from_env()
    check_env(env)
    env_cmds = env.split('\n')
    paicoind = env_cmds[0]
    container = client.containers.run(image, entrypoint=paicoind, detach=True,
                                      tty=True, auto_remove=True)
    time.sleep(1)
    for env_cmd in env_cmds[1:]:
        docker.exec_run(env_cmd)
    cmd = sanitize(cmd)
    res = container.exec_run(cmd)
    bytes_output = res.output
    # convert from bytes literal to string
    output = bytes_output.decode("utf-8")
    return output


def check_env(env):
    if not env.startswith('paicoind -'):
        raise ValueError('Environment must start with paicoind; environment'
                         ' looks like: %s\n'%env)


def sanitize(cmd):
    is_expected_cmd_encap = not cmd.startswith("'") and not cmd.endswith("'")
    if not (is_expected_cmd_encap):
        raise ValueError("The cmd did not match the encapsulation rules:"
                         "\ncmd=%s\n" % (cmd))
    new_cmd = "/bin/bash -c '" + cmd + "'"
    return new_cmd


if __name__ == '__main__':

    image = 'paicoin_repl_server:v2'
    cmd = 'paicoin-cli getbestblockhash'
    output = run_cmd(image, cmd)
    print(output)
