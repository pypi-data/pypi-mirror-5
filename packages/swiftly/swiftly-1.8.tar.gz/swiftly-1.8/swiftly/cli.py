"""
Command Line Client to Swift

Copyright 2011-2013 Gregory Holt

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

__all__ = ['VERSION', 'CLI']

from contextlib import contextmanager
from optparse import Option, OptionParser
from os import environ, makedirs, unlink, utime, walk
from os.path import dirname, exists, getmtime, getsize, join as pathjoin, isdir
from Queue import Empty, Queue
from time import mktime, strptime, time
from urllib import unquote
import sys
import textwrap

from swiftly import VERSION
from swiftly.client import Client, CHUNK_SIZE, generate_temp_url
from swiftly.concurrency import Concurrency

try:
    from simplejson import json
except ImportError:
    import json


MUTED_ACCOUNT_HEADERS = ['accept-ranges', 'content-length', 'content-type',
                         'date']
MUTED_CONTAINER_HEADERS = ['accept-ranges', 'content-length', 'content-type',
                           'date']
MUTED_OBJECT_HEADERS = ['accept-ranges', 'date']


def _delayed_imports(eventlet=None):
    PIPE = Popen = None
    if eventlet is None:
        try:
            from eventlet import __version__
            # Eventlet 0.11.0 fixed the CPU bug
            if __version__ >= '0.11.0':
                eventlet = True
        except ImportError:
            pass
    if eventlet:
        try:
            from eventlet.green.subprocess import PIPE, Popen
        except ImportError:
            pass
    if PIPE is None or Popen is None:
        from subprocess import PIPE, Popen
    return PIPE, Popen


def _command(func):
    func.__is_command__ = True
    func.__is_client_command__ = False
    return func


def _client_command(func):
    func.__is_command__ = True
    func.__is_client_command__ = True
    return func


def _get_return_code(rv):
    # Most funcs just return a return code, but some funcs return a list with
    # the return code as the first item and additional items for use with
    # nested calls.
    try:
        rc = rv[0]
    except TypeError:
        rc = rv
    return rc


class _OptionParser(OptionParser):

    def __init__(self, usage=None, option_list=None, option_class=Option,
                 version=None, conflict_handler='error', description=None,
                 formatter=None, add_help_option=True, prog=None, epilog=None,
                 stdout=None, stderr=None, preamble=''):
        self.preamble = preamble
        OptionParser.__init__(self, usage, option_list, option_class, version,
                              conflict_handler, description, formatter,
                              False, prog, epilog)
        if add_help_option:
            self.add_option(
                '-?', '--help', dest='help', action='store_true',
                help='Shows this help text.')
        if version:
            self.remove_option('--version')
            self.add_option(
                '--version', dest='version', action='store_true',
                help='Shows the version of Swiftly.')
        self.stdout = stdout
        if not self.stdout:
            self.stdout = sys.stdout
        self.stderr = stderr
        if not self.stderr:
            self.stderr = sys.stderr
        self.commands = ''
        self.error_encountered = False

    def error(self, msg):
        self.error_encountered = True
        self.stderr.write(self.preamble)
        self.stderr.write(msg)
        self.stderr.write('\n')
        self.stderr.flush()

    def exit(self, status=0, msg=None):
        if msg:
            self.error(msg)
        sys.exit(status)

    def print_help(self, file=None):
        if not file:
            file = self.stdout
        OptionParser.print_help(self, file)
        if self.commands:
            file.write(self.commands)
        file.flush()

    def print_usage(self, file=None):
        if not file:
            file = self.stdout
        OptionParser.print_usage(self, file)
        file.flush()

    def print_version(self, file=None):
        if not file:
            file = self.stdout
        OptionParser.print_version(self, file)
        file.flush()


class CLI(object):
    """
    An instance of a command line interface client to Swift. After
    construction, a call to main() will execute the command line given. No args
    will output help information.

    :param args: The command line arguments to process.
    :param stdin: The file-like-object to read input from.
    :param stdout: The file-like-object to send output to.
    :param stderr: The file-like-object to send error output to.
    """

    def __init__(self, args=None, stdin=None, stdout=None, stderr=None):
        self.args = args
        if not self.args:
            self.args = sys.argv[1:]
        self.stdin = stdin
        if not self.stdin:
            self.stdin = sys.stdin
        self.stdout = stdout
        if not self.stdout:
            self.stdout = sys.stdout
        self.stderr = stderr
        if not self.stderr:
            self.stderr = sys.stderr
        self.start_time = time()
        self.clients = Queue()
        self.client_id = 0

        self._help_parser = _OptionParser(
            usage="""
Usage: %prog [main_options] help [command]

For help on [main_options] run %prog with no args.

Outputs help information for the given [command] or general help if no
[command] is given.""".strip(),
            stdout=self.stdout, stderr=self.stderr, preamble='help command: ')

        self._auth_parser = _OptionParser(
            usage="""
Usage: %prog [main_options] auth

For help on [main_options] run %prog with no args.

Outputs auth information.""".strip(),
            stdout=self.stdout, stderr=self.stderr, preamble='auth command: ')

        self._tempurl_parser = _OptionParser(
            usage="""
Usage: %prog [main_options] tempurl <method> <path> [seconds]

For help on [main_options] run %prog with no args.

Outputs a TempURL using the information given.
The <path> should be to an object or object-prefix.
[seconds] defaults to 3600""".strip(),
            stdout=self.stdout, stderr=self.stderr,
            preamble='tempurl command: ')

        self._head_parser = _OptionParser(
            usage="""
Usage: %prog [main_options] head [options] [path]

For help on [main_options] run %prog with no args.

Outputs the resulting headers from a HEAD request of the [path] given. If no
[path] is given, a HEAD request on the account is performed.""".strip(),
            stdout=self.stdout, stderr=self.stderr, preamble='head command: ')
        self._head_parser.add_option(
            '-h', '--header', dest='header', action='append',
            metavar='HEADER:VALUE',
            help='Add a header to the request. This can be used multiple '
                 'times for multiple headers. Examples: '
                 '-hif-match:6f432df40167a4af05ca593acc6b3e4c -h '
                 '"If-Modified-Since: Wed, 23 Nov 2011 20:03:38 GMT"')
        self._head_parser.add_option(
            '-q', '--query', dest='query', action='append',
            metavar='NAME[=VALUE]',
            help='Add a query parameter to the request. This can be used '
                 'multiple times for multiple query parameters. Example: '
                 '-qmultipart-manifest=get')
        self._head_parser.add_option(
            '--ignore-404', dest='ignore_404', action='store_true',
            help='Ignores 404 Not Found responses. Nothing will be output, '
                 'but the exit code will be 0 instead of 1.')

        self._get_parser = _OptionParser(
            usage="""
Usage: %prog [main_options] get [options] [path]

For help on [main_options] run %prog with no args.

Outputs the resulting contents from a GET request of the [path] given. If no
[path] is given, a GET request on the account is performed.""".strip(),
            stdout=self.stdout, stderr=self.stderr, preamble='get command: ')
        self._get_parser.add_option(
            '--headers', dest='headers', action='store_true',
            help='Output headers as well as the contents.')
        self._get_parser.add_option(
            '-h', '--header', dest='header', action='append',
            metavar='HEADER:VALUE',
            help='Add a header to the request. This can be used multiple '
                 'times for multiple headers. Examples: '
                 '-hif-match:6f432df40167a4af05ca593acc6b3e4c -h '
                 '"If-Modified-Since: Wed, 23 Nov 2011 20:03:38 GMT"')
        self._get_parser.add_option(
            '-q', '--query', dest='query', action='append',
            metavar='NAME[=VALUE]',
            help='Add a query parameter to the request. This can be used '
                 'multiple times for multiple query parameters. Example: '
                 '-qmultipart-manifest=get')
        self._get_parser.add_option(
            '-l', '--limit', dest='limit',
            help='For account and container GETs, this limits the number of '
                 'items returned. Without this option, all items are '
                 'returned, even if it requires several backend requests to '
                 'the gather the information.')
        self._get_parser.add_option(
            '-d', '--delimiter', dest='delimiter',
            help='For account and container GETs, this sets the delimiter for '
                 'the listing retrieved. For example, a container with the '
                 'objects "abc/one", "abc/two", "xyz" and a delimiter of "/" '
                 'would return "abc/" and "xyz". Using the same delimiter, '
                 'but with a prefix of "abc/", would return "abc/one" and '
                 '"abc/two".')
        self._get_parser.add_option(
            '-p', '--prefix', dest='prefix',
            help='For account and container GETs, this sets the prefix for '
                 'the listing retrieved; the items returned will all match '
                 'the PREFIX given.')
        self._get_parser.add_option(
            '-m', '--marker', dest='marker',
            help='For account and container GETs, this sets the marker for '
                 'the listing retrieved; the items returned will begin with '
                 'the item just after the MARKER given (note: the marker does '
                 'not have to actually exist).')
        self._get_parser.add_option(
            '-e', '--end-marker', dest='end_marker', metavar='MARKER',
            help='For account and container GETs, this sets the end-marker '
                 'for the listing retrieved; the items returned will stop '
                 'with the item just before the MARKER given (note: the '
                 'marker does not have to actually exist).')
        self._get_parser.add_option(
            '-f', '--full', dest='full', action="store_true",
            help='For account and container GETs, this will output additional '
                 'information about each item. For an account GET, the items '
                 'output will be bytes-used, object-count, and '
                 'container-name. For a container GET, the items output will '
                 'be bytes-used, last-modified-time, etag, content-type, and '
                 'object-name. Note that this is mostly useless for --cdn '
                 'queries; for those it is best to just use --raw and parse '
                 'the results yourself (perhaps through "python -m '
                 'json.tool").')
        self._get_parser.add_option(
            '-r', '--raw', dest='raw', action="store_true",
            help='For account and container GETs, this will return the raw '
                 'JSON from the request. This will only do one request, even '
                 'if subsequent requests would be needed to return all items. '
                 'Use a subsequent call with --marker set to the last item '
                 'name returned to get the next batch of items, if desired.')
        self._get_parser.add_option(
            '--all-objects', dest='all_objects', action="store_true",
            help='For an account GET, performs a container GET --all-objects '
                 'for every container returned by the original account GET. '
                 'For a container GET, performs a GET for every object '
                 'returned by that original container GET. Any headers set '
                 'with --header options are sent for every GET. Any query '
                 'parameter set with --query is sent for every GET.')
        self._get_parser.add_option(
            '-o', '--output', dest='output', metavar='PATH',
            help='Indicates where to send the output; default is standard '
                 'output. If the PATH ends with a slash "/" and --all-objects '
                 'is used, each object will be placed in a similarly named '
                 'file inside the PATH given.')
        self._get_parser.add_option(
            '--ignore-404', dest='ignore_404', action='store_true',
            help='Ignores 404 Not Found responses. Nothing will be output, '
                 'but the exit code will be 0 instead of 1.')
        self._get_parser.add_option(
            '--sub-command', dest='sub_command', metavar='COMMAND',
            help='Sends the contents of each object downloaded as standard '
                 'input to the COMMAND given and outputs the command\'s '
                 'standard output as if it were the object\'s contents. This '
                 'can be useful in combination with --all-objects to filter '
                 'the objects before writing them to disk; for instance, '
                 'downloading logs, gunzipping them, grepping for a keyword, '
                 'and only storing matching lines locally (--sub-command '
                 '"gunzip | grep keyword" or --sub-command "zgrep keyword" if '
                 'your system has that).')

        self._put_parser = _OptionParser(
            usage="""
Usage: %prog [main_options] put [options] [path]

For help on [main_options] run %prog with no args.

Performs a PUT request on the <path> given. If the <path> is an object, the
contents for the object are read from standard input.

Special Note About Segmented Objects:

For object uploads exceeding the -s [size] (default: 5G) the object will be
uploaded in segments. At this time, auto-segmenting only works for objects
uploaded from source files -- objects sourced from standard input cannot exceed
the maximum object size for the cluster.

A segmented object is one that has its contents in several other objects. On
download, these other objects are concatenated into a single object stream.

Segmented objects can be useful to greatly exceed the maximum single object
size, speed up uploading large objects with concurrent segment uploading, and
provide the option to replace, insert, and delete segments within a whole
object without having to alter or reupload any of the other segments.

The main object of a segmented object is called the "manifest object". This
object just has an X-Object-Manifest header that points to another path where
the segments for the object contents are stored. For Swiftly, this header value
is auto-generated as the same name as the manifest object, but with "_segments"
added to the container name. This keeps the segments out of the main container
listing, which is often useful.

By default, Swift's dynamic large object support is used since it was
implemented first. However, if you prefix the [size] with an 's', as in '-s
s1048576' Swiftly will use static large object support. These static large
objects are very similar as described above, except the manifest contains a
static list of the object segments. For more information on the tradeoffs, see
http://greg.brim.net/post/2013/05/16/1834.html""".strip(),
            stdout=self.stdout, stderr=self.stderr, preamble='put command: ')
        self._put_parser.add_option(
            '-h', '--header', dest='header', action='append',
            metavar='HEADER:VALUE',
            help='Add a header to the request. This can be used multiple '
                 'times for multiple headers. Examples: '
                 '-hx-object-meta-color:blue -h "Content-Type: text/html"')
        self._put_parser.add_option(
            '-q', '--query', dest='query', action='append',
            metavar='NAME[=VALUE]',
            help='Add a query parameter to the request. This can be used '
                 'multiple times for multiple query parameters. Example: '
                 '-qmultipart-manifest=get')
        self._put_parser.add_option(
            '-i', '--input', dest='input_', metavar='PATH',
            help='Indicates where to read the contents from; default is '
                 'standard input. If the PATH is a directory, all files in '
                 'the directory will be uploaded as similarly named objects '
                 'and empty directories will create text/directory marker '
                 'objects.')
        self._put_parser.add_option(
            '-I', dest='INPUT_', action='store_true',
            help='Since account and container PUTs do not normally take '
                 'input, you must specify this option if you wish them to '
                 'read from the input specified by -i (or the default '
                 'standard input). This is useful with '
                 '-qextract-archive=<format> bulk upload requests. For '
                 'example: tar zc . | swiftly put -qextract-archive=tar.gz -I '
                 'container')
        self._put_parser.add_option(
            '-n', '--newer', dest='newer', action='store_true',
            help='For PUTs with an --input option, first performs a HEAD on '
                 'the object and compares the X-Object-Meta-Mtime header with '
                 'the modified time of the PATH obtained from the --input '
                 'option and then PUTs the object only if the local time is '
                 'newer. When the --input PATH is a directory, this offers an '
                 'easy way to upload only the newer files since the last '
                 'upload (at the expense of HEAD requests). NOTE THAT THIS '
                 'WILL NOT UPLOAD CHANGED FILES THAT DO NOT HAVE A NEWER '
                 'LOCAL MODIFIED TIME! NEWER does not mean DIFFERENT.')
        self._put_parser.add_option(
            '-d', '--different', dest='different', action='store_true',
            help='For PUTs with an --input option, first performs a HEAD on '
                 'the object and compares the X-Object-Meta-Mtime header with '
                 'the modified time of the PATH obtained from the --input '
                 'option and then PUTs the object only if the local time is '
                 'different. It will also check the local and remote sizes '
                 'and PUT if they differ. ETag/MD5sum checking are not done '
                 '(an option may be provided in the future) since this is '
                 'usually much more disk intensive. When the --input PATH is '
                 'a directory, this offers an easy way to upload only the '
                 'differing files since the last upload (at the expense of '
                 'HEAD requests). NOTE THAT THIS CAN UPLOAD OLDER FILES OVER '
                 'NEWER ONES! DIFFERENT does not mean NEWER.')
        self._put_parser.add_option(
            '-e', '--empty', dest='empty', action='store_true',
            help='Indicates a zero-byte object should be PUT.')
        self._put_parser.add_option(
            '-s', '--segment-size', dest='segment_size', metavar='BYTES',
            help='Indicates the maximum size of an object before uploading it '
                 'as a segmented object. See full help text for more '
                 'information.')

        self._post_parser = _OptionParser(
            usage="""
Usage: %prog [main_options] post [options] [path]

For help on [main_options] run %prog with no args.

Issues a POST request of the [path] given. If no [path] is given, a POST
request on the account is performed.""".strip(),
            stdout=self.stdout, stderr=self.stderr, preamble='post command: ')
        self._post_parser.add_option(
            '-h', '--header', dest='header', action='append',
            metavar='HEADER:VALUE',
            help='Add a header to the request. This can be used multiple '
                 'times for multiple headers. Examples: '
                 '-hx-object-meta-color:blue -h "Content-Type: text/html"')
        self._post_parser.add_option(
            '-q', '--query', dest='query', action='append',
            metavar='NAME[=VALUE]',
            help='Add a query parameter to the request. This can be used '
                 'multiple times for multiple query parameters. Example: '
                 '-qmultipart-manifest=get')
        self._post_parser.add_option(
            '-i', '--input', dest='input_', metavar='PATH',
            help='Indicates where to read the POST request body from; '
                 'default is standard input. This is not normally used with '
                 'Swift POST requests, so you must also specify -I if you '
                 'want the body sent.')
        self._post_parser.add_option(
            '-I', dest='INPUT_', action='store_true',
            help='Since Swift POSTs do not normally take input, you must '
                 'specify this option if you wish them to read from the input '
                 'specified by -i (or the default standard input). This is '
                 'not known to be useful for anything yet.')

        self._delete_parser = _OptionParser(
            usage="""
Usage: %prog [main_options] delete [options] [path]

For help on [main_options] run %prog with no args.

Issues a DELETE request of the [path] given.""".strip(),
            stdout=self.stdout, stderr=self.stderr,
            preamble='delete command: ')
        self._delete_parser.add_option(
            '-h', '--header', dest='header', action='append',
            metavar='HEADER:VALUE',
            help='Add a header to the request. This can be used multiple '
                 'times for multiple headers. Examples: '
                 '-hx-some-header:some-value -h "X-Some-Other-Header: Some '
                 'other value"')
        self._delete_parser.add_option(
            '-q', '--query', dest='query', action='append',
            metavar='NAME[=VALUE]',
            help='Add a query parameter to the request. This can be used '
                 'multiple times for multiple query parameters. Example: '
                 '-qmultipart-manifest=get')
        self._delete_parser.add_option(
            '-i', '--input', dest='input_', metavar='PATH',
            help='Indicates where to read the DELETE request body from; '
                 'default is standard input. This is not normally used with '
                 'DELETE requests, so you must also specify -I if you want '
                 'the body sent.')
        self._delete_parser.add_option(
            '-I', dest='INPUT_', action='store_true',
            help='Since DELETEs do not normally take input, you must specify '
                 'this option if you wish them to read from the input '
                 'specified by -i (or the default standard input). This is '
                 'useful with -qbulk-delete requests. For example: swiftly '
                 'delete -qbulk-delete -Ii <my-bulk-deletes-file>')
        self._delete_parser.add_option(
            '--recursive', dest='recursive', action='store_true',
            help='Normally a delete for a non-empty container will error with '
                 'a 409 Conflict; --recursive will first delete all objects '
                 'in a container and then delete the container itself. For an '
                 'account delete, all containers and objects will be deleted '
                 '(requires the --yes-i-mean-empty-the-account option).')
        self._delete_parser.add_option(
            '--yes-i-mean-empty-the-account', dest='yes_empty_account',
            action='store_true',
            help='Required when issuing a delete directly on an account with '
                 'the --recursive option. This will delete all containers and '
                 'objects in the account without deleting the account itself, '
                 'leaving an empty account. THERE IS NO GOING BACK!')
        self._delete_parser.add_option(
            '--yes-i-mean-delete-the-account', dest='yes_delete_account',
            action='store_true',
            help='Required when issuing a delete directly on an account. Some '
                 'Swift clusters do not support this. Those that do will mark '
                 'the account as deleted and immediately begin removing the '
                 'objects from the cluster in the backgound. THERE IS NO '
                 'GOING BACK!')
        self._delete_parser.add_option(
            '--ignore-404', dest='ignore_404', action='store_true',
            help='Ignores 404 Not Found responses; the exit code will be 0 '
                 'instead of 1.')

        self._main_parser = _OptionParser(
            version=VERSION,
            usage="""
Usage: %prog [options] <command> [command_options] [args]

NOTE: Be sure any names given are url encoded if necessary. For instance, an
object named 4&4.txt must be given as 4%264.txt.""".strip(),
            stdout=self.stdout, stderr=self.stderr)
        self._main_parser.add_option(
            '-h', dest='help', action='store_true',
            help='Shows this help text.')
        self._main_parser.add_option(
            '-A', '--auth-url', dest='auth_url',
            default=environ.get('SWIFTLY_AUTH_URL', ''), metavar='URL',
            help='URL to auth system, example: '
                 'http://127.0.0.1:8080/auth/v1.0 You can also set this with '
                 'the environment variable SWIFTLY_AUTH_URL.')
        self._main_parser.add_option(
            '-U', '--auth-user', dest='auth_user',
            default=environ.get('SWIFTLY_AUTH_USER', ''), metavar='USER',
            help='User name for auth system, example: test:tester You can '
                 'also set this with the environment variable '
                 'SWIFTLY_AUTH_USER.')
        self._main_parser.add_option(
            '-K', '--auth-key', dest='auth_key',
            default=environ.get('SWIFTLY_AUTH_KEY', ''), metavar='KEY',
            help='Key for auth system, example: testing You can also set this '
                 'with the environment variable SWIFTLY_AUTH_KEY.')
        self._main_parser.add_option(
            '-T', '--auth-tenant', dest='auth_tenant',
            default=environ.get('SWIFTLY_AUTH_TENANT', ''), metavar='TENANT',
            help='Tenant name for auth system, example: test You can '
                 'also set this with the environment variable '
                 'SWIFTLY_AUTH_TENANT. If not specified and needed, the auth '
                 'user will be used.')
        self._main_parser.add_option(
            '--auth-methods', dest='auth_methods',
            default=environ.get('SWIFTLY_AUTH_METHODS', ''),
            metavar='name[,name[...]]',
            help='Auth methods to use with the auth system, example: '
                 'auth2key,auth2password,auth2password_force_tenant,auth1 You '
                 'can also set this with the environment variable '
                 'SWIFTLY_AUTH_METHODS. Swiftly will try to determine the '
                 'best order for you; but if you notice it keeps making '
                 'useless auth attempts and that drives you crazy, you can '
                 'override that here. All the available auth methods are '
                 'listed in the example.')
        self._main_parser.add_option(
            '--region', dest='region',
            default=environ.get('SWIFTLY_REGION', ''), metavar='VALUE',
            help='Region to use, if supported by auth, example: DFW You can '
                 'also set this with the environment variable SWIFTLY_REGION. '
                 'Default: default region specified by the auth response.')
        self._main_parser.add_option(
            '-D', '--direct', dest='direct',
            default=environ.get('SWIFTLY_DIRECT', ''), metavar='PATH',
            help='Uses direct connect method to access Swift. Requires access '
                 'to rings and backend servers. The PATH is the account '
                 'path, example: /v1/AUTH_test You can also set this with the '
                 'environment variable SWIFTLY_DIRECT.')
        self._main_parser.add_option(
            '-P', '--proxy', dest='proxy',
            default=environ.get('SWIFTLY_PROXY', ''), metavar='URL',
            help='Uses the given proxy URL. You can also set this with the '
                 'environment variable SWIFTLY_PROXY.')
        self._main_parser.add_option(
            '-S', '--snet', dest='snet', action='store_true',
            default=environ.get('SWIFTLY_SNET', 'false').lower() == 'true',
            help='Prepends the storage URL host name with "snet-". Mostly '
                 'only useful with Rackspace Cloud Files and Rackspace '
                 'ServiceNet. You can also set this with the environment '
                 'variable SWIFTLY_SNET (set to "true" or "false").')
        self._main_parser.add_option(
            '-R', '--retries', dest='retries',
            default=int(environ.get('SWIFTLY_RETRIES', 4)), metavar='INTEGER',
            help='Indicates how many times to retry the request on a server '
                 'error. Default: 4. You can also set this with the '
                 'environment variable SWIFTLY_RETRIES.')
        self._main_parser.add_option(
            '-C', '--cache-auth', dest='cache_auth', action='store_true',
            default=(
                environ.get('SWIFTLY_CACHE_AUTH', 'false').lower() == 'true'),
            help='If set true, the storage URL and auth token are cached in '
                 '/tmp/<user>.swiftly for reuse. If there are already cached '
                 'values, they are used without authenticating first. You can '
                 'also set this with the environment variable '
                 'SWIFTLY_CACHE_AUTH (set to "true" or "false").')
        self._main_parser.add_option(
            '--cdn', dest='cdn', action='store_true',
            help='Directs requests to the CDN management interface.')
        self._main_parser.add_option(
            '--concurrency', dest='concurrency', default='1',
            metavar='INTEGER',
            help='Sets the the number of actions that can be done '
                 'simultaneously when possible (currently requires using '
                 'Eventlet too). Default: 1')
        self._main_parser.add_option(
            '--eventlet', dest='eventlet', action='store_true',
            help='Enables Eventlet, if installed. This is disabled by default '
                 'if Eventlet is not installed or is less than version 0.11.0 '
                 '(because older Swiftly+Eventlet tends to use excessive CPU.')
        self._main_parser.add_option(
            '--no-eventlet', dest='no_eventlet', action='store_true',
            help='Disables Eventlet, even if installed and version 0.11.0 or '
                 'greater.')
        self._main_parser.add_option(
            '-v', '--verbose', dest='verbose', action='store_true',
            help='Causes output to standard error indicating actions being '
                 'taken. These output lines will be prefixed with VERBOSE and '
                 'will also include the number of seconds elapsed since '
                 'Swiftly started.')
        self._main_parser.commands = 'Commands:\n'
        for key in sorted(dir(self)):
            attr = getattr(self, key)
            if getattr(attr, '__is_command__', False):
                lines = getattr(self, key + '_parser').get_usage().split('\n')
                main_line = '  ' + lines[0].split(']', 1)[1].strip()
                for x in xrange(4):
                    lines.pop(0)
                for x, line in enumerate(lines):
                    if not line:
                        lines = lines[:x]
                        break
                if len(main_line) < 24:
                    initial_indent = main_line + ' ' * (24 - len(main_line))
                else:
                    self._main_parser.commands += main_line + '\n'
                    initial_indent = ' ' * 24
                self._main_parser.commands += textwrap.fill(
                    ' '.join(lines), width=79, initial_indent=initial_indent,
                    subsequent_indent=' ' * 24) + '\n'
        self._main_options = None

    def main(self):
        """
        Process the command line given in the constructor.
        """
        self._main_parser.disable_interspersed_args()
        try:
            self._main_options, args = self._main_parser.parse_args(self.args)
        except UnboundLocalError:
            # Happens sometimes with an error handler that doesn't raise its
            # own exception. We'll catch the error below.
            pass
        self._main_parser.enable_interspersed_args()
        if self._main_parser.error_encountered:
            return 1
        if self._main_options.version:
            self._main_parser.print_version()
            return 1
        if not args or self._main_options.help:
            self._main_parser.print_help()
            return 1
        func = getattr(self, '_' + args[0], None)
        if not func or not getattr(func, '__is_command__', False):
            self._main_parser.print_help()
            return 1
        if not getattr(func, '__is_client_command__', False):
            rv = func(args[1:])
        else:
            client = self._get_client()
            if not client:
                self._main_parser.print_help()
                return 1
            self._put_client(client)
            rv = func(args[1:])
        return _get_return_code(rv)

    def _verbose(self, msg, *args):
        if self._main_options.verbose:
            try:
                self.stderr.write(
                    'VERBOSE %.02f ' % (time() - self.start_time))
                self.stderr.write(msg % args)
            except TypeError, err:
                raise TypeError('%s: %r %d args' % (err, msg, len(args)))
            self.stderr.write('\n')
            self.stderr.flush()

    def _get_client(self):
        client = None
        try:
            client = self.clients.get(block=False)
        except Empty:
            pass
        if not client:
            eventlet = None
            self.client_id += 1
            if self._main_options.eventlet:
                eventlet = True
            if self._main_options.no_eventlet:
                eventlet = False
            if self._main_options.direct:
                client = Client(
                    swift_proxy=True,
                    swift_proxy_storage_path=self._main_options.direct,
                    retries=int(self._main_options.retries),
                    eventlet=eventlet,
                    region=self._main_options.region,
                    verbose=self._verbose,
                    verbose_id=str(self.client_id))
            elif all([self._main_options.auth_url,
                      self._main_options.auth_user,
                      self._main_options.auth_key]):
                cache_path = None
                if self._main_options.cache_auth:
                    cache_path = \
                        '/tmp/%s.swiftly' % environ.get('USER', 'user')
                client = Client(
                    auth_url=self._main_options.auth_url,
                    auth_user=self._main_options.auth_user,
                    auth_key=self._main_options.auth_key,
                    auth_tenant=self._main_options.auth_tenant,
                    auth_methods=self._main_options.auth_methods,
                    proxy=self._main_options.proxy,
                    snet=self._main_options.snet,
                    retries=int(self._main_options.retries),
                    cache_path=cache_path,
                    eventlet=eventlet,
                    region=self._main_options.region,
                    verbose=self._verbose,
                    verbose_id=str(self.client_id))
        return client

    def _put_client(self, client):
        self.clients.put(client)

    @contextmanager
    def _with_client(self):
        client = self._get_client()
        if not client:
            raise Exception('No client!')
        yield client
        self._put_client(client)

    def _command_line_headers(self, options_list):
        headers = {}
        if options_list:
            for h in options_list:
                v = ''
                if ':' in h:
                    h, v = h.split(':', 1)
                headers[h.strip().lower()] = v.strip()
        return headers

    def _command_line_query_parameters(self, options_list):
        query_parameters = {}
        if options_list:
            for n in options_list:
                v = ''
                if '=' in n:
                    n, v = n.split('=', 1)
                query_parameters[n.strip()] = v.strip()
        return query_parameters

    def _output_headers(self, headers, mute=None, stdout=None):
        if headers:
            if not mute:
                mute = []
            if not stdout:
                stdout = self.stdout
            fmt = '%%-%ds %%s\n' % (min(25, max(len(k) for k in headers)) + 1)
            for key in sorted(headers):
                if key in mute:
                    continue
                stdout.write(fmt % (key.title() + ':', headers[key]))
            stdout.flush()

    @_command
    def _help(self, args):
        try:
            options, args = self._help_parser.parse_args(args)
        except UnboundLocalError:
            # Happens sometimes with an error handler that doesn't raise its
            # own exception. We'll catch the error below.
            pass
        if self._help_parser.error_encountered:
            return 1
        if not args or options.help:
            self._main_parser.print_help()
            return 1
        func = getattr(self, '_' + args[0], None)
        if not func or not getattr(func, '__is_command__', False):
            self._main_parser.print_help()
            return 1
        getattr(self, '_' + args[0] + '_parser').print_help()
        return 1

    @_client_command
    def _auth(self, args):
        try:
            options, args = self._auth_parser.parse_args(args)
        except UnboundLocalError:
            # Happens sometimes with an error handler that doesn't raise its
            # own exception. We'll catch the error below.
            pass
        if self._auth_parser.error_encountered:
            return 1
        if args or options.help:
            self._auth_parser.print_help()
            return 1
        if self._main_options.direct:
            with self._with_client() as client:
                self.stdout.write('Direct Storage Path: ')
                self.stdout.write(client.storage_path)
                self.stdout.write('\n')
                self.stdout.flush()
            return 0
        with self._with_client() as client:
            client.auth()
            self.stdout.write('Storage URL: ')
            self.stdout.write(client.storage_url)
            self.stdout.write('\n')
            if client.cdn_url:
                self.stdout.write('CDN Management URL: ')
                self.stdout.write(client.cdn_url)
                self.stdout.write('\n')
            self.stdout.write('Auth Token: ')
            self.stdout.write(client.auth_token)
            self.stdout.write('\n')
            if client.regions:
                self.stdout.write('Regions: ')
                self.stdout.write(' '.join(client.regions))
                self.stdout.write('\n')
                self.stdout.flush()
            if client.regions_default:
                self.stdout.write('Default Region: ')
                self.stdout.write(client.regions_default)
                self.stdout.write('\n')
                self.stdout.flush()
        return 0

    @_client_command
    def _tempurl(self, args):
        try:
            options, args = self._tempurl_parser.parse_args(args)
        except UnboundLocalError:
            # Happens sometimes with an error handler that doesn't raise its
            # own exception. We'll catch the error below.
            pass
        if self._tempurl_parser.error_encountered:
            return 1
        if not args or len(args) < 2 or options.help:
            self._tempurl_parser.print_help()
            return 1
        method = args.pop(0)
        path = args.pop(0).lstrip('/')
        seconds = int(args.pop(0)) if args else 3600
        if args:
            self._tempurl_parser.print_help()
            return 1
        if '/' not in path:
            self._tempurl_parser.print_help()
            return 1
        with self._with_client() as client:
            status, reason, headers, contents = client.head_account()
            if status // 100 != 2:
                self.stderr.write('%s %s\n' % (status, reason))
                self.stderr.flush()
                return 1
            key = headers.get('x-account-meta-temp-url-key')
            if not key:
                self.stderr.write(
                    'There is no X-Account-Meta-Temp-URL-Key set for this '
                    'account.\n')
                self.stderr.flush()
                return 1
            url = client.storage_url + '/' + path
            self.stdout.write(generate_temp_url(method, url, seconds, key))
            self.stdout.write('\n')
            self.stdout.flush()
        return 0

    @_client_command
    def _head(self, args):
        try:
            options, args = self._head_parser.parse_args(args)
        except UnboundLocalError:
            # Happens sometimes with an error handler that doesn't raise its
            # own exception. We'll catch the error below.
            pass
        if self._head_parser.error_encountered:
            return 1
        if options.help:
            self._head_parser.print_help()
            return 1
        hdrs = self._command_line_headers(options.header)
        options.query = self._command_line_query_parameters(options.query)
        status, reason, headers, contents = 0, 'Unknown', {}, ''
        mute = []
        if not args:
            with self._with_client() as client:
                status, reason, headers, contents = client.head_account(
                    headers=hdrs, query=options.query,
                    cdn=self._main_options.cdn)
            mute.extend(MUTED_ACCOUNT_HEADERS)
        elif len(args) == 1:
            path = args[0].lstrip('/')
            with self._with_client() as client:
                if '/' not in path.rstrip('/'):
                    status, reason, headers, contents = client.head_container(
                        path.rstrip('/'), headers=hdrs, query=options.query,
                        cdn=self._main_options.cdn)
                    mute.extend(MUTED_CONTAINER_HEADERS)
                else:
                    status, reason, headers, contents = client.head_object(
                        *path.split('/', 1), headers=hdrs, query=options.query,
                        cdn=self._main_options.cdn)
                    mute.extend(MUTED_OBJECT_HEADERS)
        else:
            self._head_parser.print_help()
            return 1
        if status // 100 != 2:
            if status == 404 and options.ignore_404:
                return 0
            self.stderr.write('%s %s\n' % (status, reason))
            self.stderr.flush()
            return 1
        self._output_headers(headers, mute)
        return 0

    def _get_recursive_helper(self, args, stdout=None):
        rv = self._get(args, stdout=stdout)
        if rv:
            self.stderr.write('aborting after error with %s\n' % args[0])
            self.stderr.flush()
            return rv
        return 0

    @_client_command
    def _get(self, args, stdout=None):
        try:
            options, args = self._get_parser.parse_args(args)
        except UnboundLocalError:
            # Happens sometimes with an error handler that doesn't raise its
            # own exception. We'll catch the error below.
            pass
        if self._get_parser.error_encountered:
            return 1
        if len(args) > 1 or options.help:
            self._get_parser.print_help()
            return 1
        hdrs = self._command_line_headers(options.header)
        options.query = self._command_line_query_parameters(options.query)
        if not stdout:
            stdout = self.stdout
        if options.output:
            if options.output.endswith('/'):
                if not exists(options.output):
                    makedirs(options.output)
            else:
                stdout = open(options.output, 'wb')
        status, reason, headers, contents = 0, 'Unknown', {}, ''
        path = ''
        if args:
            path = args[0].lstrip('/')
        if not path or '/' not in path.rstrip('/'):
            path = path.rstrip('/')
            if not path:
                mute = MUTED_ACCOUNT_HEADERS
            else:
                mute = MUTED_CONTAINER_HEADERS
            limit = options.limit or 10000
            delimiter = options.delimiter
            prefix = options.prefix
            marker = options.marker
            end_marker = options.end_marker
            with self._with_client() as client:
                if not path:
                    status, reason, headers, contents = client.get_account(
                        headers=hdrs, limit=limit, marker=marker,
                        end_marker=end_marker, query=options.query,
                        cdn=self._main_options.cdn)
                else:
                    status, reason, headers, contents = client.get_container(
                        path, headers=hdrs, limit=limit, delimiter=delimiter,
                        prefix=prefix, marker=marker, end_marker=end_marker,
                        query=options.query, cdn=self._main_options.cdn)
            if status // 100 != 2:
                if status == 404 and options.ignore_404:
                    return 0
                self.stderr.write('%s %s\n' % (status, reason))
                self.stderr.flush()
                if hasattr(contents, 'read'):
                    contents.read()
                return 1
            if options.headers and not options.all_objects:
                self._output_headers(headers, mute, stdout=stdout)
                stdout.write('\n')
                stdout.flush()
            conc_value = 1
            if options.output and options.output.endswith('/'):
                conc_value = int(self._main_options.concurrency)
            elif options.all_objects:
                self._verbose(
                    'Disabling some concurrency because of single stream '
                    'output.')
            conc = Concurrency(conc_value)
            while contents:
                if options.all_objects:
                    for item in contents:
                        if 'name' in item:
                            subargs = \
                                [path + '/' + item['name'].encode('utf8')]
                            if options.header:
                                for h in options.header:
                                    subargs.append('-h')
                                    subargs.append(h)
                            if options.output and options.output.endswith('/'):
                                outpath = options.output + \
                                    item['name'].encode('utf8')
                                dirpath = dirname(outpath)
                                if not exists(dirpath):
                                    makedirs(dirpath)
                                elif not isdir(dirpath):
                                    self.stderr.write(
                                        '%s conflict; file and directory\n' %
                                        dirpath)
                                    self.stderr.flush()
                                    return 1
                                subargs.append('--all-objects')
                                subargs.append('-o')
                                if not path:
                                    subargs.append(outpath + '/')
                                else:
                                    subargs.append(outpath)
                            subargs.append('--ignore-404')
                            if options.sub_command:
                                subargs.append('--sub-command')
                                subargs.append(options.sub_command)
                            for rv in conc.get_results().values():
                                if rv:
                                    conc.join()
                                    return rv
                            if not options.output or \
                                    not options.output.endswith('/'):
                                conc.spawn(subargs[0],
                                           self._get_recursive_helper, subargs,
                                           stdout=stdout)
                            else:
                                conc.spawn(subargs[0],
                                           self._get_recursive_helper, subargs)
                elif options.raw:
                    json.dump(contents, stdout)
                    stdout.write('\n')
                    stdout.flush()
                    break
                else:
                    for item in contents:
                        if options.full:
                            if not path:
                                stdout.write('%13s %13s ' % (
                                    item.get('bytes', '-'),
                                    item.get('count', '-')))
                            else:
                                stdout.write('%13s %22s %32s %25s ' % (
                                    item.get('bytes', '-'),
                                    item.get('last_modified',
                                             '-')[:22].replace('T', ' '),
                                    item.get('hash', '-'),
                                    item.get('content_type', '-')))
                        stdout.write(item.get(
                            'name', item.get('subdir')).encode('utf8'))
                        stdout.write('\n')
                    stdout.flush()
                if options.limit:
                    break
                marker = \
                    contents[-1].get('name', contents[-1].get('subdir', ''))
                with self._with_client() as client:
                    if not path:
                        status, reason, headers, contents = client.get_account(
                            headers=hdrs, limit=limit, delimiter=delimiter,
                            prefix=prefix, end_marker=end_marker,
                            marker=marker, query=options.query,
                            cdn=self._main_options.cdn)
                    else:
                        status, reason, headers, contents = \
                            client.get_container(
                                path, headers=hdrs, limit=limit,
                                delimiter=delimiter, prefix=prefix,
                                end_marker=end_marker, marker=marker,
                                query=options.query,
                                cdn=self._main_options.cdn)
                if status // 100 != 2:
                    if status == 404 and options.ignore_404:
                        return 0
                    self.stderr.write('%s %s\n' % (status, reason))
                    self.stderr.flush()
                    if hasattr(contents, 'read'):
                        contents.read()
                    return 1
            conc.join()
            for rv in conc.get_results().values():
                if rv:
                    return rv
            return 0
        sub_command = None
        if options.sub_command:
            eventlet = None
            if self._main_options.eventlet:
                eventlet = True
            if self._main_options.no_eventlet:
                eventlet = False
            PIPE, Popen = _delayed_imports(eventlet)
            sub_command = Popen(options.sub_command, shell=True, stdin=PIPE,
                                stdout=stdout)
            stdout = sub_command.stdin
        with self._with_client() as client:
            status, reason, headers, contents = client.get_object(
                *path.split('/', 1), headers=hdrs, query=options.query,
                cdn=self._main_options.cdn)
            if status // 100 != 2:
                if status == 404 and options.ignore_404:
                    if sub_command:
                        stdout.close()
                        self._verbose('Waiting on sub-command for %s', path)
                        self._verbose(
                            'Sub-command returned %s with object %s',
                            sub_command.wait(), path)
                    return 0
                self.stderr.write('%s %s\n' % (status, reason))
                self.stderr.flush()
                if hasattr(contents, 'read'):
                    contents.read()
                if sub_command:
                    stdout.close()
                    self._verbose('Waiting on sub-command for %s', path)
                    self._verbose(
                        'Sub-command returned %s with object %s',
                        sub_command.wait(), path)
                return 1
            if options.headers:
                self._output_headers(headers, MUTED_OBJECT_HEADERS,
                                     stdout=stdout)
                stdout.write('\n')
            if headers.get('content-type') == 'text/directory' and \
                    headers.get('content-length') == '0':
                contents.read()
                if options.output and not options.output.endswith('/'):
                    stdout.close()
                    unlink(options.output)
                    makedirs(options.output)
            else:
                # TODO: Exception handling around these and other reads
                chunk = contents.read(CHUNK_SIZE)
                while chunk:
                    stdout.write(chunk)
                    chunk = contents.read(CHUNK_SIZE)
                stdout.flush()
        if options.output and not options.output.endswith('/'):
            stdout.close()
            mtime = 0
            if 'x-object-meta-mtime' in headers:
                mtime = float(headers['x-object-meta-mtime'])
            elif 'last-modified' in headers:
                mtime = mktime(strptime(headers['last-modified'],
                                        '%a, %d %b %Y %H:%M:%S %Z'))
            if mtime:
                utime(options.output, (mtime, mtime))
        if sub_command:
            stdout.close()
            self._verbose('Waiting on sub-command for %s', path)
            self._verbose(
                'Sub-command returned %s with object %s',
                sub_command.wait(), path)
        return 0

    def _put_recursive_helper(self, args, stdin=None):
        rv = self._put(args, stdin)
        if _get_return_code(rv):
            self.stderr.write(
                'aborting after error with %s\n' % args[0])
            self.stderr.flush()
            return rv
        return rv

    @_client_command
    def _put(self, args, stdin=None):
        try:
            options, args = self._put_parser.parse_args(args)
        except UnboundLocalError:
            # Happens sometimes with an error handler that doesn't raise its
            # own exception. We'll catch the error below.
            pass
        if self._put_parser.error_encountered:
            return 1
        if len(args) > 1 or options.help:
            self._put_parser.print_help()
            return 1
        options.query = self._command_line_query_parameters(options.query)
        if options.segment_size and options.segment_size[0].lower() == 's':
            options.static_segments = True
            options.segment_size = options.segment_size[1:]
        else:
            options.static_segments = False
        g5 = 5 * 1024 * 1024 * 1024
        try:
            options.segment_size = int(options.segment_size or g5)
        except ValueError:
            self.stderr.write(
                'invalid segment size %s\n' % options.segment_size)
            self.stderr.flush()
            return 1
        if options.segment_size < 1:
            self.stderr.write(
                'invalid segment size %s\n' % options.segment_size)
            self.stderr.flush()
            return 1
        if options.input_ and isdir(options.input_):
            if not args:
                self.stderr.write(
                    'Uploading a directory structure requires at least a '
                    'container name.\n')
                self.stderr.flush()
                return 1
            subargs = [args[0].split('/', 1)[0]]
            if options.header:
                for h in options.header:
                    subargs.append('-h')
                    subargs.append(h)
            rv = self._put(subargs)
            if _get_return_code(rv):
                self.stderr.write(
                    'aborting after error with %s\n' % subargs[0])
                self.stderr.flush()
                return rv
            ilen = len(options.input_)
            if not options.input_.endswith('/'):
                ilen += 1
            conc = Concurrency(int(self._main_options.concurrency))
            for (dirpath, dirnames, filenames) in walk(options.input_):
                if not dirnames and not filenames:
                    subargs = [args[0] + '/' + dirpath[ilen:]]
                    if options.header:
                        for h in options.header:
                            subargs.append('-h')
                            subargs.append(h)
                    subargs.append('-h')
                    subargs.append('content-type:text/directory')
                    subargs.append('-h')
                    subargs.append(
                        'x-object-meta-mtime:%d' % getmtime(options.input_))
                    subargs.append('-e')
                    for rv in conc.get_results().values():
                        if _get_return_code(rv):
                            conc.join()
                            return rv
                    conc.spawn(subargs[0], self._put_recursive_helper, subargs)
                else:
                    for fname in filenames:
                        if dirpath[ilen:]:
                            subargs = \
                                ['%s/%s/%s' % (args[0], dirpath[ilen:], fname)]
                        else:
                            subargs = ['%s/%s' % (args[0], fname)]
                        if options.header:
                            for h in options.header:
                                subargs.append('-h')
                                subargs.append(h)
                        subargs.append('-i')
                        subargs.append(pathjoin(dirpath, fname))
                        if options.newer:
                            subargs.append('-n')
                        if options.different:
                            subargs.append('-d')
                        for rv in conc.get_results().values():
                            if _get_return_code(rv):
                                conc.join()
                                return rv
                        conc.spawn(subargs[0], self._put_recursive_helper,
                                   subargs)
            conc.join()
            for rv in conc.get_results().values():
                if _get_return_code(rv):
                    return rv
            return 0
        path = args[0].lstrip('/') if args else ''
        hdrs = {}
        if not stdin:
            stdin = self.stdin
        if options.empty:
            hdrs['content-length'] = '0'
            stdin = ''
        elif options.INPUT_:
            if options.input_:
                stdin = open(options.input_, 'rb')
        elif options.input_ and not isdir(options.input_) and args:
            l_mtime = getmtime(options.input_)
            if (options.newer or options.different) and \
                    '/' in path.rstrip('/'):
                r_mtime = 0
                r_size = -1
                with self._with_client() as client:
                    status, reason, headers, contents = \
                        client.head_object(
                            *path.split('/', 1), query=options.query,
                            cdn=self._main_options.cdn)
                if status // 100 == 2:
                    try:
                        r_mtime = int(headers.get('x-object-meta-mtime', 0))
                    except ValueError:
                        pass
                    try:
                        r_size = int(headers.get('content-length', -1))
                    except ValueError:
                        pass
                if options.newer and l_mtime <= r_mtime:
                    return 0, path, r_size, headers.get('etag')
                if options.different and l_mtime == r_mtime and \
                        getsize(options.input_) == r_size:
                    return 0, path, r_size, headers.get('etag')
            hdrs['x-object-meta-mtime'] = '%d' % l_mtime
            size = getsize(options.input_)
            if size <= options.segment_size:
                stdin = open(options.input_, 'rb')
            else:
                stdin = ''
                hdrs['content-length'] = '0'
                prefix = '%s_segments/%s' % tuple(args[0].split('/', 1))
                prefix = '%s/%s/%s/' % (prefix, l_mtime, size)
                conc = Concurrency(int(self._main_options.concurrency))
                start = 0
                segment = 0
                while start < size:
                    subargs = [
                        '%s%08d' % (prefix, segment),
                        '-h',
                        'content-length:%s' % min(
                            size - start, options.segment_size)]
                    substdin = open(options.input_, 'rb')
                    substdin.seek(start)
                    for rv in conc.get_results().values():
                        if _get_return_code(rv):
                            conc.join()
                            return rv
                    conc.spawn(subargs[0], self._put_recursive_helper,
                               subargs, substdin)
                    segment += 1
                    start += options.segment_size
                conc.join()
                path2info = {}
                for rv in conc.get_results().values():
                    if _get_return_code(rv):
                        return rv
                    path2info[rv[1]] = rv[2:]
                if options.static_segments:
                    options.query['multipart-manifest'] = 'put'
                    stdin = json.dumps([
                        {'path': '/' + p, 'size_bytes': s, 'etag': e}
                        for p, (s, e) in sorted(path2info.iteritems())])
                    hdrs['content-type'] = 'application/json'
                    hdrs['content-length'] = str(len(stdin))
                else:
                    hdrs['x-object-manifest'] = prefix
        hdrs.update(self._command_line_headers(options.header))
        status, reason, headers, contents = 0, 'Unknown', {}, ''
        with self._with_client() as client:
            if not path.rstrip('/'):
                body = stdin if options.INPUT_ else ''
                status, reason, headers, contents = \
                    client.put_account(
                        headers=hdrs, query=options.query,
                        cdn=self._main_options.cdn, body=body)
            elif '/' not in path.rstrip('/'):
                body = stdin if options.INPUT_ else ''
                status, reason, headers, contents = \
                    client.put_container(
                        path.rstrip('/'), headers=hdrs, query=options.query,
                        cdn=self._main_options.cdn, body=body)
            else:
                c, o = path.split('/', 1)
                status, reason, headers, contents = \
                    client.put_object(
                        c, o, stdin, headers=hdrs, query=options.query,
                        cdn=self._main_options.cdn)
        if status // 100 != 2:
            self.stderr.write('%s %s\n' % (status, reason))
            if self._main_options.verbose and contents:
                self._verbose('< ' + repr(contents))
            self.stderr.flush()
            return 1
        if self._main_options.verbose and contents:
            self._verbose('< ' + repr(contents))
        if options.input_ and not isdir(options.input_):
            size = getsize(options.input_)
        else:
            size = int(hdrs.get('content-length') or 0)
        return 0, path, size, headers.get('etag')

    @_client_command
    def _post(self, args):
        try:
            options, args = self._post_parser.parse_args(args)
        except UnboundLocalError:
            # Happens sometimes with an error handler that doesn't raise its
            # own exception. We'll catch the error below.
            pass
        if self._post_parser.error_encountered:
            return 1
        if options.help:
            self._post_parser.print_help()
            return 1
        hdrs = self._command_line_headers(options.header)
        body = None
        if options.INPUT_:
            if options.input_:
                body = open(options.input_, 'rb')
            else:
                body = self.stdin
        status, reason, headers, contents = 0, 'Unknown', {}, ''
        if not args:
            with self._with_client() as client:
                status, reason, headers, contents = \
                    client.post_account(
                        headers=hdrs, query=options.query,
                        cdn=self._main_options.cdn, body=body)
        elif len(args) == 1:
            path = args[0].lstrip('/')
            with self._with_client() as client:
                if '/' not in path.rstrip('/'):
                    status, reason, headers, contents = \
                        client.post_container(
                            path.rstrip('/'), headers=hdrs,
                            query=options.query, cdn=self._main_options.cdn,
                            body=body)
                else:
                    status, reason, headers, contents = \
                        client.post_object(
                            *path.split('/', 1), headers=hdrs,
                            query=options.query, cdn=self._main_options.cdn,
                            body=body)
        else:
            self._post_parser.print_help()
            return 1
        if status // 100 != 2:
            self.stderr.write('%s %s\n' % (status, reason))
            if self._main_options.verbose and contents:
                self._verbose('< ' + repr(contents))
            self.stderr.flush()
            return 1
        if self._main_options.verbose and contents:
            self._verbose('< ' + repr(contents))
        return 0

    def _delete_recursive_helper(self, args):
        rv = self._delete(args)
        if rv:
            self.stderr.write('aborting after error with %s\n' % args[0])
            self.stderr.flush()
            return 1
        return 0

    @_client_command
    def _delete(self, args):
        try:
            options, args = self._delete_parser.parse_args(args)
        except UnboundLocalError:
            # Happens sometimes with an error handler that doesn't raise its
            # own exception. We'll catch the error below.
            pass
        if self._delete_parser.error_encountered:
            return 1
        if options.help:
            self._delete_parser.print_help()
            return 1
        options.query = self._command_line_query_parameters(options.query)
        hdrs = self._command_line_headers(options.header)
        status, reason, headers, contents = 0, 'Unknown', {}, ''
        if not args and options.INPUT_:
            body = self.stdin
            if options.input_:
                body = open(options.input_, 'rb')
            with self._with_client() as client:
                status, reason, headers, contents = \
                    client.delete_account(
                        headers=hdrs, query=options.query,
                        cdn=self._main_options.cdn, body=body)
        elif not args:
            if options.recursive and not options.yes_empty_account:
                self.stderr.write("""
A delete --recursive directly on an account requires the
--yes-i-mean-empty-the-account option as well.

All containers and objects in the account will be deleted, leaving an empty
account.

THERE IS NO GOING BACK!""".strip())
                self.stderr.write('\n')
                self.stderr.flush()
                return 1
            if not options.recursive and not options.yes_delete_account:
                self.stderr.write("""
A delete directly on an account requires the --yes-i-mean-delete-the-account
option as well.

Some Swift clusters do not support this.

Those that do will mark the account as deleted and immediately begin removing
the objects from the cluster in the backgound.

THERE IS NO GOING BACK!""".strip())
                self.stderr.write('\n')
                self.stderr.flush()
                return 1
            if options.yes_empty_account:
                marker = None
                while True:
                    with self._with_client() as client:
                        status, reason, headers, contents = \
                            client.get_account(
                                headers=hdrs, marker=marker,
                                query=options.query,
                                cdn=self._main_options.cdn)
                    if status // 100 != 2:
                        if status == 404 and options.ignore_404:
                            return 0
                        self.stderr.write('%s %s\n' % (status, reason))
                        self.stderr.flush()
                        return 1
                    if not contents:
                        break
                    for item in contents:
                        subargs = [item['name'], '--recursive']
                        if options.header:
                            for h in options.header:
                                subargs.append('-h')
                                subargs.append(h)
                        rv = self._delete(subargs)
                        if rv:
                            self.stderr.write(
                                'aborting after error with %s\n' %
                                item['name'])
                            self.stderr.flush()
                            return 1
                    marker = item['name']
                return 0
            if options.yes_delete_account:
                with self._with_client() as client:
                    yn = options.yes_delete_account
                    status, reason, headers, contents = \
                        client.delete_account(
                            headers=hdrs, query=options.query,
                            cdn=self._main_options.cdn,
                            yes_i_mean_delete_the_account=yn)
        elif len(args) == 1:
            body = None
            if options.INPUT_:
                body = self.stdin
                if options.input_:
                    body = open(options.input_, 'rb')
            path = args[0].lstrip('/')
            if '/' not in path.rstrip('/'):
                if options.recursive:
                    marker = None
                    while True:
                        with self._with_client() as client:
                            status, reason, headers, contents = \
                                client.get_container(
                                    path.rstrip('/'), headers=hdrs,
                                    marker=marker, query=options.query,
                                    cdn=self._main_options.cdn)
                        if status // 100 != 2:
                            if status == 404 and options.ignore_404:
                                return 0
                            self.stderr.write('%s %s\n' % (status, reason))
                            self.stderr.flush()
                            return 1
                        if not contents:
                            break
                        conc = Concurrency(int(self._main_options.concurrency))
                        for item in contents:
                            subargs = \
                                ['%s/%s' % (path.rstrip('/'), item['name'])]
                            if options.header:
                                for h in options.header:
                                    subargs.append('-h')
                                    subargs.append(h)
                            subargs.append('--ignore-404')
                            for rv in conc.get_results().values():
                                if rv:
                                    conc.join()
                                    return rv
                            conc.spawn(subargs[0],
                                       self._delete_recursive_helper, subargs)
                        marker = item['name']
                        conc.join()
                        for rv in conc.get_results().values():
                            if rv:
                                return rv
                    with self._with_client() as client:
                        status, reason, headers, contents = \
                            client.delete_container(
                                path.rstrip('/'), headers=hdrs,
                                query=options.query,
                                cdn=self._main_options.cdn, body=body)
                else:
                    with self._with_client() as client:
                        status, reason, headers, contents = \
                            client.delete_container(
                                path.rstrip('/'), headers=hdrs,
                                query=options.query,
                                cdn=self._main_options.cdn, body=body)
            else:
                with self._with_client() as client:
                    status, reason, headers, contents = \
                        client.delete_object(
                            *path.split('/', 1), headers=hdrs,
                            query=options.query, cdn=self._main_options.cdn,
                            body=body)
        else:
            self._delete_parser.print_help()
            return 1
        if status // 100 != 2:
            if status == 404 and options.ignore_404:
                return 0
            self.stderr.write('%s %s\n' % (status, reason))
            if self._main_options.verbose and contents:
                self._verbose('< ' + repr(contents))
            self.stderr.flush()
            return 1
        if self._main_options.verbose and contents:
            self._verbose('< ' + repr(contents))
        return 0
