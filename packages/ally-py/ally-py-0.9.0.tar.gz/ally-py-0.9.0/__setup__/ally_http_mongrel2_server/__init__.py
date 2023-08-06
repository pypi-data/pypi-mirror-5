'''
Created on Jul 15, 2011

@package: ally http
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Contains setup and configuration files for the HTTP REST server.
'''

from .. import ally_api
from ally.container import ioc

# --------------------------------------------------------------------

NAME = 'ally HTTP mongrel2 server'
GROUP = ally_api.GROUP
VERSION = '1.0'
DESCRIPTION = 'Provides the HTTP mongrel2 server'

# --------------------------------------------------------------------
# The default configurations
