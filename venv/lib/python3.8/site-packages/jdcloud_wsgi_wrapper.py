import os
import sys
import six
if six.PY2:
    import StringIO
if six.PY3:
    import io
from headers import Headers
from constants import StringType
from file_wrapper import FileWrapper


def wsgi_run(event, context, application):
    my_wsgi = WsgiWrapper(event, context)
    ret = my_wsgi.run(application)
    return ret


class WsgiWrapper:

    error_status = '500 NOK'
    error_headers = [('Content-Type', 'text/plain')]
    error_body = "A server error occurred.  Please check input."

    def __init__(self, event, context):
        self.context = context
        self.event = event
        self.env = dict(os.environ.items())
        self.status = None
        self.headers = None
        self.content_length_flag = True
        self.result = None
        if six.PY2:
            self.body = StringIO.StringIO()
        if six.PY3:
            self.body = io.StringIO()
        self.bytes_sent = 0
        self.headers_sent = False
        self.ret_content = {
                        'statusCode': 200,
                        'headers': {},
                        'body': '',
                    }

    def gen_env(self):
        env = self.env
        env['function.event'] = self.event
        env['function.context'] = self.context

        request = self.event['detail']
        env['REQUEST_METHOD'] = request.get('httpMethod', 'GET')
        env['SCRIPT_NAME'] = ''
        env['SERVER_NAME'] = ''
        env['SERVER_PORT'] = ''
        env['SERVER_PROTOCOL'] = ''
        env['PATH_INFO'] = request.get('path', '/')

        path_params = request.get('pathParameters')
        if six.PY2:
            if path_params is None:
                for k, v in path_params.items():
                    k = k.replace('-', '_').upper()
                    v = v.strip()
                    if k in env:
                        continue  # skip content length, type,etc.
                    if 'HTTP_' + k in env:
                        env['HTTP_' + k] += ',' + v  # comma-separate multiple headers
                    else:
                        env['HTTP_' + k] = v
        if six.PY3:
            if path_params != None:
                for k, v in path_params.items():
                    k = k.replace('-', '_').upper()
                    v = v.strip()
                    if k in env:
                        continue  # skip content length, type,etc.
                    if 'HTTP_' + k in env:
                        env['HTTP_' + k] += ',' + v  # comma-separate multiple headers
                    else:
                        env['HTTP_' + k] = v

        query_string = request.get('queryString', '')
        if query_string == '':
            query_params = request.get('queryParameters')
            if six.PY2:
                if query_params is None:
                    for k, v in query_params.items():
                        k = k.strip()
                        v = v.strip()
                        if query_string != '':
                            query_string = query_string + '&'
                        query_string = query_string + k + '=' + v
            if six.PY3:
                if query_params != None:
                    for k, v in query_params.items():
                        k = k.strip()
                        v = v.strip()
                        if query_string != '':
                            query_string = query_string + '&'
                        query_string = query_string + k + '=' + v
        env['QUERY_STRING'] = query_string

        headers = request.get('headers')
        content_type = headers.get('content-type', '')
        if content_type == '':
            content_type = headers.get('Content-type', '')
        if content_type == '':
            content_type = headers.get('Content-Type', '')
        if content_type == '':
            content_type = 'Content-type: text/plain'
        env['CONTENT_TYPE'] = content_type

        if six.PY2:
            length = headers.get('content-length', '')
            if length == '':
                length = headers.get('Content-length', '')
            if length == '':
                length = headers.get('Content-Length', '')
            if length != '':
                env['CONTENT_LENGTH'] = length
            else:
                env['CONTENT_LENGTH'] = '0'
        if six.PY3:
            length = headers.get('content-length', None)
            if length == None:
                length = headers.get('Content-length', None)
            if length == None:
                length = headers.get('Content-Length', None)
            if length:
                env['CONTENT_LENGTH'] = length
            else:
                env['CONTENT_LENGTH'] = '0'

        for k, v in headers.items():
            k = k.replace('-', '_').upper()
            v = v.strip()
            if k in env:
                continue  # skip content length, type,etc.
            if 'HTTP_' + k in env:
                env['HTTP_' + k] += ',' + v  # comma-separate multiple headers
            else:
                env['HTTP_' + k] = v

        input_body = request.get('body')
        if six.PY2:
            buf = StringIO.StringIO(input_body)
        if six.PY3:
            buf = io.StringIO(input_body)
        env['wsgi.input'] = buf
        env['wsgi.version'] = (1, 0)
        env['wsgi.url_scheme'] = self.get_scheme()
        env['wsgi.errors'] = sys.stderr
        env['wsgi.multithread'] = True
        env['wsgi.multiprocess'] = True
        env['wsgi.run_once'] = False
        env['wsgi.file_wrapper'] = FileWrapper

    def get_scheme(self):
        """Return a guess for whether 'wsgi.url_scheme' should be 'http' or 'https'
        """
        if self.env.get("HTTPS") in ('yes', 'on', '1'):
            return 'https'
        else:
            return 'http'

    def start_response(self, status, headers, exc_info=None):
        """'start_response()' callable as specified by PEP 333"""

        if exc_info:
            try:
                if self.headers_sent:
                    # Re-raise original exception if headers sent
                    raise exc_info[0](exc_info[1]).with_traceback(exc_info[2])
            finally:
                exc_info = None        # avoid dangling circular ref
        elif self.headers is not None:
            raise AssertionError("Headers already set!")

        assert type(status) is str, "Status must be a string"
        assert len(status) >= 4, "Status must be at least 4 characters"
        assert int(status[:3]), "Status message must begin w/3-digit code"
        assert status[3] == " ", "Status message must have a space after code"

        self.status = int(status[:3])
        self.headers = Headers(headers)

        return self.write

    def write(self, data):
        """'write()' callable as specified by PEP 333"""

        assert type(data) is StringType, "write() argument must be string"

        if not self.status:
            raise AssertionError("write() before start_response()")

        elif not self.headers_sent:
            # Before the first output, send the stored headers
            self.bytes_sent = len(data)  # make sure we know content-length
            self.send_headers()
        else:
            self.bytes_sent += len(data)
            if self.content_length_flag == False:
                self.ret_content['headers']['Content-Length'] = str(self.bytes_sent)

        # XXX check Content-Length and truncate if too many bytes written?
        self.body.write(data)
        self.body.flush()

    def send_headers(self):
        """Transmit headers to the client, via self._write()"""
        if 'Content-Length' not in self.headers:
            self.headers['Content-Length'] = str(self.bytes_sent)
            self.content_length_flag = False
        self.headers_sent = True
        self.ret_content['statusCode'] = self.status
        for item in self.headers.items():
            for k, v in self.headers.items():
                k = k.strip()
                v = v.strip()
                self.ret_content['headers'][k] = v

    def finish_response(self):
        for data in self.result:
            if six.PY2:
                str_data = str(data)
                self.write(str_data)
            if six.PY3:
                if isinstance(data, str):
                    str_data = data
                elif isinstance(data, bytes):
                    str_data = data.decode()
                else:
                    str_data = str(data)
                self.write(str_data)
        self.finish_content()

    def finish_content(self):
        """Ensure headers and content have both been sent"""
        if not self.headers_sent:
            # Only zero Content-Length if not set by the application (so
            # that HEAD requests can be satisfied properly, see #3839)
            self.headers.setdefault('Content-Length', "0")
            self.send_headers()
        else:
            pass  # XXX check if content-length was too short?

    def handle_error(self):
        """Log current error, and send error output to client if possible"""
        if not self.headers_sent:
            self.result = self.error_output(self.env, self.start_response)
            self.finish_response()

    def error_output(self, environ, start_response):
        start_response(self.error_status, self.error_headers[:], sys.exc_info())
        return [self.error_body]

    def run(self, application):
        try:
            self.gen_env()
            self.result = application(self.env, self.start_response)
            self.finish_response()
        except Exception as e:
            print(str(e))
            self.handle_error()

        self.ret_content['body'] = self.body.getvalue()
        return self.ret_content


