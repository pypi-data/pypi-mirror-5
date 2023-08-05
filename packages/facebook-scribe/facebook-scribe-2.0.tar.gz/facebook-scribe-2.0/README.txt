Scribe client
=============

This is a Python client for scribe that can be installed using pip::

    pip install facebook-scribe


Usage
-----

Connect to ``HOST:9999`` using *Thrift*::

    from scribe import scribe
    from thrift.transport import TTransport, TSocket
    from thrift.protocol import TBinaryProtocol

    socket = TSocket.TSocket(host="HOST", port=9999)
    transport = TTransport.TFramedTransport(socket)
    protocol = TBinaryProtocol.TBinaryProtocol(trans=transport, strictRead=False, strictWrite=False)
    client = scribe.Client(protocol)
    transport.open()

    category = 'LOGS'
    message = 'hello world'

    log_entry = scribe.LogEntry(category, message)
    result = client.Log(messages=[log_entry])
    if result == 0:
      print 'success'


Links
-----

* `Facebook Scribe on GitHub <https://github.com/facebook/scribe>`_

