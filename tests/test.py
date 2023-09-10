import sys

from medusa import PortBlaster, PortBlasterError

if __name__ == '__main__':
    mds = PortBlaster()
    print("medusa version:", mds.medusa_version)
    mds.brute(
        hosts='192.168.2.185',
        ports='22',
        arguments='-M ssh',
        isfile_hosts=False,
        isfile_user=False,
        isfile_password=False
    )
    print("medusa command line:", mds.command_line)
    print(mds.get_medusa_last_output)
    # print('medusa bruteinfo: ', mds.bruteinfo)
    # print('medusa brutestats: ', mds.brutestats)

    for host in mds.all_hosts:
        print("Host: %s (%s)" % (host, mds[host]))
