You can run this sockjs server with::

    gserve test_sockjs_server.init

The test server is at http://localhost:8080/__test_sockjs__

To test it you must use the sockjs tests:

http://sockjs.github.io/sockjs-protocol/sockjs-protocol-0.3.3.html

I use this command to do the test:

SOCKJS_URL=http://localhost:8080/__test_sockjs__ ./venv/bin/python sockjs-protocol-0.3.3.py -v


Warning: I don't support WebsocketHixie76!
