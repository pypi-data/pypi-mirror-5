This package provides a service based on JSONRPC with some small additions to the standard in order to enable authenticated requests.  The WSGI specification is used for data communication.  The package is broken down into two halves - a client and a server.  For security, the server is best run over HTTPS, although this is not enforced.

This package depends on WebOb 1.2 (or above).  This is automatically installed if you have an internet connection and use pip, otherwise download and install from http://pypi.python.org/pypi/WebOb

Example Usage (Server):

::

    import hashlib
    from wsgiref import simple_server
    from AuthRPC.server import AuthRPCApp

    def myauth(username, password, useragent):
        return username  == 'myuser' and \
               password  == hashlib.md5('secret'.encode()).hexdigest() and \
               useragent == 'myprogram'

    class api(object):
        def do_something(self, myvar):
            """Your code placed here"""
            return 'Something', myvar

    application = AuthRPCApp(api(), auth=myauth, filepath='/home/myapp/datadir')
    server = simple_server.make_server('localhost', 1234, application)
    server.serve_forever()

Example Usage (Client):

::

    from AuthRPC.client import ServerProxy, BatchCall

    client = ServerProxy('http://localhost:1234/',
                         username='myuser',
                         password='secret',
                         user_agent='myprogram')
    retval = client.do_something('test')

    # get a file and save local copy
    file_contents_generator = client.__getfile__('myfile.pdf')
    with open('myfile_downloaded.pdf', 'wb') as f:
        for data in file_contents_generator:
            f.write(data)

    batch = BatchCall(client)
    batch.do_something('call 1')
    batch.do_something('call 2')
    batch()

