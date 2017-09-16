import os
import shlex
import sys
import argparse
import json
import subprocess

# https://gist.github.com/techtonik/4368898
def find_executable(executable, path=None):
    """Find if 'executable' can be run. Looks for it in 'path'
    (string that lists directories separated by 'os.pathsep';
    defaults to os.environ['PATH']). Checks for all executable
    extensions. Returns full path or None if no command is found.
    """
    if path is None:
        path = os.environ['PATH']
    paths = path.split(os.pathsep)
    extlist = ['']
    if os.name == 'os2':
        (base, ext) = os.path.splitext(executable)
        # executable files on OS/2 can have an arbitrary extension, but
        # .exe is automatically appended if no dot is present in the name
        if not ext:
            executable = executable + ".exe"
    elif sys.platform == 'win32':
        pathext = os.environ['PATHEXT'].lower().split(os.pathsep)
        (base, ext) = os.path.splitext(executable)
        if ext.lower() not in pathext:
            extlist = pathext
    for ext in extlist:
        execname = executable + ext
        if os.path.isfile(execname):
            return execname
        else:
            for p in paths:
                f = os.path.join(p, execname)
                if os.path.isfile(f):
                    return f
    else:
        return None

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
    # print(configJson)
    if 'server' in configJson:
        server_addr = configJson['server']
    else:
        server_addr = '0.0.0.0'

    if 'server_port' in configJson:
        server_port = configJson['server_port']
    else:
        server_port = 9883
        
    # server_port = configJson['server_port']
    encrypt_password = configJson['password']
    encrypt_method = configJson['method']
    timeout = configJson['timeout']

    if 'workers' in configJson:
        workers = configJson['workers']
    else:
        workers = 1

    fast_open = configJson['fast_open']
    plugin = configJson['plugin']
    plugin_opts = configJson['plugin_opts']

    if fast_open is not None and fast_open is True:
        fast_open_opt = 'true'
    else:
        fast_open_opt = 'false'

    if workers is not None and type(workers) == int:
        workers_num = workers
    else:
        workers_num = 1
    
    for port in range(server_port, server_port + workers_num):
        pid_file = '/var/run/ss-{0}.pid'.format(port)
        opts = ' -s {server_addr} -p {server_port} -k \'{encrypt_password}\' -m {encrypt_method} -a root -f {pid_file} -t {timeout} -n 65536 -u -d 8.8.8.8 -d 8.8.4.4 --reuse-port --fast-open --plugin {plugin} --plugin-opts {plugin_opts} > /dev/null 2>&1 &'.format(server_addr = server_addr, server_port = port, encrypt_password = encrypt_password, encrypt_method = encrypt_method, pid_file = pid_file, timeout = timeout, plugin = plugin, plugin_opts = plugin_opts)

        sss_path = find_executable('ss-server')
        command_line = '{0} {1}'.format(sss_path, opts)
        args = shlex.split(command_line)
        # os.spawnl(os.P_NOWAIT, cmds)
        # ls_output=subprocess.Popen([sss_path, opts], stdout=subprocess.PIPE)
        output=subprocess.Popen(args)
        # print(output)
        # print(find_executable('ss-server'))
        # print(port)


if __name__ == "__main__":
    # execute only if run as a script
    main()
