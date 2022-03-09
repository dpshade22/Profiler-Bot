from jdcloud_wsgi_wrapper import wsgi_run


def application(environ, start_response):
    print(environ['function.event'])
    print(environ['function.context'])

    status = "200 OK"
    path = environ["PATH_INFO"]
    print(path)
    length = int(environ["CONTENT_LENGTH"], 0)
    body = environ["wsgi.input"].read(length)
    print(body)
    response_headers = [('Content-type', 'text/plain')]

    start_response(status, response_headers)
    return ['Function : My Own Hello World!']


def handler(event, context):
    result = wsgi_run(event, context, application)
    return result

