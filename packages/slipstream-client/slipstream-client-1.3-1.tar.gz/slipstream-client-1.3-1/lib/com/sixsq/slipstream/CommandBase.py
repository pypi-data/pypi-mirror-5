#!/usr/bin/env python
'''
This software code is made available "AS IS" without warranties of any kind.
You may NOT copy, display, modify or redistribute the software code or binaries
either by itself or as incorporated into your code, without the explicit
written permission from SixSq.  Your use of this software code is at your own
risk and you waive any claim against SixSq Sarl with respect to your use of
this software code. (c) 2011 SixSq Sarl. All rights reserved.

SixSq: http://www.sixsq.com
'''

from com.sixsq.slipstream import __version__
import com.sixsq.slipstream.util as util
import os
import sys
from optparse import OptionParser
from com.sixsq.slipstream.exceptions.Exceptions import NotYetSetException

if os.environ.has_key('SLIPSTREAM_HOME'):
    slipstreamHome = os.environ['SLIPSTREAM_HOME']
else:
    slipstreamHome = os.path.dirname(__file__)

slipstreamDirName = 'slipstream'
binDirName = 'bin'
repDirName = 'repository'
repDir = os.path.join(slipstreamDirName,repDirName)

def setEnv():

    newEnv = \
        '.' + os.pathsep + \
        os.path.join(slipstreamHome,'bin') + os.pathsep + \
        os.path.join(slipstreamHome,'httpurl2')
    if os.getenv('PYTHONPATH'):
        os.environ['PYTHONPATH'] = newEnv + os.pathsep + os.environ['PYTHONPATH']
    else:
        os.environ['PYTHONPATH'] = newEnv

def setPath():
    slipstreamHome = util.getInstallationLocation()
    sys.path.insert(1,'.')
    sys.path.append(os.path.join(slipstreamHome,'httplib2'))
    setEnv()

setPath()
    
try:
    from com.sixsq.slipstream.exceptions.Exceptions import NetworkError
    from com.sixsq.slipstream.exceptions.Exceptions import ServerError
    from com.sixsq.slipstream.exceptions.Exceptions import SecurityError
    from com.sixsq.slipstream.exceptions.Exceptions import AbortException
    from com.sixsq.slipstream.exceptions.Exceptions import ClientError
    from com.sixsq.slipstream.exceptions.Exceptions import TimeoutException
    util.slipstreamHome = slipstreamHome
except KeyboardInterrupt:
    print '\nExecution interrupted by the user... goodbye!'
    sys.exit(-1)

class CommandBase(object):
    
    def __init__(self, dummy):
        
        self.verboseLevel = 0
        self.options = None
        self.parser = None
        self._setParserAndParse()

        self.userProperties = {}
        self.userEnv = {}
        self.version = False
        self.noemail = False
        
        util.PRINT_TO_STDERR_ONLY = True

        util.printDetail("Calling: '%s'" % ' '.join(sys.argv), self.verboseLevel)
        self._callAndHandleErrorsForCommands(self.doWork.__name__)
        
        util.PRINT_TO_STDERR_ONLY = False

    def _setParserAndParse(self):
        self.parser = OptionParser()
        self.parser.add_option('-v', '--verbose', dest='verboseLevel',
                help='verbose level. Add more to get more details.',
                action='count', default=self.verboseLevel)
        self.parse()
        self.verboseLevel = self.options.verboseLevel

    def parse(self):
        pass

    def addIgnoreAbortOption(self):
        self.parser.add_option('--ignore-abort', dest='ignoreAbort',
                               help='by default, if the run abort flag is set, any \
                               call will return with an error. With this option values \
                               can be queried even if the abort flag is raised',
                               default=False, action='store_true')
    
    
    def _callAndHandleErrorsForCommands(self,methodName,*args,**kw):
        res = 0
        try:
            res = self.__class__.__dict__[methodName](self,*args,**kw)
        except KeyboardInterrupt:
            raise
        except NotYetSetException, ex:
            sys.stderr.writelines('\n%s\n' % str(ex))
            self._exit(1)
        except ValueError, ex:
            sys.stderr.writelines('\nError: %s\n' % str(ex))
            self._exit(3)
        except NetworkError, ex:
            sys.stderr.writelines('\nError: couldn\'t connect to the server. ')
            sys.stderr.writelines('Check network connection and server, and try again.')
            sys.stderr.writelines('\nError details: %s\n' % ex)
            self._exit(4)
        except SecurityError, ex:
            sys.stderr.writelines("\nSecurity Error: %s \n" % str(ex))
            self._exit(6)
        except ServerError, ex:
            sys.stderr.writelines("\nError: the following unexpected error was detected:\n   '%s'\n" % str(ex))
            self._exit(5)
        except TimeoutException, ex:
            sys.stderr.writelines('\nError: %s\n' % str(ex))
            self._exit(9)
        except AbortException, ex:
            sys.stderr.writelines('\nError: %s\n' % str(ex))
            self._exit(8)
        except ClientError, ex:
            sys.stderr.writelines("\nError: %s\n" % str(ex))
            self._exit(7)
        except SystemExit, ex:
            raise
        except Exception, ex:
            raise
        return res

    def _exit(self, code):
        if self.verboseLevel > 1:
            raise
        sys.exit(code)

    def _getHomeDirectory(self):
        return util.getHomeDirectory()

    def parseCommandLineProperties(self,value):
        bits = value.split('=')
        if len(bits) != 2:
            self.usageExit("Error: properties must be expressed as: <name>=<value>, got '%s'" % value)
            
        #Type convertions
        if bits[1].lower() == 'true':
            bits[1] = True
        elif bits[1].lower() == 'false':
            bits[1] = False
        else:
            if bits[1].isdigit():
                try:
                    bits[1] = int(bits[1])
                except ValueError:
                    pass

        self.userProperties[bits[0]] = bits[1]
        
        return bits[0],bits[1]

    def parseCommandLineEnv(self,value):
        bits = value.split('=')
        if len(bits) == 0 or len(bits) > 2:
            self.usageExit("Error: environment variables must be expressed as: <name>=<value>, got '%s'" % value)
        self.userEnv[bits[0]] = bits[1]

        return bits[0],bits[1]

    def usageExitTooFewArguments(self):
        return self.usageExit('Too few arguments')

    def usageExitTooManyArguments(self):
        return self.usageExit('Too many arguments')

    def usageExitWrongNumberOfArguments(self):
        return self.usageExit('Wrong number of arguments')

    def usageExitNoArgumentsRequired(self):
        return self.usageExit('No arguments required')

    def usageExit(self, msg=None):
        if msg: 
            print msg, '\n'
        self.parser.print_help()
        print ''
        if msg: 
            print msg
        print 'got: ' + ' '.join(sys.argv)
        self._exit(2)

    def getVersion(self):
        print __version__.getPrettyVersion()

    def log(self, message):
        util.printDetail(message, self.verboseLevel)
