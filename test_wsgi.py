def simple_app(environ, start_response):
    status = '200 OK'
    output = b'WSGI is working!'
    response_headers = [('Content-type', 'text/plain'), ('Content-Length', str(len(output)))]
    start_response(status, response_headers)
    return [output]

if __name__ == '__main__':
    from wfastcgi import run
    run(simple_app)