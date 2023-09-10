# -*- coding: utf-8 -*-

import logging
import os
import re
import shlex
import subprocess
import sys
import json

from multiprocessing import Process

__author__ = 'hanxinkong (xinkonghan@gmail.com)'
__last_modification__ = '2022.11.17'

IS_PY2 = sys.version_info[0] == 2


class NetworkConnectionError(Exception):
    pass


class PortBlasterError(Exception):
    """Exception error class for PortBlaster class."""

    def __init__(self, value):
        """Initialize the exception."""
        self.value = value

    def __str__(self):
        """String representation of a value."""
        return repr(self.value)

    def __repr__(self):
        """Representation of an exception."""
        return 'PortBlasterError exception {0}'.format(self.value)


class PortBlaster(object):
    """Class which allows to use medusa from Python."""

    def __init__(self, medusa_search_path=(
            'medusa', '/usr/bin/medusa', '/usr/local/bin/medusa', '/sw/bin/medusa', '/opt/local/bin/medusa')):
        """
        Initialize the Port blaster.

        * detects medusa on the system and medusa version
        * may raise PortBlasterError exception if medusa is not found in the path

        :param medusa_search_path: tuple of string where to search for medusa executable. Change this if you want to use a specific version of medusa.
        :returns: nothing

        """
        self._medusa_path = ''  # medusa path
        self._brute_result = {"command_line": {}, "brute": {}}
        self._medusa_version_number = 0  # medusa version number
        self._medusa_subversion_number = 0  # medusa subversion number
        self._medusa_revised_number = 0  # medusa revised number
        self._medusa_last_output = ''  # last full ascii medusa output
        self._args = ''
        self._bruteinfo = {}
        is_medusa_found = False  # true if we have found medusa

        self.__process = None

        # regex used to detect medusa (http or https)
        regex = re.compile(
            r'Medusa v[0-9]*\.[0-9]*[^ ]* \[http(|s)://.*\]'
        )
        # launch 'medusa -V', we wait after
        # 'Medusa v2.2 [http://www.foofus.net] (C) JoMo-Kun / Foofus Networks <jmk@foofus.net>'
        # This is for Mac OSX. When idle3 is launched from the finder, PATH is not set so medusa was not found
        for medusa_path in medusa_search_path:
            try:
                if sys.platform.startswith('freebsd') \
                        or sys.platform.startswith('linux') \
                        or sys.platform.startswith('darwin'):
                    p = subprocess.Popen(
                        [medusa_path, '-V'],
                        bufsize=10000,
                        stdout=subprocess.PIPE,
                        close_fds=True)
                else:
                    p = subprocess.Popen(
                        [medusa_path, '-V'],
                        bufsize=10000,
                        stdout=subprocess.PIPE)

            except OSError:
                pass
            else:
                self._medusa_path = medusa_path  # save path
                break
        else:
            raise PortBlasterError(
                'medusa program was not found in path. PATH is : {0}'.format(os.getenv('PATH'))
            )
        if IS_PY2:
            self._medusa_last_output = bytes.decode(p.communicate()[0])  # sav stdout
        else:
            self._medusa_last_output = p.communicate()[0]
            if isinstance(self._medusa_last_output, bytes):
                self._medusa_last_output = self._medusa_last_output.decode('utf-8')

        for line in self._medusa_last_output.split(os.linesep):
            if regex.match(line):
                is_medusa_found = True
                # Search for version number
                regex_version = re.compile(r'v(?P<version>\d{1,4})\.(?P<subversion>\d{1,4})')
                rv = regex_version.search(line)

                if rv:
                    # extract version/subversion/revised
                    self._medusa_version_number = int(rv.group('version'))
                    self._medusa_subversion_number = int(rv.group('subversion'))
                    # self._medusa_revised_number = int(rv.group('revised'))
                break

        if not is_medusa_found:
            raise PortBlasterError('medusa program was not found in path')

    def __getitem__(self, host):
        """Return a host detail."""
        if IS_PY2:
            assert type(host) in (str, unicode), 'Wrong type for [host], should be a string [was {0}]'.format(
                type(host))
        else:
            assert type(host) is str, 'Wrong type for [host], should be a string [was {0}]'.format(type(host))

        if host in self._brute_result['brute']:
            return self._brute_result['brute'][host]
        return None

    @property
    def get_medusa_last_output(self):
        """
        Return the last text output of medusa in raw text
        this may be used for debugging purpose.

        :returns: string containing the last text output of medusa in raw text
        """
        return self._medusa_last_output

    @property
    def medusa_version(self):
        """
        Return the medusa version if detected (int version, int subversion)
        or (0, 0) if unknown.

        :returns: medusa_version_number, medusa_subversion_number
        """
        return "v{}.{}".format(self._medusa_version_number, self._medusa_subversion_number)

    @property
    def all_hosts(self):
        """Return a sorted list of all hosts."""
        host_list = []
        if self._brute_result['brute']:
            host_list = self._brute_result['brute'].keys()
        return host_list

    @property
    def command_line(self):
        """
        Returns the command line used for blasting.

        may raise AssertionError exception if called before scanning
        """

        return self._brute_result['command_line']

    @property
    def brute_result(self):
        """
        Returns the command line used for blasting.

        may raise AssertionError exception if called before scanning
        """
        return json.dumps(self._brute_result)

    def brute(self, hosts='127.0.0.1', user='root', password='root', ports=None, arguments='', sudo=False, **kwargs):
        """
        Brute given hosts.

        May raise PortScannerError exception if medusa output was not XML

        Test existence of the following key to know
        if something went wrong : ['medusa']['bruteinfo']['error']
        If not present, everything was ok.
        :key isfile_hosts:
        :key isfile_user:
        :key isfile_password:
        :param password:
        :param user:
        :param hosts: string for hosts as medusa use it 'scanme.medusa.org' or '198.116.0.1'
        :param ports: string for ports as medusa use it '22'
        :param arguments: string of arguments for medusa '-[h Text |H File] -[u Text | U File] -[p Text | P File] -M [ssh|...] -n [port] -L -f -F -t -T'
        :param sudo: launch medusa with sudo if True

        :returns: brute_result as dictionary
        """
        if IS_PY2:
            assert type(hosts) in (str, unicode), 'Wrong type for [hosts], should be a string [was {0}]'.format(
                type(hosts))  # noqa
            assert type(ports) in (
                str, unicode, type(None)), 'Wrong type for [ports], should be a string [was {0}]'.format(
                type(ports))  # noqa
            assert type(arguments) in (str, unicode), 'Wrong type for [arguments], should be a string [was {0}]'.format(
                type(arguments))  # noqa
        else:
            assert type(hosts) is str, 'Wrong type for [hosts], should be a string [was {0}]'.format(
                type(hosts))  # noqa
            assert type(ports) in (str, type(None)), 'Wrong type for [ports], should be a string [was {0}]'.format(
                type(ports))  # noqa
            assert type(arguments) is str, 'Wrong type for [arguments], should be a string [was {0}]'.format(
                type(arguments))  # noqa

        h_args = shlex.split(hosts)
        f_args = shlex.split(arguments)

        isfile_hosts = kwargs.pop('isfile_hosts', False)
        isfile_user = kwargs.pop('isfile_user', False)
        isfile_password = kwargs.pop('isfile_password', False)

        # Launch brute
        isfile_hosts = '-H' if isfile_hosts else '-h'
        isfile_user = '-U' if isfile_user else '-u'
        isfile_password = '-P' if isfile_password else '-p'

        args = [self._medusa_path] + ['-O', '-'] + [isfile_hosts, *h_args] + [isfile_user, user] + [isfile_password,
                                                                                                    password] + ['-n',
                                                                                                                 ports] * (
                       ports is not None) + f_args

        self._args = ' '.join(args)

        if sudo:
            args = ['sudo'] + args

        self._brute_result['command_line'] = self._args

        p = subprocess.Popen(
            args,
            bufsize=100000,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        # wait until finished
        # get output
        self._medusa_last_output, medusa_err = p.communicate()
        if IS_PY2:
            self._medusa_last_output = bytes.decode(self._medusa_last_output)
            medusa_err = bytes.decode(medusa_err)
        else:
            if isinstance(self._medusa_last_output, bytes):
                self._medusa_last_output = self._medusa_last_output.decode('utf-8')
            if isinstance(medusa_err, bytes):
                medusa_err = medusa_err.decode('utf-8')

        # If there was something on stderr, there was a problem so abort...  in
        # fact not always. As stated by AlenLPeacock :
        # This actually makes python-medusa mostly unusable on most real-life
        # networks -- a particular subnet might have dozens of scannable hosts,
        # but if a single one is unreachable or unroutable during the scan,
        # medusa.brute() returns nothing. This behavior also diverges significantly
        # from commandline medusa, which simply stderrs individual problems but
        # keeps on trucking.

        medusa_err_keep_trace = []
        medusa_warn_keep_trace = []
        if len(medusa_err) > 0:
            regex_warning = re.compile('^NOTICE: .*', re.IGNORECASE)
            for line in medusa_err.split(os.linesep):
                if len(line) > 0:
                    rgw = regex_warning.search(line)
                    if rgw is not None:
                        # sys.stderr.write(line+os.linesep)
                        medusa_warn_keep_trace.append(line + os.linesep)
                    else:
                        # raise PortBlasterError(medusa_err)
                        medusa_err_keep_trace.append(medusa_err)

        # ACCOUNT FOUND: [ssh] Host: 127.0.0.1 User: root Password: root [SUCCESS]
        # [{'host': '127.0.0.1', 'user': 'root', 'password': 'root', 'status': 'SUCCESS'}]
        try:
            regex_found = re.compile('ACCOUNT FOUND: .*', re.IGNORECASE)
            brute_result = regex_found.findall(self._medusa_last_output)
            for line in brute_result:
                if len(line) > 0:
                    _host = re.search(r'Host:[\s](.*?)[\s]', line).group(1)
                    _user = re.search(r'User:[\s](.*?)[\s]', line).group(1)
                    _password = re.search(r'Password:[\s](.*?)[\s]', line).group(1)
                    _status = re.findall(r'\[(.*?)\]', line)[-1]
                    if _host not in self._brute_result["brute"]:
                        self._brute_result["brute"][_host] = []
                    self._brute_result["brute"][_host].append({
                        'host': _host,
                        'port': ports,
                        'user': _user,
                        'password': _password,
                        'status': _status
                    })

        except ValueError as ex:
            pass

        return self._brute_result

    def has_host(self, host):
        """If host has result it returns True, False otherwise."""
        if self._brute_result['brute'] and host in self._brute_result['brute']:
            return True
        return False


if __name__ == '__main__':

    import sys

    try:
        mds = PortBlaster()
    except PortBlasterError:
        print("medusa binary not found", sys.exc_info()[0])
        sys.exit(1)
    except:
        print("Unexpected error:", sys.exc_info()[0])
        sys.exit(1)

    print("medusa version:", mds.medusa_version)
    mds.brute(
        hosts='127.0.0.1',
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
