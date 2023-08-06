import logging
import os
import sys
import time
import ujson as json
import string

from brubeck.connections import (
    load_zmq,
    load_zmq_ctx,
    Mongrel2Connection,
    Connection,
)
from brubeck.request import Request, to_bytes, to_unicode
from brubeck.request_handling import (
    MessageHandler,
    http_response,
    coro_spawn,
    CORO_LIBRARY,
)
from dictshield.document import Document
from dictshield.fields import (
    StringField,
    BooleanField,
    URLField,
    EmailField,
    LongField,
    DictField,
    IntField,
)
from uuid import uuid4
from resource import (
    assure_resource,
    is_resource_registered,
    register_resource,
    unregister_resource,
    get_resource,
    create_resource_key,
)
from brubeck.connections import (load_zmq, load_zmq_ctx)

#########################################################
### Attempt to setup gevent wrappers for sleep and events
### Always prefere gevent if installed, then try eventlet
#########################################################
if CORO_LIBRARY == 'gevent':
    from gevent import monkey
    monkey.patch_all()

    from gevent.event import AsyncResult
    from gevent import sleep
    
    def coro_sleep(secs):
        sleep(secs)

    def coro_get_event():
        return AsyncResult()

    def coro_send_event(e, value):
        e.set(value)

    CORO_LIBRARY = 'gevent'

elif CORO_LIBRARY == 'eventlet':
    from eventlet import event
    from eventlet import sleep

    def coro_sleep(secs):
        sleep(secs)

    def coro_get_event():
        return Event()

    def coro_send_event(e, value):
        e.send(value)

    CORO_LIBRARY = 'eventlet'

# supported methods for a service (MAYBE, NOT ALL IMPLEMENTED)
_SERVICE_METHODS = ['get', 'post', 'put', 'delete', 
                   'options', 'connect', 'response', 'request']
_DEFAULT_SERVICE_REQUEST_METHOD = 'request'
_DEFAULT_SERVICE_RESPONSE_METHOD = 'response'
_SERVICE_RESOURCE_TYPE = 'SERVICE'
            
#################################
## Request and Response stuff 
#################################


#########################################################
## Some functions for creating/parsing tnetstrings fields
#########################################################
def t(text):
    """create a tnetstring field given the text"""
    return "%d:%s" % (len(str(text)), str(text))

def t_parse(field_text):
    """ parse a tnetstring field, and return any remainder
        field_value - a value in n:data format where n is the data length
            and data is the text to get the first n chars from
        returns the a tuple containing the value and whatever remains
    """
    logging.debug("t_parse: %s" % field_text)
    field_data = field_text.split(':', 1)
    expected_len = int(field_data[0])
    logging.debug("expected_len: %s" % expected_len)
    if expected_len > 0:
        field_value = field_data[1]
        value = field_value[0:expected_len]
    else:
        value = ''
    rest = field_value[expected_len:] if len(field_value) > expected_len else ''
    return (value, rest)


def parse_service_request(msg, passphrase):
    """Function for constructing a Request instance out of a
    message read straight off a zmq socket from a ServiceClientConnection.
    """
    logging.debug("parse_service_request: %s" % msg)
    fields = (sender, conn_id, request_timestamp, msg_passphrase, 
    origin_sender_id, origin_conn_id, origin_out_addr, 
    path, method, rest) = msg.strip().split(' ', 9)
    # first field is not tnetstring, no need to do anything
    # last is group of tnetstrings, will handle after
    i=1
    for field in fields[1:-1]:
        fields[i] = t_parse(field)[0]
        i+=1
    # our minimal "security" 
    if fields[3] != passphrase:
        raise Exception('Unknown service identity! (%s != %s)' % (str(fields[3]),str(passphrase)))
    # handle the "body" of the message or last parsed field
    arguments, rest = t_parse(rest)
    headers, rest = t_parse(rest)
    body = t_parse(rest)[0]
    arguments = json.loads(arguments) if len(arguments) > 0 else {}
    headers = json.loads(headers) if len(headers) > 0 else {}
    body = json.loads(body) if len(body) > 0 else {}
    # create our sevice request object
    r = ServiceRequest(**{
            "sender": fields[0],
            "conn_id": fields[1],
            "request_timestamp": fields[2],
            "origin_sender_id": fields[4],
            "origin_conn_id": fields[5],
            "origin_out_addr": fields[6],
            "path": fields[7],
            "method": fields[8],
            "arguments": arguments,
            "headers": headers,
            "body": body,
    })
    return r


def create_service_response(service_request, handler, method=_DEFAULT_SERVICE_REQUEST_METHOD, arguments={}, msg={}, headers={}):
    """Function for creating a ServiceResponse object to send."""
    if not isinstance(headers, dict):
        headers = json.loads(headers)
    if not isinstance(msg, dict):
        msg = json.loads(msg)

    service_response = ServiceResponse(**{
        "sender": service_request.sender,
        "conn_id": service_request.conn_id,
        "origin_sender_id": service_request.origin_sender_id,
        "origin_conn_id": service_request.origin_conn_id,
        "origin_out_addr": service_request.origin_out_addr,
        "path": service_request.path,
        "method": method,
        "arguments": arguments,
        "headers": headers,
        "body": msg,
        "status_code": handler.status_code,
        "status_msg": handler.status_msg,
    })

    return service_response


def parse_service_response(msg, passphrase):
    """Function for constructing a Reponse instance out of a
    message read straight off a zmq socket from a ServiceConnection.
    """
    logging.debug("parse_service_response: %s" % msg)

    fields = (sender, conn_id, request_timestamp, start_timestamp, end_timestamp, 
    msg_passphrase, origin_sender_id, origin_conn_id, origin_out_addr, 
    path, method, rest) = msg.split(' ', 11)
    # first field is not tnetstring, no need to do anything
    # last is group of tnetstrings, will handle after
    i=1
    for field in fields[1:-1]:
        fields[i] = t_parse(field)[0]
        i+=1   
    # our minimal "security"    
    if fields[5] != passphrase:
        raise Exception('Unknown service identity! (%s != %s)' % (str(fields[5]),str(passphrase)))
    # deal with the "body" or rest that is group of tnetstrings
    (status_code, rest) = t_parse(rest)
    (status_msg, rest) = t_parse(rest)
    (arguments, rest) = t_parse(rest)
    (headers, rest) = t_parse(rest)
    (body, rest) = t_parse(rest)
    logging.debug("arguments: %s" % arguments)
    logging.debug("headers: %s" % headers)
    logging.debug("body: %s" % body)
    arguments = json.loads(arguments) if len(arguments) > 0 else {}
    headers = json.loads(headers) if len(headers) > 0 else {}
    if body[0] == "{":
        body = json.loads(body) if len(body) > 0 else {}
    else:
        body = {
            "RETURN_DATA": body,
        }
    # create our service response
    service_response = ServiceResponse(**{
        "sender": fields[0], 
        "conn_id": fields[1], 
        "request_timestamp": fields[2],
        "start_timestamp": fields[3],
        "end_timestamp": fields[4],
        "origin_sender_id": fields[6], 
        "origin_conn_id": fields[7], 
        "origin_out_addr": fields[8], 
        "path": fields[9], 
        "method": fields[10], 
        "status_code": int(status_code), 
        "status_msg": status_msg,
        "arguments": arguments, 
        "headers": headers, 
        "body": body, 
    })
    return service_response


class ServiceRequest(Document):
    """Class used to construct a Brubeck service request message.
    Both the client and the server use this.
    """
    # set by the send call in the client connection
    sender = StringField(required=True)
    # set by the send call in the client connection
    conn_id = StringField(required=True)
    # set by send call in client connection
    # used to return the message to the originator
    origin_sender_id = StringField(required=True)
    # This is the connection id used by the originator and is needed for Mongrel2
    origin_conn_id  = StringField(required=True)
    # This is the socket address for the reply to the client
    origin_out_addr  = StringField(required=True)
    # used to route the request
    path = StringField(required=True)
    # used to route the request to the proper method of the handler
    method = StringField(required=True)
    # a dict, used to populat an arguments dict for use within the method
    arguments = DictField(required=False)
    # a dict, these get passed to the method called (use body for complex or large objects)
    headers = DictField(required=False)
    # a dict, this can be whatever you need it to be to get the job done.
    body = DictField(required=True)

    def __init__(self, *args, **kwargs):
        self.request_timestamp = int(time.time() * 1000)
        super(ServiceRequest, self).__init__(*args, **kwargs)

    def get_argument(self, key, default=None):
        """get's an argument by name"""
        if key in self.arguments:
            return self.arguments[key]
        return default


class ServiceResponse(ServiceRequest):
    """Class used to construct a Brubeck service response message.
    """
    status_code = IntField(required=True)
    status_message = StringField()
    def __init__(self, *args, **kwargs):
        self.start_timestamp = int(time.time() * 1000)
        self.end_timestamp = 0
        super(ServiceResponse, self).__init__(*args, **kwargs)

################################################################################
## Brubeck service connections 
## (service, client and mongrel2 with greenlet handlers)
################################################################################

class ServiceConnection(Mongrel2Connection):
    """Class is specific to handling communication with a ServiceClientConnection.
    """
    
    def __init__(self, svc_addr, svc_resp_addr, passphrase):
        """sender_id = uuid.uuid4() or anything unique
        pull_addr = pull socket used for incoming messages
        pub_addr = publish socket used for outgoing messages

        The class encapsulates socket type by referring to it's pull socket
        as in_sock and it's publish socket as out_sock.
        """
        zmq = load_zmq()
        ctx = load_zmq_ctx()

        self.sender_id = uuid4().hex
        self.in_addr = svc_addr
        self.out_addr = svc_resp_addr


        # the request (in_sock) is received from a DEALER socket (round robin)
        self.in_sock = ctx.socket(zmq.PULL)
        self.in_sock.connect(self.in_addr)
        print("Connected service requested PULL socket %s" % (self.in_addr))

        # the response is sent to original clients incoming DEALER socket
        self.out_sock = ctx.socket(zmq.ROUTER)
        self.out_sock.connect(self.out_addr)
        print("Connected service response ROUTER socket %s" % (self.out_addr))

        self.zmq = zmq
        self.passphrase = passphrase

    def process_message(self, application, message):
        """Function for coroutine that looks at the message, determines which handler will
        be used to process it, and then begins processing.
        The application is responsible for handling misconfigured routes.
        """
        
        # see if we have initialize _resource attribute on application
        assure_resource(application)

        service_request = parse_service_request(message, application.msg_conn.passphrase)

        handler = application.route_message(service_request)
        result = handler()

        msg = {}

        if result is not None and result is not "":
            msg = json.dumps(result)
        service_response = create_service_response(service_request, handler, method='response', arguments={}, msg=msg, headers={})
        
        application.msg_conn.send(service_response)

    def send(self, service_response):
        """uuid = unique ID that both the client and server need to match
           conn_id = connection id from this request needed to wake up handler on response
           origin_uuid = unique ID from the original request
           origin_conn_id = the connection id from the original request
           origin_out_addr = the socket address that expects the final result
           msg = the payload (a JSON object)
           path = the path used to route to the proper response handler
        """

        service_response.end_timestamp = int(time.time() * 1000)

        header = "%s %s %s %s %s %s %s %s %s %s %s" % ( service_response.sender,
            t(service_response.conn_id),
            t(service_response.request_timestamp),
            t(service_response.start_timestamp),
            t(service_response.end_timestamp),
            t(self.passphrase),
            t(service_response.origin_sender_id),
            t(service_response.origin_conn_id),
            t(service_response.origin_out_addr),
            t(service_response.path),
            t(service_response.method),
        )
        status_code = to_bytes(str(json.dumps(service_response.status_code)))
        status_msg = to_bytes(json.dumps(service_response.status_msg))
        arguments = to_bytes(json.dumps(service_response.arguments))
        headers = to_bytes(json.dumps(service_response.headers))
        body = to_bytes(json.dumps(service_response.body))
        msg = '%s %s%s%s%s%s' % (header,
            t(status_code),
            t(status_msg),
            t(arguments),
            t(headers),
            t(body),
        )
        
        logging.debug("ServiceConnection send (%s) : \"%s\"" % (service_response.sender, msg))

        self.out_sock.send(service_response.sender, self.zmq.SNDMORE)
        self.out_sock.send("", self.zmq.SNDMORE)
        self.out_sock.send(msg, self.zmq.NOBLOCK)
        return

    def recv(self):
        """Receives a message from a ServiceClientConnection.
        """
        # blocking recv call
        logging.debug("recv waiting...")
        zmq_msg = self.in_sock.recv()
        logging.debug("...recv got")
        # if we are multipart, keep getting our message until we are done
        while self.in_sock.getsockopt(self.zmq.RCVMORE):
            logging.debug("...recv getting more")
            zmq_msg += self.in_sock.recv()
        logging.debug("...recv got all")
        
        return zmq_msg


class ServiceClientConnection(ServiceConnection):
    """Class is specific to communicating with a ServiceConnection.
    """

    def __init__(self, svc_addr, svc_resp_addr, passphrase):
        """ passphrase = unique ID that both the client and server need to match
                for security purposed

            svc_addr = address of the Brubeck Service we are connecting to
            This socket is used for both inbound and outbound messages
        """

        self.passphrase = passphrase
        self.sender_id = uuid4().hex
        self.out_addr = svc_addr
        self.in_addr = svc_resp_addr
        
        zmq = load_zmq()
        ctx = load_zmq_ctx()

        self.out_sock = ctx.socket(zmq.PUSH)
        self.out_sock.bind(self.out_addr)
        logging.debug("Bound service request PUSH socket %s" % (self.out_addr))

        self.in_sock = ctx.socket(zmq.DEALER)
        self.in_sock.setsockopt(zmq.IDENTITY, self.sender_id)
        self.in_sock.bind(self.in_addr)
        logging.debug("Bound service response DEALER socket %s ID:%s" % (self.in_addr, self.sender_id))

        self.zmq = zmq

    def process_message(
        self,
        application,
        message,
        service_addr,
        service_passphrase,
        handle=True
    ):
        """This coroutine looks at the message, determines which handler will
        be used to process it, and then begins processing.
        Since this is a reply, not a request,
        we simply call the handler and are done
        returns a tuple containing 1) the response object created 
            from parsing the message and 2) the handlers return value
        """
        logging.debug("service_client_process_message service_passphrase: %s" % service_passphrase)
        service_response = parse_service_response(message, service_passphrase)
    
        logging.debug(
            "service_client_process_message service_response: %s" % service_response
        )
        
        logging.debug("service_client_process_message handle: %s" % handle)
        logging.debug("service_client_process_message service_response.path: %s" % service_response.path)
        if handle:
            handler = application.route_message(service_response)
            
            handler.set_status(service_response.status_code,  service_response.status_msg)
            result = handler()
            logging.debug(
                "service_client_process_message service_response: %s" % service_response)
            logging.debug("service_client_process_message result: %s" % result)
            return (service_response, result)
    
        return (service_response, None)

    def send(self, service_req):
        """Send will wait for a response with a listener and is async
        """
        service_req.conn_id = uuid4().hex

        header = "%s %s %s %s %s %s %s %s %s" % (self.sender_id, 
            t(service_req.conn_id), 
            t(service_req.request_timestamp),
            t(self.passphrase),
            t(service_req.origin_sender_id),
            t(service_req.origin_conn_id),
            t(service_req.origin_out_addr),
            t(service_req.path),
            t(service_req.method),
        )
        arguments = to_bytes(json.dumps(service_req.arguments))
        headers = to_bytes(json.dumps(service_req.headers))
        body = to_bytes(json.dumps(service_req.body))

        msg = ' %s %s%s%s' % (header, t(arguments),t(headers), t(body))
        logging.debug(
            "ServiceClientConnection send (%s:%s): %s" % (self.sender_id, service_req.conn_id, msg)
        )
        self.out_sock.send(msg)

        return service_req

    def close(self):
        """close our connections"""
        self.out_sock.close()
        self.in_sock.close()

##########################################
## Handler stuff
##########################################
class ServiceMessageHandler(MessageHandler):
    """Class is the simplest implementation of a message handlers. 
    Intended to be used for Service inter communication.
    """
    def __init__(self, application, message, *args, **kwargs):
        self.headers = {}
        super(ServiceMessageHandler, self).__init__(application, message, *args, **kwargs)
        
    def render(self, status_code=None, status_msg=None, headers = None, **kwargs):
        if status_code is not None:
            self.set_status(status_code, status_msg)

        if headers is not None:
            self.headers = headers

        body = self._payload
        
        logging.info('%s %s %s (%s:%s) for (%s:%s)' % (self.status_code, self.message.method,
                                        self.message.path,
                                        self.message.sender,
                                        self.message.conn_id,
                                        self.message.origin_out_addr,
                                        self.message.origin_conn_id,
                                        ))

        return body

    def __call__(self):
        """This is similar to the base call in MessageHandler without the 
        assumption we are an HTTP request.

        It requires a method attribute to indicate which function on the
        handler should be called. If that function is not supported, call the
        handlers unsupported function.

        In the event that an error has already occurred, _finished will be
        set to true before this function call indicating we should render
        the handler and nothing else.

        In all cases, generating a response for the service request is attempted.
        """
        try:
            self.prepare()
            if not self._finished:
                mef = self.message.method.lower()  # M-E-T-H-O-D man!

                # Find function mapped to method on self
                if (mef in _SERVICE_METHODS):
                    fun = getattr(self, mef, self.unsupported)
                else:
                    fun = self.unsupported

                # Call the function we settled on
                try:
                    if not hasattr(self, '_url_args') or self._url_args is None:
                        self._url_args = []

                    if isinstance(self._url_args, dict):
                        ### if the value was optional and not included, filter it
                        ### out so the functions default takes priority
                        kwargs = dict((k, v)
                                      for k, v in self._url_args.items() if v)
                        rendered = fun(**kwargs)
                    else:
                        rendered = fun(*self._url_args)

                    if rendered is None:
                        logging.debug('Handler had no return value: %s' % fun)
                        return ''
                except Exception, e:
                    logging.error(e, exc_info=True)
                    rendered = self.error(e)

                self._finished = True
                return rendered
            else:
                return self.render()
        finally:
            self.on_finish()

def service_response_listener(application, service_addr,  service_resp_addr, service_conn, service_passphrase, handle=True):
    """Function runs in a coroutine, one listener for each server per handler.
    Once running, it stays running until the brubeck instance is killed."""
    ##try:
    logging.debug("service_response_listener: service_passphrase 1: %s" % service_passphrase);
    while True:
        logging.debug("service_response_listener: service_passphrase 2: %s" % service_passphrase);
        logging.debug("service_response_listener waiting");
        raw_response = service_conn.recv()
        logging.debug("service_response_listener: service_passphrase 3: %s" % service_passphrase);
        logging.debug("service_response_listener recv(): %s" % raw_response);
        # just send raw message to connection client
        sender, conn_id = raw_response.split(' ', 1)
        logging.debug("service_response_listener: service_passphrase 4: %s" % service_passphrase);        
        conn_id = t_parse(conn_id)[0]
        logging.debug("service_response_listener: service_passphrase 5: %s" % service_passphrase);        
        if (
            not _notify_waiting_service_client(application, service_addr, conn_id, raw_response)
            and handle
        ):
            # Call our handler
            logging.debug("service_response_listener: calling process_message service_passphrase 6: %s" % service_passphrase);
            (response, handler_response) = service_conn.process_message(
                application,
                raw_response,
                service_addr,
                service_passphrase,
                handle
            )
    
class ServiceClientMixin(object):
    """Class adds the functionality to any handler to send messages to a ServiceConnection
    This must be used with a handler or something that has the following attributes:
        self.application
    """

    ################################
    ## The public interface methods
    ## This is all your handlers should use
    ################################

    def register_service(self, service_addr, service_resp_addr, service_passphrase, handle=True):
        """Public wrapper around _register_service"""
        return _register_service(self.application, service_addr, service_resp_addr, service_passphrase, handle)
        
    def unregister_service(self, service_addr, service_passphrase):
        """Public wrapper around _unregister_service"""
        return _unregister_service(self.application, service_addr, service_passphrase)
        
    def create_service_request(self, path, method=_DEFAULT_SERVICE_REQUEST_METHOD, arguments={}, msg={}, headers={}):
        """ path - string, used to route to proper handler
            method - used to map to the proper method of the handler
            arguments - dict, used within the method call if needed
            These are not used anymore, but I feel they belong. 

            If not to only hold the original request
                headers - dict, contains the accepted method to call on handler
                msg - dict, the body of the message to process
        """
        if not isinstance(headers, dict):
            headers = json.loads(headers)
        if not isinstance(msg, dict):
            msg = json.loads(msg)

        data = {
            # Not sure if this is the socket_id, but it is used to return the message to the originator
            "origin_sender_id": self.message.sender,
            # This is the connection id used by the originator and is needed for Mongrel2
            "origin_conn_id": self.message.conn_id,
            # This is the socket address for the reply to the client
            "origin_out_addr": self.application.msg_conn.out_addr,
            # used to route the request
            "path": path,
            "method": method,
            "arguments": arguments,
            # a dict, right now only METHOD is required and must be one of: ['get', 'post', 'put', 'delete','options', 'connect', 'response', 'request']
            "headers": headers,
            # a dict, this can be whatever you need it to be to get the job done.
            "body": msg,
        }
        return ServiceRequest(**data)
    
    def send_service_request(self, service_addr, service_req, handle=True):
        """do some work and wait for the results of the response to handler_response the response from the service
        blocking, waits for handled result.
        """
        service_req = _send_service_request(self.application, service_addr, service_req)
        conn_id = service_req.conn_id
        raw_response = _wait(self.application, service_addr, conn_id)
        service_conn = _get_service_conn(self.application, service_addr)
        
        (response, handler_response) = service_conn.process_message( 
            self.application, raw_response, 
            service_addr, service_conn.passphrase, handle,
        )

        return (response, handler_response)

    def send_service_request_nowait(self, service_addr, service_req):
        """defer some work, but still handle the response yourself
        non-blocking, returns immediately.
        """
        _send_service_request(self.application, service_addr, service_req)
        return

    def forward_to_service(self, service_addr, service_req):
        """give up any responsability for the request, someone else will respond to the client
        non-blocking, returns immediately.
        """
        raise NotImplemented("forward_to_service is not yet implemented, use send_service_request_nowait instead")


#############################################
## Functions for sending the service request
#############################################
def _send_service_request(application, service_addr, service_req):
    """send our message, used internally only"""
    logging.debug("sending service request")
    service_conn = _get_service_conn(application, service_addr)
    return service_conn.send(service_req)


def _get_service_info(application, service_addr):
    if _service_is_registered(application, service_addr):
        key = create_resource_key(service_addr, _SERVICE_RESOURCE_TYPE)
        service_info = get_resource(key)
        return service_info
    else:
        raise Exception("%s service not registered" % service_addr)

def _get_service_conn(application, service_addr):
    """get the ServiceClientConnection for a service."""
    service_info = _get_service_info(application, service_addr)
    if service_info is None:
        return None
    else:     
        return service_info['service_conn']        


###################################################
## Functions for waiting and notifying of response
###################################################
def _wait(application, service_addr, conn_id):
    """wait fro the application to create an event from the service listener"""
    raw_response = None
    conn_id = str(conn_id)


    logging.debug("creating event for %s" % conn_id)

    e = coro_get_event()
    waiting_events = _get_waiting_service_clients(application, service_addr)
    waiting_events[conn_id] = (int(time.time()), e)

    logging.debug("event for %s waiting" % conn_id)
    raw_response = e.get()
    logging.debug("event for %s raised" % conn_id)
    logging.debug("raw_response %s" % raw_response)


    if raw_response is not None:
        #logging.debug("process_message %s,%s,%s,%s" % (self.application, raw_response, self, service_addr))
        return raw_response
    else:
        logging.debug("NO RESULTS")
        return None
                                            
def _get_waiting_service_clients(application, service_addr):
    """get the waiting service clients."""
    service_info = _get_service_info(application, service_addr)
    if service_info is None:
        return None
    else:     
        return service_info['waiting_clients']

def _notify_waiting_service_client(application, service_addr, conn_id, raw_results):
    """Notify waiting events if they exist."""
    #logging.debug("NOTIFY: %s: %s (%s)" % (service_addr, conn_id, raw_results))
    waiting_clients = _get_waiting_service_clients(application, service_addr)
    logging.debug("waiting_clients: %s" % (waiting_clients))
    conn_id = str(conn_id)
    if not waiting_clients is None and conn_id in waiting_clients:
        logging.debug("conn_id %s found to notify(%s)" % (conn_id,waiting_clients[conn_id]))
        coro_send_event(waiting_clients[conn_id][1], raw_results)
        #logging.debug("conn_id %s sent to: %s" % (conn_id, raw_results))
        coro_sleep(0)
        return True
    else:
        logging.debug("conn_id %s not found to notify." % conn_id)
        return False

############################################
## Service registration (Resource) helpers
############################################

def _service_is_registered(application, service_addr):
    """ Check if a service is registered"""
    key = create_resource_key(service_addr, _SERVICE_RESOURCE_TYPE)
    return is_resource_registered(key)

def _register_service(application, service_addr, service_resp_addr, service_passphrase, handle=True):
    """ Create and store a connection and it's listener and waiting_clients queue.
    """
    logging.debug("service_passphrase: %s" % service_passphrase)
    assure_resource(application)
    key = create_resource_key(service_addr, _SERVICE_RESOURCE_TYPE)        
    if not is_resource_registered(key):
        # create our service connection
        logging.debug("register_service creating service_conn: %s" % service_addr)
            
        service_conn = ServiceClientConnection(
                        service_addr,  service_resp_addr, service_passphrase
                    )

        # create and start our listener
        logging.debug("register_service starting listener: %s" % service_addr)
        coro_spawn(
            service_response_listener,
            application, 
            service_addr, 
            service_resp_addr, 
            service_conn, 
            service_passphrase,
            handle
        )
        # give above process a chance to start
        coro_sleep(0)
    
        # add us to the list
        resource = {'service_conn': service_conn, 'waiting_clients': {}}
        register_resource(resource, key)
        logging.debug("register_service success: %s" % key)
    else:
        logging.debug("register_service ignored: %s already registered" % service_addr)
    return True

def _unregister_service(application, service_addr,service_passphrase):
    """ unregister a service.
    """
    if not self._service_is_registered(service_addr):
        logging.debug("unregister_resource ignored: %s not registered" % service_addr)
        return False
    else:
        service_info = _get_service_info(application, service_addr)
        service_conn = service_info['service_conn']
        waiting_clients = service_info['waiting_clients']
        service_conn.close()
        for sock in waiting_clients:
            logging.debug("killing internal reply socket %s" % sock)
            sock.close()
                
        key = create_resource_key(service_addr, _SERVICE_RESOURCE_TYPE)    
        unregister_resource(key)
        logging.debug("unregister_service success: %s" % service_addr)
        return True

