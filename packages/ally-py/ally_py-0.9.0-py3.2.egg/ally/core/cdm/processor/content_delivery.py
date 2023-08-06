'''
Created on Jul 14, 2011

@package: service CDM
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Mugur Rus

Provides the content delivery handler.
'''

from ally.container.ioc import injected
from ally.design.processor.attribute import requires, defines
from ally.design.processor.context import Context
from ally.design.processor.handler import HandlerProcessorProceed
from ally.http.spec.codes import METHOD_NOT_AVAILABLE, PATH_NOT_FOUND, \
    PATH_FOUND
from ally.http.spec.server import HTTP_GET
from ally.support.util_io import IInputStream
from ally.zip.util_zip import normOSPath, normZipPath
from mimetypes import guess_type
from os.path import isdir, isfile, join, dirname, normpath, sep
from urllib.parse import unquote
from zipfile import ZipFile
import json
import logging
import os

# --------------------------------------------------------------------

log = logging.getLogger(__name__)

# --------------------------------------------------------------------

class Request(Context):
    '''
    The request context.
    '''
    # ---------------------------------------------------------------- Required
    scheme = requires(str)
    uri = requires(str)
    method = requires(str)

class Response(Context):
    '''
    The response context.
    '''
    # ---------------------------------------------------------------- Defined
    code = defines(str)
    status = defines(int)
    isSuccess = defines(bool)
    allows = defines(list, doc='''
    @rtype: list[string]
    Contains the allow list for the methods.
    ''')

class ResponseContent(Context):
    '''
    The response context.
    '''
    # ---------------------------------------------------------------- Defined
    source = defines(IInputStream, doc='''
    @rtype: IInputStream
    The stream that provides the response content in bytes.
    ''')
    length = defines(int, doc='''
    @rtype: integer
    Contains the length for the content.
    ''')
    type = defines(str, doc='''
    @rtype: string
    The type for the streamed content.
    ''')

# --------------------------------------------------------------------

@injected
class ContentDeliveryHandler(HandlerProcessorProceed):
    '''
    Implementation for a processor that delivers the content based on the URL.
    '''

    repositoryPath = str
    # The directory where the file repository is
    defaultContentType = 'application/octet-stream'
    # The default mime type to set on the content response if None could be guessed
    _linkExt = '.link'
    # Extension to mark the link files in the repository.
    _zipHeader = 'ZIP'
    # Marker used in the link file to indicate that a link is inside a zip file.
    _fsHeader = 'FS'
    # Marker used in the link file to indicate that a link is file system

    def __init__(self):
        assert isinstance(self.repositoryPath, str), 'Invalid repository path value %s' % self.repositoryPath
        assert isinstance(self.defaultContentType, str), 'Invalid default content type %s' % self.defaultContentType
        self.repositoryPath = normpath(self.repositoryPath)
        if not os.path.exists(self.repositoryPath): os.makedirs(self.repositoryPath)
        assert isdir(self.repositoryPath) and os.access(self.repositoryPath, os.R_OK), \
            'Unable to access the repository directory %s' % self.repositoryPath
        super().__init__()

        self._linkTypes = {self._fsHeader:self._processLink, self._zipHeader:self._processZiplink}

    def process(self, request:Request, response:Response, responseCnt:ResponseContent, **keyargs):
        '''
        @see: HandlerProcessorProceed.process
        
        Provide the file content as a response.
        '''
        assert isinstance(request, Request), 'Invalid request %s' % request
        assert isinstance(response, Response), 'Invalid response %s' % response
        assert isinstance(responseCnt, ResponseContent), 'Invalid response content %s' % responseCnt

        if request.method != HTTP_GET:
            if response.allows is not None: response.allows.append(HTTP_GET)
            else: response.allows = [HTTP_GET]
            response.code, response.status, response.isSuccess = METHOD_NOT_AVAILABLE
        else:
            # Make sure the given path points inside the repository
            entryPath = normOSPath(join(self.repositoryPath, normZipPath(unquote(request.uri))))
            if not entryPath.startswith(self.repositoryPath):
                response.code, response.status, response.isSuccess = PATH_NOT_FOUND
            else:
                # Initialize the read file handler with None value
                # This will be set upon successful file open
                rf = None
                if isfile(entryPath):
                    rf, size = open(entryPath, 'rb'), os.path.getsize(entryPath)
                else:
                    linkPath = entryPath
                    while len(linkPath) > len(self.repositoryPath):
                        if isfile(linkPath + self._linkExt):
                            with open(linkPath + self._linkExt) as f: links = json.load(f)
                            subPath = normOSPath(entryPath[len(linkPath):]).lstrip(sep)
                            for linkType, *data in links:
                                if linkType in self._linkTypes:
                                    # make sure the subpath is normalized and uses the OS separator
                                    if not self._isPathDeleted(join(linkPath, subPath)):
                                        entry = self._linkTypes[linkType](subPath, *data)
                                        if entry is not None:
                                            rf, size = entry
                                            break
                            break
                        subLinkPath = dirname(linkPath)
                        if subLinkPath == linkPath:
                            break
                        linkPath = subLinkPath
        
                if rf is None:
                    response.code, response.status, response.isSuccess = PATH_NOT_FOUND
                else:
                    response.code, response.status, response.isSuccess = PATH_FOUND
                    responseCnt.source = rf
                    responseCnt.length = size
                    responseCnt.type, _encoding = guess_type(entryPath)
                    if not responseCnt.type: responseCnt.type = self.defaultContentType
                    return

    # ----------------------------------------------------------------

    def _processLink(self, subPath, linkedFilePath):
        '''
        Reads a link description file and returns a file handler to
        the linked file.
        '''
        # make sure the file path uses the OS separator
        linkedFilePath = normOSPath(linkedFilePath)
        if isdir(linkedFilePath):
            resPath = join(linkedFilePath, subPath)
        elif not subPath:
            resPath = linkedFilePath
        else:
            return None
        if isfile(resPath):
            return open(resPath, 'rb'), os.path.getsize(resPath)

    def _processZiplink(self, subPath, zipFilePath, inFilePath):
        '''
        Reads a link description file and returns a file handler to
        the linked file inside the ZIP archive.
        '''
        # make sure the ZIP file path uses the OS separator
        zipFilePath = normOSPath(zipFilePath)
        # convert the internal ZIP path to OS format in order to use standard path functions
        inFilePath = normOSPath(inFilePath)
        zipFile = ZipFile(zipFilePath)
        # resource internal ZIP path should be in ZIP format
        resPath = normZipPath(join(inFilePath, subPath))
        if resPath in zipFile.NameToInfo:
            return zipFile.open(resPath, 'r'), zipFile.getinfo(resPath).file_size

    def _isPathDeleted(self, path):
        '''
        Returns true if the given path was deleted or was part of a directory
        that was deleted.
        '''
        path = normpath(path)
        while len(path) > len(self.repositoryPath):
            if isfile(path + '.deleted'): return True
            subPath = dirname(path)
            if subPath == path: break
            path = subPath
        return False
