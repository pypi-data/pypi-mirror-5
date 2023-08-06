'''
Created on Jul 15, 2011

@package: ally http
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Contains setup and configuration files for the HTTP REST server.
'''

from ally.container import ioc

# --------------------------------------------------------------------

NAME = 'ally HTTP'
GROUP = 'ally'
VERSION = '1.0'
DESCRIPTION = 'Provides the HTTP communication support'

# --------------------------------------------------------------------

SERVER_BASIC = 'basic'
# The basic server name

# --------------------------------------------------------------------
# The default configurations

@ioc.config
def server_type() -> str:
    '''
    The type of the server to use, the options are:
    "basic"- single threaded server, the safest but slowest server to use.
    '''
    return SERVER_BASIC

@ioc.config
def server_host() -> str:
    '''The IP address to bind the server to, something like 127.0.0.1'''
    return '0.0.0.0'

@ioc.config
def server_port() -> int:
    '''The port on which the server will run'''
    return 8080

@ioc.config
def server_version() -> str:
    '''The server version name'''
    return 'Ally/0.1'
