'''
Created on Nov 7, 2012

@package: ally base
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the logging configurations to be used for the application.
'''

from ally.container import ioc
import __deploy__
import __setup__
import ally

# --------------------------------------------------------------------

@ioc.config
def format():
    '''
    The format to use for the logging messages more details can be found at "http://docs.python.org/3/library/logging.html"
    in chapter "16.7.6. LogRecord attributes. Example:
        "%(asctime)s %(levelname)s (%(threadName)s %(module)s.%(funcName)s %(lineno)d): %(message)s"
        "%(levelname)-8s %(message)s\n  File "%(pathname)s", line %(lineno)d, in %(funcName)s"
        "%(module)s.%(funcName)s %(lineno)d: %(message)s"
        "%(levelname)-8s %(message)-100s %(name)s"
    '''
    return '%(levelname)-8s %(message)-100s %(name)s'

@ioc.config
def debug_for():
    '''
    The list of packages or module patterns to provide debugging for, attention this is available only if the application 
    is not run with -O or -OO option
    '''
    return []

@ioc.config
def info_for():
    '''The list of packages or module patterns to provide info for'''
    return [__deploy__.__name__, __setup__.__name__]

@ioc.config
def warning_for():
    '''The list of packages or module patterns to provide warnings for'''
    return [ally.__name__]

@ioc.config
def log_file():
    ''' The name of the log file '''
    return 'app.log'
