import os
import sys
import signal
import argparse
import json
import subprocess

def pid_exists(pid):
    """Check whether pid exists in the current process table.
    UNIX only.
    """
    if pid < 0:
        return False
    if pid == 0:
        # According to "man 2 kill" PID 0 refers to every process
        # in the process group of the calling process.
        # On certain systems 0 is a valid PID but we have no way
        # to know that in a portable fashion.
        raise ValueError('invalid PID 0')
    try:
        os.kill(pid, 0)
    except OSError as err:
        if err.errno == errno.ESRCH:
            # ESRCH == No such process
            return False
        elif err.errno == errno.EPERM:
            # EPERM clearly means there's a process to deny access to
            return True
        else:
            # According to "man 2 kill" possible error values are
            # (EINVAL, EPERM, ESRCH)
            raise
    else:
        return True

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--config', help = 'config file')
    # parser.add_argument('-n', '--number', help = 'process number')
    args = parser.parse_args()

    # if not args.number.isdigit():
    #     print('input number({0}) is not a valid digit.'.format(args.number))
    #     return

    configFile = args.config
    configJson = {}

    if configFile is None or configFile == '' :
        print('must specify config file!')
        return
    else:
        try:
            with open(configFile, 'r') as configFile:
                configJson = json.load(configFile)
        except IOError as err:
            print("Oops!  error open config file: {0}.".format(err))
            return

    if 'server_port' in configJson:
        server_port = configJson['server_port']
    else:
        server_port = 9883

    if 'workers' in configJson:
        workers = configJson['workers']
    else:
        workers = 1

    if workers is not None and type(workers) == int:
        workers_num = workers
    else:
        workers_num = 1

    for port in range(server_port, server_port + workers_num):
        pid_file = '/var/run/ss-{0}.pid'.format(port)
        # print(pid_file)
        try:
            with open(pid_file, 'r') as f:
                pid = f.read()
                if pid is not None and pid_exists(pid) == True:
                    os.kill(int(pid), signal.SIGTERM) # or signal.SIGKILL
                else:
                    print('Pid({0}) is not running or invalid.'.format(pid))
        except IOError as err:
            print("Oops!  error open config file: {0}.".format(err))
            continue
            # return

if __name__ == "__main__":
    # execute only if run as a script
    main()
