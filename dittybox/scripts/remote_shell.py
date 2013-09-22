import argparse
import StringIO
import sys

from dittybox import controller


def sudo():
    parser = argparse.ArgumentParser(description='Remote sudo')
    parser.add_argument('ssh_config', help='SSH config')
    parser.add_argument('host', help='Host')
    parser.add_argument('password', help='Password')
    parser.add_argument('command', help='Command to execute')
    args = parser.parse_args()

    executor = controller.SSHExecutor(args)

    result = executor.sudo_script(args.command)
    executor.disconnect()

    sys.stdout.flush()

    print "Result code:", result.return_code
    print "Standard out:", result.stdout
    print "Standard error:", result.stderr
