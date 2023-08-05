##############################################################################
#
# Copyright (C) Zenoss, Inc. 2013, all rights reserved.
#
# This content is made available according to terms specified in the LICENSE
# file at the top-level directory of this package.
#
##############################################################################

import os
import re
import base64
import logging
import httplib
from datetime import datetime
from xml.etree import cElementTree as ET
from twisted.internet import reactor, defer
from twisted.internet.protocol import Protocol, ProcessProtocol
from twisted.web.client import Agent
from twisted.web.http_headers import Headers
from . import constants as c

KERBEROS_INSTALLED = False
try:
    import kerberos
    KERBEROS_INSTALLED = True
except ImportError:
    pass

log = logging.getLogger('zen.winrm')
_XML_WHITESPACE_PATTERN = re.compile(r'>\s+<')
_AGENT = None
_MAX_PERSISTENT_PER_HOST = 200
_CACHED_CONNECTION_TIMEOUT = 24000
_CONNECT_TIMEOUT = 500
_NANOSECONDS_PATTERN = re.compile(r'\.(\d{6})(\d{3})')
_REQUEST_TEMPLATE_NAMES = (
    'enumerate', 'pull',
    'create', 'command', 'send', 'receive', 'signal', 'delete',
    'subscribe', 'event_pull', 'unsubscribe')
_REQUEST_TEMPLATE_DIR = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), 'request')
_REQUEST_TEMPLATES = {}
_CONTENT_TYPE = {'Content-Type': ['application/soap+xml;charset=UTF-8']}
_MAX_KERBEROS_RETRIES = 3


def _get_agent():
    global _AGENT
    if _AGENT is None:
        try:
            # HTTPConnectionPool has been present since Twisted version 12.1
            from twisted.web.client import HTTPConnectionPool
            pool = HTTPConnectionPool(reactor, persistent=True)
            pool.maxPersistentPerHost = _MAX_PERSISTENT_PER_HOST
            pool.cachedConnectionTimeout = _CACHED_CONNECTION_TIMEOUT
            _AGENT = Agent(
                reactor, connectTimeout=_CONNECT_TIMEOUT, pool=pool)
        except ImportError:
            try:
                # connectTimeout first showed up in Twisted version 11.1
                _AGENT = Agent(reactor, connectTimeout=_CONNECT_TIMEOUT)
            except TypeError:
                _AGENT = Agent(reactor)
    return _AGENT


class _StringProducer(object):
    """
    The length attribute must be a non-negative integer or the constant
    twisted.web.iweb.UNKNOWN_LENGTH. If the length is known, it will be used to
    specify the value for the Content-Length header in the request. If the
    length is unknown the attribute should be set to UNKNOWN_LENGTH. Since more
    servers support Content-Length, if a length can be provided it should be.
    """

    def __init__(self, body):
        self._body = body
        self.length = len(body)

    def startProducing(self, consumer):
        """
        This method is used to associate a consumer with the producer. It
        should return a Deferred which fires when all data has been produced.
        """
        consumer.write(self._body)
        return defer.succeed(None)

    def pauseProducing(self):
        pass

    def stopProducing(self):
        pass


def _parse_error_message(xml_str):
    elem = ET.fromstring(xml_str)
    text = elem.findtext('.//{' + c.XML_NS_SOAP_1_2 + '}Text').strip()
    detail = elem.findtext('.//{' + c.XML_NS_SOAP_1_2 + '}Detail/*/*').strip()
    return "{0} {1}".format(text, detail)


class _ErrorReader(Protocol):

    def __init__(self):
        self.d = defer.Deferred()
        self._data = []

    def dataReceived(self, data):
        self._data.append(data)

    def connectionLost(self, reason):
        message = _parse_error_message(''.join(self._data))
        self.d.callback(message)


class RequestError(Exception):
    pass


class UnauthorizedError(RequestError):
    pass


def _get_request_template(name):
    if name not in _REQUEST_TEMPLATE_NAMES:
        raise Exception('Invalid request template name: {0}'.format(name))
    if name not in _REQUEST_TEMPLATES:
        path = os.path.join(_REQUEST_TEMPLATE_DIR, '{0}.xml'.format(name))
        with open(path) as f:
            _REQUEST_TEMPLATES[name] = \
                _XML_WHITESPACE_PATTERN.sub('><', f.read()).strip()
    return _REQUEST_TEMPLATES[name]


def _get_basic_auth_header(username, password):
    authstr = "{0}:{1}".format(username, password)
    return 'Basic {0}'.format(base64.encodestring(authstr).strip())


class KinitProcessProtocol(ProcessProtocol):

    def __init__(self, password):
        self._password = password
        self.d = defer.Deferred()

    def outReceived(self, data):
        log.debug("kinit wrote to stdout: {0}".format(data))
        if 'Password for' in data:
            self.transport.write('{0}\n'.format(self._password))

    def errReceived(self, data):
        log.debug("kinit wrote to stdin: {0}".format(data))

    def processEnded(self, reason):
        self.d.callback(None)


@defer.inlineCallbacks
def kinit(username, password):
    kinit = '/usr/bin/kinit'
    userid, realm = username.split('@')
    args = [kinit, '{0}@{1}'.format(userid, realm.upper())]
    log.debug('spawing kinit process: {0}'.format(args))
    protocol = KinitProcessProtocol(password)
    reactor.spawnProcess(protocol, kinit, args)
    yield protocol.d


class AuthGSSClient(object):
    """
    The Generic Security Services (GSS) API allows Kerberos implementations to
    be API compatible. Instances of this class operate on a context for GSSAPI
    client-side authentication with the given service principal.

    GSSAPI Function Result Codes:
        -1 : Error
        0  : GSSAPI step continuation (only returned by 'Step' function)
        1  : GSSAPI step complete, or function return OK
    """

    def __init__(self, service, username, password):
        """
        @param service: a string containing the service principal in the form
            'type@fqdn' (e.g. 'imap@mail.apple.com').
        """
        self._service = service
        self._username = username
        self._password = password
        result_code, self._context = kerberos.authGSSClientInit(service)
        if result_code != kerberos.AUTH_GSS_COMPLETE:
            raise Exception('kerberos authGSSClientInit failed')

    def __del__(self):
        result_code = kerberos.authGSSClientClean(self._context)
        if result_code != kerberos.AUTH_GSS_COMPLETE:
            raise Exception('kerberos authGSSClientClean failed')

    def _step(self, challenge=''):
        """
        Processes a single GSSAPI client-side step using the supplied server
        data.

        @param challenge: a string containing the base64-encoded server data
            (which may be empty for the first step).
        @return:          a result code
        """
        log.debug('GSSAPI step challenge="{0}"'.format(challenge))
        return kerberos.authGSSClientStep(self._context, challenge)

    @defer.inlineCallbacks
    def get_base64_client_data(self):
        """
        @return: a string containing the base64-encoded client data to be sent
            to the server.
        """
        result_code = None
        for i in xrange(_MAX_KERBEROS_RETRIES):
            try:
                result_code = self._step()
                break
            except kerberos.GSSError as e:
                log.debug('{0}. Calling kinit.'.format(e.args[1][0]))
                yield kinit(self._username, self._password)
        if result_code != kerberos.AUTH_GSS_CONTINUE:
            raise Exception('kerberos authGSSClientStep failed ({0}).'
                            .format(result_code))
        base64_client_data = kerberos.authGSSClientResponse(self._context)
        defer.returnValue(base64_client_data)

    def get_username(self, challenge):
        """
        Get the user name of the principal authenticated via the now complete
        GSSAPI client-side operations.

        @param challenge: a string containing the base64-encoded server data
        @return:          a string containing the user name.
        """
        result_code = self._step(challenge)
        if result_code != kerberos.AUTH_GSS_COMPLETE:
            raise Exception('kerberos authGSSClientStep failed ({0}). '
                            'challenge={1}'
                            .format(result_code, challenge))
        return kerberos.authGSSClientUserName(self._context)


@defer.inlineCallbacks
def _authenticate_with_kerberos(hostname, username, password, scheme, url):
    if not KERBEROS_INSTALLED:
        raise Exception('You must run "easy_install kerberos".')
    service = '{0}@{1}'.format(scheme.upper(), hostname)
    gss_client = AuthGSSClient(service, username, password)
    base64_client_data = yield gss_client.get_base64_client_data()
    auth = 'Kerberos {0}'.format(base64_client_data)
    k_headers = Headers(_CONTENT_TYPE)
    k_headers.addRawHeader('Authorization', auth)
    k_headers.addRawHeader('Content-Length', '0')
    response = yield _get_agent().request('POST', url, k_headers, None)
    if response.code == httplib.UNAUTHORIZED:
        raise UnauthorizedError(
            "HTTP Unauthorized received on initial kerberos request.")
    elif response.code != httplib.OK:
        proto = _StringProtocol()
        response.deliverBody(proto)
        xml_str = yield proto.d
        raise Exception(
            "status code {0} received on initial kerberos request {1}"
            .format(response.code, xml_str))
    auth_header = response.headers.getRawHeaders('WWW-Authenticate')[0]
    for field in auth_header.split(','):
        kind, details = field.strip().split(' ', 1)
        if kind.lower() == 'kerberos':
            auth_details = details.strip()
            break
    else:
        raise Exception(
            'negotiate not found in WWW-Authenticate header: {0}'
            .format(auth_header))
    k_username = gss_client.get_username(auth_details)
    log.debug('kerberos auth successful for user: {0} / {1} '
              .format(username, k_username))


@defer.inlineCallbacks
def _get_url_and_headers(hostname, auth_type, username, password,
                         scheme='http', port=5985):
    url = "{scheme}://{hostname}:{port}/wsman".format(
        scheme=scheme, hostname=hostname, port=port)
    headers = Headers(_CONTENT_TYPE)
    if auth_type == 'basic':
        headers.addRawHeader('Authorization',
                             _get_basic_auth_header(username, password))
    elif auth_type == 'kerberos':
        yield _authenticate_with_kerberos(
            hostname, username, password, scheme, url)
    else:
        raise Exception('unknown auth type: {0}'.format(auth_type))
    defer.returnValue((url, headers))


class RequestSender(object):

    def __init__(self, hostname, auth_type, username, password):
        self._hostname = hostname
        self._auth_type = auth_type
        self._username = username
        self._password = password
        self._url = None
        self._headers = None

    @defer.inlineCallbacks
    def _set_url_and_headers(self):
        self._url, self._headers = yield _get_url_and_headers(
            self._hostname, self._auth_type, self._username, self._password)

    @property
    def hostname(self):
        return self._hostname

    @defer.inlineCallbacks
    def send_request(self, request_template_name, **kwargs):
        log.debug('sending request: {0} {1}'.format(
            request_template_name, kwargs))
        if not self._url or self._auth_type == 'kerberos':
            yield self._set_url_and_headers()
        request = _get_request_template(request_template_name).format(**kwargs)
        # log.debug(request)
        body_producer = _StringProducer(request)
        response = yield _get_agent().request(
            'POST', self._url, self._headers, body_producer)
        log.debug('received response {0} {1}'.format(
            response.code, request_template_name))
        if response.code == httplib.UNAUTHORIZED:
            raise UnauthorizedError(
                "unauthorized, check username and password.")
        elif response.code != httplib.OK:
            reader = _ErrorReader()
            response.deliverBody(reader)
            message = yield reader.d
            raise RequestError("HTTP status: {0}. {1}".format(
                response.code, message))
        defer.returnValue(response)


class _StringProtocol(Protocol):

    def __init__(self):
        self.d = defer.Deferred()
        self._data = []

    def dataReceived(self, data):
        self._data.append(data)

    def connectionLost(self, reason):
        self.d.callback(''.join(self._data))


class EtreeRequestSender(object):
    """A request sender that returns an etree element"""

    def __init__(self, hostname, username, password, auth_type):
        self._sender = RequestSender(hostname, username, password, auth_type)

    @defer.inlineCallbacks
    def send_request(self, request_template_name, **kwargs):
        resp = yield self._sender.send_request(
            request_template_name, **kwargs)
        proto = _StringProtocol()
        resp.deliverBody(proto)
        xml_str = yield proto.d
        defer.returnValue(ET.fromstring(xml_str))


def get_datetime(text):
    """
    Parse the date from a WinRM response and return a datetime object.
    """
    if text.endswith('Z'):
        if '.' in text:
            format = "%Y-%m-%dT%H:%M:%S.%fZ"
            date_string = _NANOSECONDS_PATTERN.sub(r'.\g<1>', text)
        else:
            format = "%Y-%m-%dT%H:%M:%SZ"
            date_string = text
    else:
        format = '%m/%d/%Y %H:%M:%S.%f'
        date_string = text
    return datetime.strptime(date_string, format)
