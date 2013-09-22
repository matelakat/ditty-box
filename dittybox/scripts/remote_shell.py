import argparse
import StringIO

from dittybox import controller


def sudo():
    parser = argparse.ArgumentParser(description='Remote sudo')
    parser.add_argument('ssh_config', help='SSH config')
    parser.add_argument('host', help='Host')
    parser.add_argument('password', help='Password')
    parser.add_argument('command', help='Command to execute')
    args = parser.parse_args()

    executor = controller.SSHExecutor(args)

    f = StringIO.StringIO(args.command)

    out = executor.sudo_script(f)
    print out
