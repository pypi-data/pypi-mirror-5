'''
Created on Nov 24, 2011

@package: ally core http
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the configurations for encoders and decoders.
'''

from ..ally_core.encoder_decoder import assemblyParsing, updateAssemblyParsing
from ally.container import ioc
from ally.core.http.impl.processor.parser.formdata import ParseFormDataHandler
from ally.core.http.impl.url_encoded import parseStr
from ally.core.impl.processor.parser.text import ParseTextHandler
from ally.design.processor.handler import Handler
import codecs

# --------------------------------------------------------------------

@ioc.config
def content_types_urlencoded() -> dict:
    '''The URLEncoded content type'''
    return {
            'application/x-www-form-urlencoded': None,
            }

# --------------------------------------------------------------------
# Creating the parsers

@ioc.entity
def parseURLEncoded() -> Handler:
    def parseURLEncoded(content, charSet): return parseStr(codecs.getreader(charSet)(content).read())
    
    b = ParseTextHandler(); yield b
    b.contentTypes = set(content_types_urlencoded())
    b.parser = parseURLEncoded
    b.parserName = 'urlencoded'

@ioc.entity
def parseFormData() -> Handler:
    b = ParseFormDataHandler(); yield b
    b.contentTypeUrlEncoded = next(iter(content_types_urlencoded()))

# --------------------------------------------------------------------

@ioc.before(updateAssemblyParsing)
def updateAssemblyParsingFormData():
    assemblyParsing().add(parseFormData())
    assemblyParsing().add(parseURLEncoded())
