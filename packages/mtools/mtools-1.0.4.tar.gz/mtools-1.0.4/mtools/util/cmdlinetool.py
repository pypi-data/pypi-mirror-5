import argparse
import sys
from mtools.version import __version__
import signal

class BaseCmdLineTool(object):
    """ Base class for any mtools command line tool. Adds --version flag and basic control flow. """

    def __init__(self):
        """ Constructor. Any inheriting class should add a description to the argparser and extend 
            it with additional arguments as needed.
        """
        # define argument parser and add version argument
        self.argparser = argparse.ArgumentParser()
        self.argparser.add_argument('--version', action='version', version="mtools version %s" % __version__)


    def run(self, arguments=None, get_unknowns=False):
        """ Init point to execute the script. If `arguments` string is given, will evaluate the 
            arguments, else evaluates sys.argv. Any inheriting class should extend the run method 
            (but first calling BaseCmdLineTool.run(self)).
        """
        # redirect PIPE signal to quiet kill script
        signal.signal(signal.SIGPIPE, signal.SIG_DFL)

        if get_unknowns:
            if arguments:
                self.args, self.unknown_args = self.argparser.parse_known_args(args=arguments.split())
            else:
                self.args, self.unknown_args = self.argparser.parse_known_args()
            self.args = vars(self.args)
        else:
            if arguments:
                self.args = vars(self.argparser.parse_args(args=arguments.split()))
            else:
                self.args = vars(self.argparser.parse_args())


class LogFileTool(BaseCmdLineTool):
    """ Base class for any mtools tool that acts on logfile(s). """

    def __init__(self, multiple_logfiles=False, stdin_allowed=True):
        """ Constructor. Adds logfile(s) and stdin option to the argument parser. """
        BaseCmdLineTool.__init__(self)

        self.multiple_logfiles = multiple_logfiles
        self.stdin_allowed = stdin_allowed

        arg_opts = {'action':'store', 'type':argparse.FileType('r')}

        if self.stdin_allowed:
            arg_opts['default'] = None
            arg_opts['nargs'] = '?'

        if self.multiple_logfiles:
            arg_opts['nargs'] = '*'
            arg_opts['help'] = 'logfile(s) to parse'
        else:
            arg_opts['help'] = 'logfile to parse'

        if not sys.stdin.isatty():
            arg_opts['const'] = sys.stdin
            arg_opts['action'] = 'store_const'
            del arg_opts['type']
            del arg_opts['nargs']

        self.argparser.add_argument('logfile', **arg_opts)


if __name__ == '__main__':
    tool = LogFileTool(multiple_logfiles=True, stdin_allowed=False)
    tool.run()
    print tool.args

